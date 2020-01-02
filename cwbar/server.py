import glob
import os
import re

import cwbar.async_profiler
import cwbar.krupd
import cwbar.postgres
import cwbar.settings
import cwbar.source_project
import cwbar.wildfly


def _param_value_int(args, name, default_value):
    for arg in args:
        if arg.startswith(name + "="):
            return int(arg[len(name + "="):])
    return default_value


def _param_value_str(args, name, default_value):
    for arg in args:
        if arg.startswith(name + "="):
            return arg[len(name + "="):]
    return default_value


class Server:

    def __init__(self, server_type, server_name=None):
        self.server_type = server_type
        self.server_name = server_name if server_name else self.server_type

    def get_server_dir(self):
        return os.path.join(cwbar.settings.BASE_COMPILE, self.server_name)

    def get_wildfly_dir_name(self):
        return glob.glob(os.path.join(self.get_server_dir(), "jboss-*"))[0]

    def wf(self):
        wildfly_dir_name = self.get_wildfly_dir_name()
        return cwbar.wildfly.Wildfly(wildfly_dir_name)

    def get_db_set(self):
        wildfly = self.wf()
        result = set()
        for data_source in wildfly.get_config().get_data_sources():
            result.add(data_source.get_connection())
        return result

    def db(self):
        print(self.get_db_set())

    def set_db(self, new_name):
        wildfly = self.wf()
        cfg = wildfly.get_config()
        for data_source in cfg.get_data_sources():
            if "postgres" in data_source.get_driver():
                data_source.set_connection("jdbc:postgresql://" + new_name)
                m = re.match("(.*?):(.*?)/(.*)", new_name)
                if m:
                    user_pass = cwbar.postgres.lookup_user_pass(*m.groups())
                    if user_pass:
                        data_source.set_user(user_pass[0])
                        data_source.set_password(user_pass[1])
                cfg.save()
                print("Set url " + new_name + " for " + data_source.get_name())

    def kd(self):
        root_dir = self.get_server_dir()
        return cwbar.krupd.Krupd(root_dir)

    def sp(self):
        return cwbar.source_project.SourceProject.get_project(self.server_type)

    def log(self):
        self.wf().log()

    def log_tail(self):
        self.wf().log_tail()

    def config(self):
        self.wf().config()

    def start(self):
        self.kd().start()

    def stop(self):
        self.kd().stop()

    def kill(self):
        self.wf().kill()

    def cli(self, *args):
        self.wf().cli(*args)

    def restart(self, *args):
        if "--soft" in args:
            self.stop()
        else:
            self.kill()
        self.start()

    def build(self, *args):
        print("Full build: " + self.server_type)
        self.sp().build("--only" in args, "--non-clean" not in args, False)

    def qbuild(self, *args):
        print("Quick build: " + self.server_type)
        self.sp().build("--only" in args, "--non-clean" not in args, True)

    def cbuild(self, *args):
        print("Build compound pom: " + self.server_type)
        self.sp().build_compound("--clean" in args)

    def deploy(self, *args):
        print("Deploy: " + self.server_type)
        project = self.sp()
        server = self.wf()
        server.deploy(project, "--full" in args, set(filter(lambda x: not x.startswith("--"), args)))

    def ddeploy(self, *args):
        print("Deploy domain: " + self.server_type)
        project = self.sp()
        server = self.wf()
        server.ddeploy(project, "--full" in args, set(filter(lambda x: not x.startswith("--"), args)))

    def dstart(self):
        print("Starting domain: " + self.server_type)
        self.wf().dstart()

    def pid(self):
        pids = list(self.wf().get_servers_pids(verbose=False))
        if pids:
            print(pids[0])

    def sql(self):
        wildfly = self.wf()
        for data_source in wildfly.get_config().get_data_sources():
            if "postgres" in data_source.get_driver():
                pg = cwbar.postgres.Postgres(data_source.get_host(), data_source.get_port(), data_source.get_db(),
                                             data_source.get_user())
                pg.psql()
                return

    def profile(self, *args):
        pids = list(self.wf().get_servers_pids(verbose=False))
        if pids:
            profiler = cwbar.async_profiler.AsyncProfiler(pids[0])
            duration = _param_value_int(args, "--duration", 30)
            output_file_name = _param_value_str(args, "--out", "/tmp/profile_result.svg")
            profiler.profile(duration, output_file_name)
        else:
            print("Сервер не запущен")