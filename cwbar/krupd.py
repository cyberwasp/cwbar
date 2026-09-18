import os

import cwbar.cmd


class Krupd:

    def __init__(self, root_dir):
        self.root_dir = root_dir

    def krupd(self, *args):
        env = {"PGDATABASE": None, "PGHOST": None, "PGPORT": None, "PGUSER": None}
        cmd = " ".join([os.path.join(self.root_dir, "krupd")] + list(args))
        cwbar.cmd.execute(cmd, env=env)

    def start(self, no_spawn=False):
        self.krupd("jboss.start.debug" + (".nospawn" if no_spawn else ""))

    def stop(self):
        self.krupd("jboss.stop")


