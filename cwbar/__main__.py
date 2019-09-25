#!/usr/bin/python3
import glob
import os
import sys
import re

import krupd
import settings
import source_project
import wildfly
import postgres

os.environ["JAVA_HOME"] = settings.JAVA_HOME


def get_server_dir(server_name):
    return os.path.join(settings.BASE_COMPILE, server_name)


def get_wildfly_dir_name(server_name):
    return glob.glob(os.path.join(get_server_dir(server_name), "jboss-*"))[0]


def get_db_set(server_name):
    wildfly = wf(server_name)
    result = set()
    for data_source in wildfly.get_config().get_data_sources():
        result.add(data_source.get_connection())
    return result


def db(server_name):
    print(get_db_set(server_name))


def set_db(server_name, new_name):
    wildfly = wf(server_name)
    cfg = wildfly.get_config()
    for data_source in cfg.get_data_sources():
        if "postgres" in data_source.get_driver():
            data_source.set_connection("jdbc:postgresql://" + new_name)
            m = re.match("(.*?):(.*?)/(.*)", new_name)
            if m:
                user_pass = postgres.lookup_user_pass(*m.groups())
                if user_pass:
                    data_source.set_user(user_pass[0])
                    data_source.set_password(user_pass[1])
            cfg.save()
            print("Set url " + new_name + " for " + data_source.get_name())


def wf(server_name):
    wildfly_dir_name = get_wildfly_dir_name(server_name)
    return wildfly.Wildfly(wildfly_dir_name)


def kd(server_name):
    root_dir = get_server_dir(server_name)
    return krupd.Krupd(root_dir)


def sp(server_name):
    return source_project.SourceProject.get_project(server_name)


def log(server_name):
    wf(server_name).log()


def log_tail(server_name):
    wf(server_name).log_tail()


def config(server_name):
    wf(server_name).config()


def start(server_name):
    print("Starting: " + server_name)
    kd(server_name).start()


def stop(server_name):
    print("Stopping: " + server_name)
    kd(server_name).stop()


def kill(server_name):
    print("Killing: " + server_name)
    wf(server_name).kill()


def cli(server_name, *args):
    wf(server_name).cli(*args)


def restart(server_name, *args):
    if "--soft" in args:
        stop(server_name)
    else:
        kill(server_name)
    start(server_name)


def build(server_name, *args):
    print("Full build: " + server_name)
    sp(server_name).build_with_dependencies("--non-clean" not in args, False)


def qbuild(server_name, *args):
    print("Quick build: " + server_name)
    sp(server_name).build_with_dependencies("--non-clean" not in args, True)


def cbuild(server_name, *args):
    print("Build compound pom: " + server_name)
    sp(server_name).build_compound("--clean" in args)


def deploy(server_name, *args):
    print("Deploy: " + server_name)
    project = sp(server_name)
    server = wf(server_name)
    server.deploy(project, "--full" in args, set(filter(lambda x: not x.startswith("--"), args)))


def ddeploy(server_name, *args):
    print("Deploy domain: " + server_name)
    project = sp(server_name)
    server = wf(server_name)
    server.ddeploy(project, "--full" in args, set(filter(lambda x: not x.startswith("--"), args)))


def dstart(server_name):
    print("Starting domain: " + server_name)
    wf(server_name).dstart()


def pid(server_name):
    pids = list(wf(server_name).get_servers_pids(verbose=False))
    if pids:
        print(pids[0])


def sql(server_name):
    wildfly = wf(server_name)
    for data_source in wildfly.get_config().get_data_sources():
        if "postgres" in data_source.get_driver():
            pg = postgres.Postgres(data_source.get_host(), data_source.get_port(), data_source.get_db(),
                                   data_source.get_user())
            pg.psql()
            return


if len(sys.argv) > 1:
    if sys.argv[1]:
        op = globals()[sys.argv[1].replace("-", "_")]
        server_name = os.path.basename(sys.argv[0])
        args = sys.argv[2:] if len(sys.argv) > 2 else None
        if args:
            op(server_name, *args)
        else:
            op(server_name)
