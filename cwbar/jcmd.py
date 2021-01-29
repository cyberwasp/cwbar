import os

from cwbar import cmd, settings


def thread_print(pid):
    command = os.path.join(os.path.expanduser(settings.JAVA_HOME), "bin", "jcmd") + " " + str(pid) + " Thread.print"
    return cmd.execute_with_output(command, split=False)
