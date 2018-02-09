"""
bjoda, better commands and subprocesses for python
"""
import locale
import os
import shlex
import signal
import subprocess
import sys
from bjoda.globals import (
    DEFAULT_TIMEOUT,
    STR_TYPES
)
from bjoda.strings import (
    EXIT_STRINGS
)
from pexpect.popen_spawn import (
    PopenSpawn
)


class Bjoda(object):
    """the bjoda command object"""
    def __init__(self, command, timeout=DEFAULT_TIMEOUT):
        super(Bjoda, self).__init__()
        self.command = command
        self.timeout = timeout
        self.subprocess = None
        self.blocking = None
        self.was_run = False
        self.__out = None
        self.__err = None

    def __repr__(self):
        """repr magic method"""
        return '<Bjoda {!r}>'.format(self.command)

    @property
    def _popen_args(self):
        """generated command string"""
        return self.command

    @property
    def _default_popen_kwargs(self):
        """default arguments for the given command"""
        return {
            'env': os.environ.copy(),
            'stdin': subprocess.PIPE,
            'stdout': subprocess.PIPE,
            'stderr': subprocess.PIPE,
            'shell': True,
            'universal_newlines': True,
            'bufsize': 0
        }

    @property
    def _default_pexpect_kwargs(self):
        encoding = 'utf-8'
        if sys.platform == 'win32':
            default_encoding = locale.getdefaultlocale()[1]
            if default_encoding is not None:
                encoding = default_encoding
        return {
            'env': os.environ.copy(),
            'encoding': encoding,
            'timeout': self.timeout
        }

    @property
    def _uses_subprocess(self):
        """if it uses subprocess"""
        return isinstance(self.subprocess, subprocess.Popen)

    @property
    def _uses_pexpect(self):
        """if it uses pexpect"""
        return isinstance(self.subprocess, PopenSpawn)

    @property
    def std_out(self):
        """standard output for subprocess"""
        return self.subprocess.stdout

    @property
    def _pexpect_out(self):
        """standard output for pexpect"""
        if self.subprocess.encoding:
            result = ''
        else:
            result = b''
        if self.subprocess.before:
            result += self.subprocess.before

        if self.subprocess.after:
            result += self.subprocess.after

        result += self.subprocess.read()
        return result

    @property
    def out(self):
        """std/out output (cached)"""
        if self.__out is not None:
            return self.__out
        if self._uses_subprocess:
            self.__out = self.std_out.read()
        else:
            self.__out = self._pexpect_out
        return self.__out

    @property
    def out_float(self):
        """returns the first line of output, stripped, converted to a float"""
        return float(self.out.split('\n')[0].strip())

    @property
    def out_int(self):
        """returns the first line of output, stripped, converted to an int"""
        return int(self.out_float)

    @property
    def out_bool(self):
        """returns the first line of output, stripped, converted to an int, and then to a bool"""
        return bool(self.out_bool)

    @property
    def std_err(self):
        """standard error for subprocess"""
        return self.subprocess.stderr

    @property
    def err(self):
        """standard error (cached)"""
        if self.__err is not None:
            return self.__err
        if self._uses_subprocess:
            self.__err = self.std_err.read()
            return self.__err
        return self._pexpect_out

    @property
    def pid(self):
        """The process' PID."""
        if hasattr(self.subprocess, 'proc'):
            return self.subprocess.proc.pid
        return self.subprocess.pid

    @property
    def exit_code(self):
        """process return code"""
        if self._uses_pexpect:
            return self.subprocess.exitstatus
        return self.subprocess.returncode

    @property
    def exit_message(self):
        """process exit message if we have one"""
        if self.exit_code and self.exit_code > 0:
            if self.exit_code in EXIT_STRINGS:
                return EXIT_STRINGS[self.exit_code]
            return '[{}] Command Exited with non-zero return code'.format(self.exit_code)
        return ''

    @property
    def std_in(self):
        """standard in pipe"""
        return self.subprocess.stdin

    def run(self, block=True, binary=False, cwd=None):
        """Runs the given command, with or without pexpect functionality enabled."""
        self.blocking = block
        # Use subprocess.
        if self.blocking:
            popen_kwargs = self._default_popen_kwargs.copy()
            popen_kwargs['universal_newlines'] = not binary
            if cwd:
                popen_kwargs['cwd'] = cwd
            spawn = subprocess.Popen(self._popen_args, **popen_kwargs)
        # Otherwise, use pexpect.
        else:
            pexpect_kwargs = self._default_pexpect_kwargs.copy()
            if binary:
                pexpect_kwargs['encoding'] = None
            if cwd:
                pexpect_kwargs['cwd'] = cwd
            # Enable Python subprocesses to work with expect functionality.
            pexpect_kwargs['env']['PYTHONUNBUFFERED'] = '1'
            spawn = PopenSpawn(self._popen_args, **pexpect_kwargs)
        self.subprocess = spawn
        self.was_run = True

    def expect(self, pattern, timeout=-1):
        """Waits on the given pattern to appear in std_out"""
        if self.blocking:
            raise RuntimeError('expect can only be used on non-blocking commands.')
        self.subprocess.expect(pattern=pattern, timeout=timeout)

    def send(self, message, end=os.linesep, is_signal=False):
        """Sends the given string or signal to std_in."""
        if self.blocking:
            raise RuntimeError('send can only be used on non-blocking commands.')
        if not is_signal:
            if self._uses_subprocess:
                return self.subprocess.communicate(message + end)
            return self.subprocess.send(message + end)
        return self.subprocess.send_signal(message)

    def terminate(self):
        """kills the process with a SIGTERM"""
        self.subprocess.terminate()

    def kill(self):
        """kills the process with a SIGINT"""
        self.subprocess.kill(signal.SIGINT)

    def kill9(self):
        """kill9's the process with SIGKILL"""
        self.subprocess.kill(signal.SIGKILL)

    def block(self):
        """Blocks until process is complete."""
        if self._uses_subprocess:
            # consume stdout and stderr
            try:
                stdout, stderr = self.subprocess.communicate()
                self.__out = stdout
                self.__err = stderr
            except ValueError:
                pass
        else:
            self.subprocess.wait()

    def pipe(self, command, timeout=None, cwd=None):
        """Runs the current command and passes its output to the next given process"""
        if not timeout:
            timeout = self.timeout

        if not self.was_run:
            self.run(block=False, cwd=cwd)

        data = self.out

        if timeout:
            proc = Bjoda(command, timeout)
        else:
            proc = Bjoda(command)

        proc.run(block=False, cwd=cwd)
        if data:
            proc.send(data)
            proc.subprocess.sendeof()
        proc.block()
        return proc


