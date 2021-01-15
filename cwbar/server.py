import datetime
import glob
import os
import re

import cwbar.async_profiler
import cwbar.krupd
import cwbar.postgres
import cwbar.settings
import cwbar.source_project
import cwbar.wildfly
import cwbar.arguments
import cwbar.cmd


class Server:

    def __init__(self, server_type, name=None, ssh=None):
        self.type = server_type
        self.name = name if name else self.type
        self.ssh = ssh + "-" + type if ssh else None

    def get_server_dir(self):
        return os.path.realpath(os.path.join(cwbar.settings.BASE_COMPILE, self.name))

    def get_props_file_name(self):
        return os.path.join(self.get_server_dir(), "jboss.properties")

    def get_wildfly_dir_name(self):
        return glob.glob(os.path.join(self.get_server_dir(), "jboss-*"))[0]

    def get_props(self):
        props_file_name = self.get_props_file_name()
        result = {}
        prev_line = ""
        with open(props_file_name, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("#"):
                    continue
                if line.endswith("\\"):
                    prev_line += line[:-1]
                    continue
                if prev_line:
                    line = prev_line + line
                p = line.index("=")
                if p > 0:
                    result[line[:p].strip()] = line[p + 1:].strip()
        return result

    def wf(self):
        wildfly_dir_name = self.get_wildfly_dir_name()
        wildfly_props = self.get_props()
        return cwbar.wildfly.Wildfly(wildfly_dir_name, wildfly_props)

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
        return cwbar.source_project.SourceProject.get_project(self.type)

    def log(self, yesterday=False, clean=False, filter=None):
        self.wf().log(yesterday, clean, filter)

    def log_tail(self):
        self.wf().log_tail()

    def config(self):
        self.wf().config()

    def start(self, no_spawn=False):
        self.kd().start(no_spawn)

    def stop(self):
        self.kd().stop()

    def kill(self):
        self.wf().kill()

    def cli(self, *args):
        self.wf().cli(*args)

    def restart(self, soft=False):
        if soft:
            self.stop()
        else:
            self.kill()
        self.start()

    def build(self, only=False, non_clean=False, full=False):
        print("Full build: " + self.type)
        self.sp().build(only, not non_clean, False, full)
        print("Ends: " + str(datetime.datetime.now()))

    def qbuild(self, only=False, non_clean=False, full=False):
        print("Quick build: " + self.type)
        self.sp().build(only, not non_clean, True, full)
        print("Ends: " + str(datetime.datetime.now()))

    def cbuild(self, clean=False, full=False):
        print("Build compound pom: " + self.type)
        self.sp().build_compound(clean, full)
        print("Ends: " + str(datetime.datetime.now()))

    def dist_list(self, full=False):
        print("Distributions list: " + self.type)
        for d in self.sp().get_distribution_projects(full):
            print(d)
        print("Ends: " + str(datetime.datetime.now()))

    def deploy(self, full=False, deployments: list = None):
        print("Deploy: " + self.type)
        project = self.sp()
        server = self.wf()
        server.deploy(project, full, deployments)

    def ddeploy(self, full=False, deployments=None):
        print("Deploy domain: " + self.type)
        project = self.sp()
        server = self.wf()
        server.ddeploy(project, full, deployments)

    def dstart(self):
        print("Starting domain: " + self.type)
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

    def profile(self, duration=30, output_file_name="/tmp/profile_result.svg"):
        pids = list(self.wf().get_servers_pids(verbose=False))
        if pids:
            profiler = cwbar.async_profiler.AsyncProfiler(pids[0])
            profiler.profile(int(duration), output_file_name)
        else:
            print("Сервер не запущен")

    def props(self):
        props_file_name = self.get_props_file_name()
        cmd = "vim " + props_file_name
        cwbar.cmd.execute(cmd)
