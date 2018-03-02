from abc import ABCMeta, abstractmethod
import asyncore
import socket

from .dcache import Envelope, CouldNotReadEnvelope
from .utils import MakeLines


#def definitely_send(socket, s):
#    while s:
#        try:
#            n = socket.send(s)
#            s = s[n:]
#            break
#        except IOError as e:
#            if e.errno == errno.EAGAIN:
#                sys.stderr.write('E')
#                time.sleep(0.1)
#                continue
#            if e.errno == 98:
#                print('broken pipe')
#                raise
def tcplisten(mi, port):
    server = EchoServer(mi, '0.0.0.0', port)
    while 1:
        asyncore.loop(count=1, timeout=1.0)
        for e in mi.get_all_available_for_me():
            for addr, socket in server.addr2socket.items():
                if e.maddr_to.startswith(addr):
                    rest = e.maddr_to[len(addr):]
                    e.maddr_to = rest
                    s = e.to_json() + '\n'
                    try:
                        socket.setblocking(1)
                        socket.sendall(s)
                    except IOError as e:
                        print('Could not send packet: ' + e)
                    break
            else:
                msg = 'Could not route connection %s' % e.maddr_to
                print(msg)


class Processor():
    __metaclass__ = ABCMeta

    def set_handler(self, handler):
        self.handler = handler

    @abstractmethod
    def receive(self, line):
        pass

    def send(self, line):
        self.handler.send(line)


class EchoHandler(asyncore.dispatcher_with_send):

    def init(self, processor):
        self.processor = processor
        self.ml = MakeLines()

    def handle_read(self):
        s = self.recv(8192)
#        print('handle_read : %r' % s)
        self.ml.push(s)
        for line in self.ml.get_lines():
#            print('line : %r' % line)
            self.processor.receive(line)


class EchoServer(asyncore.dispatcher):

    def __init__(self, mi, host, port):
        self.mi = mi
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)
        self.addr2socket = {}

    def handle_accept(self):
        pair = self.accept()

        if pair is not None:
            sock, addr = pair
            sock.setblocking(1)
            maddr = '/ip4/%s/tcp/%s' % addr
            self.addr2socket[maddr] = sock
            print('Incoming connection from %s' % maddr)
            handler = EchoHandler(sock)
            processor = MyProcessor(self.mi, addr)
            processor.set_handler(handler)
            handler.init(processor)


class MyProcessor(Processor):

    def __init__(self, mi, addr):
        self.mi = mi
        self.host, self.port = addr

    def receive(self, line):
        try:
            env = Envelope.from_json(line)
        except CouldNotReadEnvelope as e:
            print(str(e))
            self.send(str(e) + '\n')
        else:
            m = '/ip4/%s/tcp/%s' % (self.host, self.port)
            env.maddr_from = m + env.maddr_from
            print('dispatching %s' % env)
            self.mi.dispatch(env)

