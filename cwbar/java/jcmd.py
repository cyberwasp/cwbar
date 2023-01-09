import os

import cwbar.config
import cwbar.cmd


def thread_print(pid):
    command = os.path.join(os.path.expanduser(cwbar.config.JAVA_HOME), "bin", "jcmd") + " " + str(pid) + " Thread.print"
    return cwbar.cmd.execute_with_output(command, split=False)
