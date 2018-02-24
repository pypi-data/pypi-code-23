
from multiprocessing import Queue
import socket
from threading import Thread

from contracts.utils import check_isinstance

from .dcache import Envelope
from .tcpendpoint import MakeLines


class AsyncLineBasedConnection():

    def __init__(self, host, port):
        addr = (host, port)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(addr)
        print('Connected to %s:%s' % (addr))

        self.q_in = Queue()
        self.q_out = Queue()

        address = '/ip4/%s/tcp/%s/lswarm' % (host, port)
        thread1 = Thread(target=read_from_socket, args=(s, self.q_in, address))
        thread1.daemon = True
        thread1.start()
        thread2 = Thread(target=write_to_socket, args=(s, self.q_out,))
        thread2.daemon = True
        thread2.start()

    def get_q_inbound(self):
        return self.q_in

    def get_q_outbound(self):
        return self.q_out


def read_from_socket(socket, q_in, address):
    ml = MakeLines()
    while True:
        chars = socket.recv(1)
        ml.push(chars)
        for line in ml.get_lines():
            env = Envelope.from_json(line)
            env.maddr_from = address + env.maddr_from
            q_in.put(env)


def write_to_socket(socket, q_out):
    while True:
        env = q_out.get()
        check_isinstance(env, Envelope)
        line = env.to_json()
        print('writing %s' % env.contents)
        socket.sendall(line + '\n')

