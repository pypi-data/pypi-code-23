import sys

from socket import socket
from abc import abstractmethod
from threading import Thread, local
from code import InteractiveInterpreter

from .singleton import SingletonABCMeta
from .managers import ExceptContext

__all__ = ["Consoler"]

_local = local()
_displayhook = sys.displayhook


class StringO(object):
    """
    替代标准输出
    """
    def __init__(self):
        self._buffer = []

    def isatty(self):
        return False

    def close(self):
        pass

    def flush(self):
        pass

    def seek(self, n, mode=0):
        pass

    def readline(self):
        if len(self._buffer) == 0:
            return ''
        ret = self._buffer[0]
        del self._buffer[0]
        return ret

    def reset(self):
        val = ''.join(self._buffer)
        del self._buffer[:]
        return val

    def _write(self, x):
        if isinstance(x, bytes):
            x = x.decode('utf-8', 'replace')
        self._buffer.append(str(x))

    def write(self, x):
        self._write(x)

    def writelines(self, x):
        self._write(''.join(x))


class ThreadedStream(object):

    """Thread-local wrapper for sys.stdout for the interactive console."""

    def push():
        if not isinstance(sys.stdout, ThreadedStream):
            sys.stdout = ThreadedStream()
        _local.stream = StringO()
    push = staticmethod(push)

    def fetch():
        try:
            stream = _local.stream
        except AttributeError:
            return ''
        return stream.reset()
    fetch = staticmethod(fetch)

    def displayhook(obj):
        try:
            stream = _local.stream
        except AttributeError:
            return _displayhook(obj)
        # stream._write bypasses escaping as debug_repr is
        # already generating HTML for us.
        if obj is not None:
            _local._current_ipy.locals['_'] = obj
            stream._write(obj)
    displayhook = staticmethod(displayhook)

    def __setattr__(self, name, value):
        raise AttributeError('read only attribute %s' % name)

    def __dir__(self):
        return dir(sys.__stdout__)

    def __getattribute__(self, name):
        if name == '__members__':
            return dir(sys.__stdout__)
        try:
            stream = _local.stream
        except AttributeError:
            stream = sys.__stdout__
        return getattr(stream, name)

    def __repr__(self):
        return repr(sys.__stdout__)


sys.displayhook = ThreadedStream.displayhook


class CustomInteractiveInterpreter(InteractiveInterpreter):

    def __init__(self, locals):
        super(CustomInteractiveInterpreter, self).__init__(locals)
        self.buffer = []
        self.stdout = sys.stdout
        self.more = False

    def runsource(self, source):
        source = source.rstrip() + '\n'
        try:
            ThreadedStream.push()
            source_to_eval = ''.join(self.buffer + [source])
            # print("exec source : %s"%source_to_eval)
            result = super(CustomInteractiveInterpreter, self).runsource(source_to_eval)
            # print("result: %s"%result)
            if (self.more or result) and source != "\n":
                self.buffer.append(source)
                self.more = True
            else:
                del self.buffer[:]
                self.more = False
        finally:
            output = ThreadedStream.fetch()
            sys.stdout = self.stdout
        prompt = self.more and '... ' or '>>> '
        return prompt + output

    def write(self, data):
        sys.stdout.write(data)


class Consoler(metaclass=SingletonABCMeta):
    """
    通过交互客户端实时了解程序内部变化
    """
    alive = True
    parser = None

    def __init__(self, ls=None):
        if self.args.console:
            self.start_client()
        else:
            if not ls:
                ls = locals()
            self.init_console(ls)
        super(Consoler, self).__init__()

    def init_console(self, locals):
        console_thread = Thread(target=self.console, args=(locals, ))
        console_thread.setDaemon(True)
        console_thread.start()

    def start_client(self):
        client = socket()
        client.connect((self.args.console_host, self.args.console_port))
        result = b""
        while self.alive:
            if not result.count(b"...") and result != b">>> ":
                print(">>> ", end="")
            try:
                cmd = input()
            except KeyboardInterrupt:
                break
            if not cmd:
                cmd = "\n"
            client.send(cmd.encode())
            result = client.recv(102400)
            if result:
                print(result.decode(), end="" if result.count(b"...") or result == b">>> " else "\n")
            else:
                break
        client.close()
        self.alive = False
        sys.exit(0)

    def console(self, locals):
        server = socket()
        server.bind((self.args.console_host, self.args.console_port))
        server.listen(0)
        ci = CustomInteractiveInterpreter(locals)
        _local._current_ipy = ci
        while self.alive:
            client = None
            try:
                client, addr = server.accept()
                while self.alive:
                    cmd = client.recv(102400)
                    if cmd == b"exit" or cmd == b"exit()" or not cmd:
                        break
                    result = ci.runsource(cmd.decode()).encode()
                    client.send(result)
            except Exception as e:
                print(e)
            finally:
                if client:
                    try:
                        client.close()
                    except:
                        pass
        server.close()

    @property
    @abstractmethod
    def args(self):
        pass

    def enrich_parser_arguments(self):
        self.parser.add_argument("--console", help="start a console. ", action="store_true")
        self.parser.add_argument("--console-host", help="console host. ", default="")
        self.parser.add_argument("--console-port", type=int, help="console port. ", default=7878)
