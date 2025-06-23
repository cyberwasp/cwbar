import os
import colorama

import cwbar.arguments
import cwbar.server
import cwbar.config


def main(args):
    if args[1]:
        colorama.init()
        arguments = cwbar.arguments.Arguments(args)
        server_type = arguments.server_type()
        server_name = arguments.server_name()
        server_kwargs = arguments.server_kwargs()
        server = cwbar.server.Server(server_type, name = server_name, **server_kwargs)
        op = getattr(server, arguments.command())
        command_args = arguments.command_args(op)
        command_kwargs = arguments.command_kwargs(op)
        op(*command_args, **command_kwargs)
