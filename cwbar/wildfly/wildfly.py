import glob
import os
import re
import shutil
import datetime

import cwbar.cmd
import cwbar.wildfly.config
import cwbar.wildfly.log
import cwbar.config
import cwbar.vim


class Wildfly:

    def __init__(self, home_dir, properties, ssh):
        self._home_dir = home_dir
        self.properties = properties
        self.ssh = ssh
        self._config = None

    def get_conf_file_name(self):
        file_name_list = glob.glob(
            os.path.join(self._home_dir, "standalone", "configuration", "standalone-full.xml"))
        return file_name_list[0] if file_name_list else None

    def get_log_file_name(self, yesterday):
        suffix = ""
        if yesterday:
            suffix = "." + datetime.datetime.strftime(datetime.datetime.now() - datetime.timedelta(1), '%Y-%m-%d')
        return glob.glob(os.path.join(self._home_dir, "standalone", "log", "server.log" + suffix))[0]

    def get_deployment_dir(self):
        return os.path.join(self._home_dir, "standalone", "deployments")

    def get_servers_pids(self, verbose=True):
        cmd = os.path.expanduser(os.path.join(cwbar.config.JAVA_HOME, "bin/", "jps")) + " -m"
        for ps in cwbar.cmd.execute_with_output(cmd, verbose):
            if self._home_dir in ps:
                yield re.match(r"^(\d+)", ps).group(0)

    def get_config(self):
        if not self._config:
            dirname = os.path.dirname(self._home_dir)
            self._config = cwbar.wildfly.config.WildflyConfig(dirname, self.get_conf_file_name())
        return self._config

    def cli(self, *args):
        print("Running cli: " + self._home_dir + " " + " ".join(args))
        cmd = os.path.join(self._home_dir, "bin", "jboss-cli.sh", )
        cwbar.cmd.execute(cmd + " -c --controller=localhost:" + str(self.port(9990)) + " " + " ".join(args))

    def kill(self):
        for pid in self.get_servers_pids():
            cmd = 'kill -s KILL ' + str(pid)
            cwbar.cmd.execute(cmd)

    def log(self, yesterday, clean, filter_string):
        log_file_name = self.get_log_file_name(yesterday)
        if not clean:
            if not filter_string:
                cmd = "vim " + log_file_name
                cwbar.cmd.execute(cmd)
            else:
                log_file = cwbar.wildfly.log.LogFile(log_file_name)
                content = "\n".join(map(lambda x: str(x), log_file.filter(filter_string)))
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
        cwbar.vim.edit_file(self.ssh, conf_file_name)

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

    def start(self, prod=False):
        props = self.properties
        cmd = os.path.join(self._home_dir, "bin", "standalone.bat" if os.name == "nt" else "standalone.sh")
        cmd += " -Dfile.encoding=UTF-8"
        cmd += (" " + props.get("jboss.java.opts", ""))
        cmd += (" -Djboss.node.name=" + props.get("jboss.node.name", "node1"))
        cmd += (" -Djboss.server.base.dir=" + props.get("jboss.bind.address", self.get_base_dir()))
        cmd += (" -Djboss.socket.binding.port-offset=" + props.get("jboss.socket.binding.port-offset", "0"))
        cmd += (" -b " + props.get("jboss.socket.binding.port-offset", "0.0.0.0"))
        cmd += (" -bmanagement " + props.get("jboss.bind.address.management", "0.0.0.0" if not prod else "127.0.0.1"))
        cmd += (" -u " + props.get("jboss.unicast.address", "230.0.0.4"))
        cmd += (" -c " + props.get("jboss.config.file", "standalone-full.xml"))
        if not prod:
            cmd += (" " + props.get("jboss.java.debug.opts", ""))
        cwbar.cmd.execute(cmd)

    def get_base_dir(self):
        return os.path.join(self._home_dir, "standalone")

    def port(self, base_port):
        return base_port + int(self.properties.get("jboss.socket.binding.port-offset", "0"))
