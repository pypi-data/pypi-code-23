# coding: utf8

import gevent
from gevent.server import DatagramServer

from .mixins import AppEventsMixin
from .connection import Connection


class Server(AppEventsMixin):

    server_class = DatagramServer
    connection_class = Connection

    box_class = None

    host_list = None
    port = None
    # 连接最长不活跃时间
    timeout = None
    conv = None

    conn_dict = None

    def __init__(self, box_class, host_list, port, timeout=None, conv=None):
        super(Server, self).__init__()
        self.box_class = box_class
        self.host_list = host_list
        self.port = port
        self.timeout = timeout
        self.conv = conv or 0
        self.conn_dict = dict()

    def handle(self, sock, message, address):
        conn = self.conn_dict.get(address)
        if not conn:
            conn = self.connection_class(self, sock, address)
            self.conn_dict[address] = conn

        conn.handle(message)

    def run(self):
        job_list = []
        for host in self.host_list:
            class UDPServer(self.server_class):
                def handle(sub_self, message, address):
                    gevent.spawn(self.handle, sub_self.socket, message, address).join()

            server = UDPServer((host, self.port))
            job_list.append(gevent.spawn(server.serve_forever))

        gevent.joinall(job_list)

    def remove_conn(self, conn):
        self.conn_dict.pop(conn.address, None)