def _expand_args(command):
    """Parses command strings and returns a Popen-ready list."""
    if isinstance(command, STR_TYPES):
        if sys.version_info[0] == 2:
            splitter = shlex.shlex(command.encode('utf-8'))
        elif sys.version_info[0] == 3:
            splitter = shlex.shlex(command)
        else:
            splitter = shlex.shlex(command.encode('utf-8'))
        splitter.whitespace = '|'
        splitter.whitespace_split = True
        new_command = []

        while True:
            token = splitter.get_token()
            if token:
                new_command.append(token)
            else:
                break
        new_command = list(map(shlex.split, new_command))
    return new_command


def chain(command, timeout=DEFAULT_TIMEOUT, cwd=None):
    """run a command as a chain of commands"""
    commands = _expand_args(command)
    data = None
    for individual_command in commands:
        proc = run(individual_command, block=False, timeout=timeout, cwd=cwd)

        if data:
            proc.send(data)
            proc.subprocess.sendeof()
        data = proc.out

    return proc


def run(command, block=True, binary=False, timeout=DEFAULT_TIMEOUT, cwd=None):
    """run the given command with the specified options"""
    proc = Bjoda(command, timeout=timeout)
    proc.run(block=block, binary=binary, cwd=cwd)
    if block:
        proc.block()
    return proc
