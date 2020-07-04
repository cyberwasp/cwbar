import os

import cwbar.arguments
import cwbar.server
import cwbar.settings

os.environ["JAVA_HOME"] = os.path.expanduser(cwbar.settings.JAVA_HOME)


def main(args):
    if args[1]:
        arguments = cwbar.arguments.Arguments(args)
        server_type = arguments.server_type()
        server_kwargs = arguments.server_kwargs()
        server = cwbar.server.Server(server_type, **server_kwargs)
        op = getattr(server, arguments.command())
        command_args = arguments.command_args(op)
        command_kwargs = arguments.command_kwargs(op)
        op(*command_args, **command_kwargs)
