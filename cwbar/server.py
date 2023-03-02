import datetime
import glob
import os
import re

import colorama

import cwbar.java.profiler
import cwbar.krupd
import cwbar.postgres
import cwbar.config
import cwbar.source.project
import cwbar.wildfly.wildfly
import cwbar.arguments
import cwbar.cmd
import cwbar.props
import cwbar.config
import cwbar.vim
import cwbar.java.jstack

level = 0


def comment(descr):
    def decorator(func):
        def wrapper(*args, **kwargs):
            global level
            level += 1
            sp = (level - 1) * 2 * " "
            print(f"{sp}{colorama.Fore.GREEN}begin {descr.lower()} {args[0].type} {colorama.Style.RESET_ALL}")
            start = datetime.datetime.now()
            func(*args, **kwargs)
            end = datetime.datetime.now()
            diff = (end - start).total_seconds()
            print(f"{sp}{colorama.Fore.GREEN}end {descr.lower()} {str(end)[:19]} [{diff}s]{colorama.Style.RESET_ALL}")
            level -= 1
        return wrapper
    return decorator


class Server:

    def __init__(self, server_type, name=None, ssh=None):
        self.type = server_type
        self.name = name if name else self.type
        self.ssh = ssh + "-" + self.type if ssh else None

    def get_server_dir(self):
        if self.ssh:
            return os.path.join(cwbar.config.BASE_COMPILE, self.name)
        else:
            return os.path.realpath(os.path.join(cwbar.config.BASE_COMPILE, self.name))

    def get_props_file_name(self):
        return os.path.join(self.get_server_dir(), "jboss.properties")

    def get_wildfly_dir_name(self):
        return glob.glob(os.path.join(self.get_server_dir(), "jboss-*"))[0]

    def get_props(self):
        props_file_name = self.get_props_file_name()
        return cwbar.props.parse_file(props_file_name)

    def get_pid(self):
        pids = list(self.wf().get_servers_pids(verbose=False))
        return pids[0]

    def wf(self):
        wildfly_dir_name = self.get_wildfly_dir_name()
        wildfly_props = self.get_props()
        return cwbar.wildfly.wildfly.Wildfly(wildfly_dir_name, wildfly_props, self.ssh)

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
        return cwbar.source.project.SourceProject.get_project(self.type)

    @comment("View log")
    def log(self, yesterday=False, clean=False, filter_string=None):
        self.wf().log(yesterday, clean, filter_string)

    @comment("Tail log")
    def log_tail(self):
        self.wf().log_tail()

    @comment("Standalone full edit")
    def config(self):
        self.wf().config()

    @comment("Start")
    def start(self, no_spawn=False, jdk=None):
        if jdk:
            os.environ["JAVA_HOME"] = os.path.expanduser(jdk)
        self.kd().start(no_spawn)

    @comment("Stop")
    def stop(self):
        self.kd().stop()

    @comment("Kill")
    def kill(self):
        self.wf().kill()

    @comment("JBoss Cli")
    def cli(self, *args):
        self.wf().cli(*args)

    @comment("Restart")
    def restart(self, soft=False, no_spawn=False, jdk=None):
        if jdk:
            os.environ["JAVA_HOME"] = os.path.expanduser(jdk)
        if soft:
            self.stop()
        else:
            self.kill()
        self.start(no_spawn)

    @comment("Full build")
    def build(self, only=False, non_clean=False, full=False):
        self.sp().build(only, not non_clean, False, full)

    @comment("Quick build")
    def qbuild(self, only=False, non_clean=False, full=False):
        self.sp().build(only, not non_clean, True, full)

    @comment("Compound pom build")
    def cbuild(self, clean=False, full=False):
        self.sp().build_compound(clean, full)

    @comment("Distribution list")
    def dist_list(self, full=False):
        for d in self.sp().get_distribution_projects(full):
            print(d)

    @comment("Deploy")
    def deploy(self, full=False, deployments: list = None):
        project = self.sp()
        server = self.wf()
        server.deploy(project, full, deployments)

    @comment("Deploy domain")
    def ddeploy(self, full=False, deployments=None):
        project = self.sp()
        server = self.wf()
        server.ddeploy(project, full, deployments)

    @comment("Starting domain")
    def dstart(self):
        self.wf().dstart()

    def pid(self):
        pids = list(self.wf().get_servers_pids(verbose=False))
        if pids:
            print(pids[0])

    @comment("psql")
    def sql(self):
        wildfly = self.wf()
        for data_source in wildfly.get_config().get_data_sources():
            if "postgres" in data_source.get_driver():
                pg = cwbar.postgres.Postgres(data_source.get_host(), data_source.get_port(), data_source.get_db(),
                                             data_source.get_user())
                pg.psql()
                return

    @comment("Async profile")
    def profile(self, duration=30, output_file_name="/tmp/profile_result.html"):
        pids = list(self.wf().get_servers_pids(verbose=False))
        if pids:
            profiler = cwbar.java.profiler.AsyncProfiler(pids[0])
            profiler.profile(int(duration), output_file_name)
        else:
            print("Сервер не запущен")

    @comment("Edit jboss.properties")
    def props(self):
        props_file_name = self.get_props_file_name()
        cwbar.vim.edit_file(self.ssh, props_file_name)

    @comment("JStack analyze")
    def jstack(self, file_name=None, filter_string="s.all_tags('krista')", content="no"):
        pid = self.get_pid() if not file_name else None
        jstack = cwbar.java.jstack.JStack(file_name, pid, filter_string)
        tags = jstack.get_tags_map()
        if content == "yes":
            for stack_trace in jstack.stack_traces:
                print(stack_trace)
                print("\n")
        print("total:", len(jstack.stack_traces))
        for tag in tags:
            print("    " + tag + ": " + str(len(tags.get(tag))))

    @comment("BAR")
    def bar(self, only=False, non_clean=False, full=False, spawn=False, quick=False):
        if quick:
            self.qbuild(only, non_clean, full)
        else:
            self.build(only, non_clean, full)
        self.kill()
        self.deploy(full)
        self.start(not spawn)

    @comment("QBAR")
    def qbar(self, only=False, non_clean=False, full=False, spawn=False):
        self.bar(only, non_clean, full, spawn, True)
