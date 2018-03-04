from __future__ import print_function
from subprocess import Popen
import shlex

def execute(commands):
    for command in commands:
        args = shlex.split(command)
        proc = Popen(args, shell=False)
        proc.wait()
