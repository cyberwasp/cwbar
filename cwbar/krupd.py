import os

import cwbar.cmd


class Krupd:

    def __init__(self, root_dir):
        self.root_dir = root_dir

    def krupd(self, *args):
        cmd = " ".join([os.path.join(self.root_dir, "krupd")] + list(args))
        cwbar.cmd.execute(cmd)

    def start(self):
        self.krupd("jboss.start.debug")

    def stop(self):
        self.krupd("jboss.start.debug")


