"""
An msurrogate model server. Start this code to connect from other applications
"""
from __future__ import division, print_function, unicode_literals
import sys
import os
import json
import uuid
import subprocess
import threading


class SurrogateSubprocess(object):

    def __init__(
        self,
        python_call    = None,
        module_name    = None,
        env            = None,
        stdout_prepend = '  PYOUT:',
        stderr_prepend = '  PYERR:',
        args           = [],
        relay_stdout   = True,
        relay_stderr   = True,
    ):

        self.stdout_prepend = stdout_prepend
        self.stderr_prepend = stderr_prepend
        self.relay_stdout = relay_stdout
        self.relay_stderr = relay_stderr

        #update the environment and clear variables with None
        if env is not None:
            env_use = dict(os.environ)
            for k, v in env.items():
                if v is None:
                    try:
                        del env_use[k]
                    except KeyError:
                        pass
                else:
                    env_use[k] = v
        else:
            env_use = None

        if python_call is None:
            python_call = sys.executable

        if module_name is None:
            raise RuntimeError("Must specify module_name")

        #the -u is for unbuffered output (otherwise code must use flush everywhere)
        #-S - and -c - are for the secret to be relayed via stdin and the cookie via stdout.
        self.proc = subprocess.Popen(
            [python_call, '-u', '-m', module_name, '-S', '-', '-c', '-'] + args,
            stdout = subprocess.PIPE,
            stdin  = subprocess.PIPE,
            stderr = subprocess.PIPE,
            env    = env_use,
            bufsize=1,
        )

        #write the secret
        mysecret = str(uuid.uuid4())
        self.proc.stdin.write(mysecret + "\n")

        #start the error feed first so that we can see what is going on
        self.stderr_thread = threading.Thread(
            target = self._stderr_thread_loop,
            name = 'python subprocess stderr feed'
        )
        self.stderr_thread.daemon = True
        self.stderr_thread.start()

        while True:
            line = self.proc.stdout.readline()
            if not line:
                raise RuntimeError("Subprocess Did not complete its output")
            if line.strip() == 'COOKIE_START':
                break
            sys.stdout.write(self.stdout_prepend + line)

        cookie_lines = []
        while True:
            line = self.proc.stdout.readline()
            if not line:
                raise RuntimeError("Subprocess Did not complete its output")
            if line.strip() == 'COOKIE_END':
                break
            cookie_lines.append(line)
        self.cookie_dict = json.loads(''.join(cookie_lines))

        #add the secret back in
        if 'secret' not in self.cookie_dict:
            self.cookie_dict['secret'] = mysecret

        self.stdout_thread = threading.Thread(
            target = self._stdout_thread_loop,
            name = 'python subprocess stdout feed'
        )
        self.stdout_thread.daemon = True
        self.stdout_thread.start()

        return

    def stop(self):
        proc = self.proc
        if proc is not None:
            #TODO need try-catch if already stopped?
            proc.kill()
            #TODO check if process really terminated
            #stops the threads
            self.proc = None
        return

    def _stdout_thread_loop(self):
        proc = self.proc
        while proc is not None:
            line = proc.stdout.readline()
            if not line:
                break
            if self.relay_stdout:
                sys.stdout.write(self.stdout_prepend + line)
            proc = self.proc

    def _stderr_thread_loop(self):
        proc = self.proc
        while proc is not None:
            line = proc.stderr.readline()
            if not line:
                break
            if self.relay_stderr:
                sys.stderr.write(self.stderr_prepend + line)
            proc = self.proc



