import os
import sys

import cwbar.settings
import cwbar.server
import cwbar.arguments

os.environ["JAVA_HOME"] = cwbar.settings.JAVA_HOME

if len(sys.argv) > 1:
    if sys.argv[1]:
        arguments = cwbar.arguments.Arguments(sys.argv)
        server_type = arguments.server_type()
        server_kwargs = arguments.server_kwargs()
        server = cwbar.server.Server(server_type, **server_kwargs)
        op = getattr(server, arguments.command())
        command_args = arguments.command_args(op)
        command_kwargs = arguments.command_kwargs(op)
        op(*command_args, **command_kwargs)
