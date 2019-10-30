import glob
import os
import re
import shutil

import cwbar.wildfly_config
import cwbar.cmd


class Wildfly:

    def __init__(self, home_dir):
        self._home_dir = home_dir
        self._config = None

    def get_conf_file_name(self):
        file_name_list = glob.glob(
            os.path.join(self._home_dir, "standalone", "configuration", "standalone-full.xml"))
        return file_name_list[0] if file_name_list else None

    def get_log_file_name(self):
        return glob.glob(os.path.join(self._home_dir, "standalone", "log", "server.log"))[0]

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

    def log(self):
        log_file_name = self.get_log_file_name()
        cmd = "vim " + log_file_name
        cwbar.cmd.execute(cmd)

    def log_tail(self):
        log_file_name = self.get_log_file_name()
        cmd = "tail -f " + log_file_name
        cwbar.cmd.execute(cmd)

    def config(self):
        conf_file_name = self.get_conf_file_name()
        cmd = "vim " + conf_file_name
        cwbar.cmd.execute(cmd)

    def deploy(self, project, full, project_names):
        targets = project.get_distribution_project_targets(full)
        deployment_dir = self.get_deployment_dir()
        for target in targets:
            if len(project_names) == 0 or os.path.basename(target).split(".")[0] in project_names:
                print("Copy " + target)
                shutil.copy(target, deployment_dir)

    def ddeploy(self, project, full, project_names):
        targets = project.get_distribution_project_targets(full)
        for target in targets:
            if len(project_names) == 0 or os.path.basename(target).split(".")[0] in project_names:
                self.cli("-c", "--command=\"deploy --force " + target + "\"")

    def dstart(self):
        cwbar.cmd.execute(os.path.join(self._home_dir, "bin", "domain.sh"))
