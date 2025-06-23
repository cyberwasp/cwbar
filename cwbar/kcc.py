import os

import cwbar.cmd
import cwbar.config


class Kcc:

    def __init__(self, root_dir):
        self.root_dir = root_dir

    def kcc(self, *args):
        java = os.path.join(cwbar.config.JAVA_HOME, "bin", "java")
        kcc_jar = os.path.join(self.root_dir, "kcc.jar")
        cmd = " ".join([java, "-jar", kcc_jar] + list(args))
        cwbar.cmd.execute(cmd)

    def start(self, *args):        
        self.kcc(*(["start"] + args))

    def stop(self, *args):
        self.kcc(*(["stop"] + args))


