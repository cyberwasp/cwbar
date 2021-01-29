import os
import subprocess


def execute(cmd):
    print(cmd)
    v = os.system(cmd)
    if v > 0:
        raise Exception("Ошибка выполениния команды " + cmd)


def execute_with_output(cmd, verbose=True, split=True):
    if verbose:
        print(cmd)
    process = subprocess.Popen(
        args=cmd,
        stdout=subprocess.PIPE,
        shell=True)
    output = process.communicate()[0].decode("utf-8")
    return output.split("\n") if split else output


def execute_with_input(cmd, input_data, verbose=True):
    if verbose:
        print(cmd)
    process = subprocess.Popen(
        args=cmd,
        stdin=subprocess.PIPE,
        shell=True)
    process.communicate(input_data)


