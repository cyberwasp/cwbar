import os
import subprocess


def execute(cmd):
    print(cmd)
    v = os.system(cmd)
    if v > 0:
        raise Exception("Ошибка выполениния команды " + cmd)


def execute_with_output(cmd, verbose=True):
    if verbose:
        print(cmd)
    process = subprocess.Popen(
        args=cmd,
        stdout=subprocess.PIPE,
        shell=True)
    return process.communicate()[0].decode("utf-8").split("\n")
