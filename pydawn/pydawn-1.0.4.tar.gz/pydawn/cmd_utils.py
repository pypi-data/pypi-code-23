import datetime
import time
import subprocess
import os
import signal
from subprocess import STDOUT, check_output


def run_cmd(cmd, timeout):
    start = datetime.datetime.now()
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if timeout != 0:
        while p.poll() is None:
            time.sleep(1)
            now = datetime.datetime.now()
            if (now - start).seconds > timeout:
                os.kill(p.pid, signal.SIGKILL)
                os.waitpid(-1, os.WNOHANG)
                return [None, None]
    stdout, stderr = p.communicate()
    return [stdout, stderr]


if __name__ == '__main__':
    stdout, stderr = run_cmd("ls", 10)
    print "stdout: %s" % stdout
    print "stderr: %s" % stderr
