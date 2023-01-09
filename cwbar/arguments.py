import inspect
import os


def _is_full_var_args(func):
    spec = inspect.getfullargspec(func)
    return not spec.defaults and not spec.varkw


def _args_to_kwargs(args):
    kwargs = {}
    for kwarg in args:
        name, value = kwarg.split("=") if "=" in kwarg else (kwarg, True)
        kwargs[name[2:].replace("-", "_")] = value
    return kwargs


class Arguments:

    def __init__(self, args):
        self._raw_command = next(filter(lambda x: not x.startswith("--"), args[1:]), None)
        self._command_index = args.index(self._raw_command)
        self._server_type = os.environ.get("SERVER_TYPE")
        self._server_type = self._server_type if self._server_type else os.path.basename(args[0])
        self._server_kwargs = _args_to_kwargs(args[1:self._command_index])
        self._command_args = args[self._command_index + 1:]
        self._command_kwargs = _args_to_kwargs(args[self._command_index + 1:])

    def server_type(self):
        return self._server_type

    def server_kwargs(self):
        return self._server_kwargs

    def command(self):
        return self._raw_command.replace("-", "_")

    def command_args(self, command_func):
        return self._command_args if _is_full_var_args(command_func) else []

    def command_kwargs(self, command_func):
        return self._command_kwargs if not _is_full_var_args(command_func) else {}
