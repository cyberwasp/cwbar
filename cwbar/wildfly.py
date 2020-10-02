import glob
import os
import re
import shutil
from datetime import timedelta, datetime

import cwbar.cmd
import cwbar.wildfly_config
from cwbar import wildfly_log


class Wildfly:

    def __init__(self, home_dir):
        self._home_dir = home_dir
        self._config = None

    def get_conf_file_name(self):
        file_name_list = glob.glob(
            os.path.join(self._home_dir, "standalone", "configuration", "standalone-full.xml"))
        return file_name_list[0] if file_name_list else None

    def get_log_file_name(self, yesterday):
        suffix = ""
        if yesterday:
            suffix = "." + datetime.strftime(datetime.now() - timedelta(1), '%Y-%m-%d')
        return glob.glob(os.path.join(self._home_dir, "standalone", "log", "server.log" + suffix))[0]

    def get_deployment_dir(self):
        return os.path.join(self._home_dir, "standalone", "deployments")

    def get_servers_pids(self, verbose=True):
        cmd = "jps -m"
        for ps in cwbar.cmd.execute_with_output(cmd, verbose):
            if self._home_dir in ps:
                yield re.match(r"^(\d+)", ps).group(0)

    def get_config(self):
        if not self._config:
            dirname = os.path.dirname(self._home_dir)
            self._config = cwbar.wildfly_config.WildflyConfig(dirname, self.get_conf_file_name())
        return self._config

    def cli(self, *args):
        print("Running cli: " + self._home_dir + " " + " ".join(args))
        cmd = os.path.join(self._home_dir, "bin", "jboss-cli.sh")
        cwbar.cmd.execute(cmd + " " + " ".join(args))

    def kill(self):
        for pid in self.get_servers_pids():
            cmd = 'kill -s KILL ' + str(pid)
            cwbar.cmd.execute(cmd)

    def log(self, yesterday, clean, filter_string):
        log_file_name = self.get_log_file_name(yesterday)
        if not clean:
            if not filter:
                cmd = "vim " + log_file_name
                cwbar.cmd.execute(cmd)
            else:
                content = "\n".join(map(lambda x: str(x), wildfly_log.LogFile(log_file_name).filter(filter_string)))
                cmd = "vim - << EOF\n" + content + "\nEOF\n"
                cwbar.cmd.execute(cmd)
        else:
            shutil.copy(log_file_name, log_file_name + ".old")
            with open(log_file_name, "w"):
                pass

    def log_tail(self):
        log_file_name = self.get_log_file_name(False)
        cmd = "tail -f " + log_file_name
        cwbar.cmd.execute(cmd)

    def config(self):
        conf_file_name = self.get_conf_file_name()
        cmd = "vim " + conf_file_name
        cwbar.cmd.execute(cmd)

    def deploy(self, project, full, deployments):
        targets = project.get_distribution_project_targets(full)
        deployment_dir = self.get_deployment_dir()
        for target in targets:
            if not deployments or os.path.basename(target).split(".")[0] in deployments:
                print("Copy " + target)
                shutil.copy(target, deployment_dir)

    def ddeploy(self, project, full, project_names):
        targets = project.get_distribution_project_targets(full)
        for target in targets:
            if len(project_names) == 0 or os.path.basename(target).split(".")[0] in project_names:
                self.cli("-c", "--command=\"deploy --force " + target + "\"")

    def dstart(self):
        cwbar.cmd.execute(os.path.join(self._home_dir, "bin", "domain.sh"))
