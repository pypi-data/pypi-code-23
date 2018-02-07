#!/usr/bin/env python
"""
Client side: use sockets to send data to the server, and print server's
reply to each message line; 'localhost' means that the server is running
on the same machine as the client, which lets us test client and server
on one machine; to test over the Internet, run a server on a remote
machine, and set serverHost or argv[1] to machine's domain name or IP addr;
Python sockets are a portable BSD socket interface, with object methods
for the standard socket calls available in the system's C library;
"""

import sys
from socket import * # portable socket interface plus constants
from datetime import *
import time
#global lastSN

MAX = 128
class TCPClient():
    def __init__(self,serverHost='138.197.6.173',serverPort=10001,clientID='0000'):
        self.serverHost = serverHost # server name
        self.serverPort = serverPort # non-reserved port used by the server
        self.socketobj = socket(AF_INET, SOCK_STREAM)  # make a TCP/IP socket object
        self.received = None

    def connect(self):
        #sockobj = socket(AF_INET, SOCK_STREAM)  # make a TCP/IP socket object
        self.socketobj.connect((self.serverHost, self.serverPort))  # connect to server machine + port

    def send(self,data,size=MAX):#command should by byte string
        self.socketobj.sendall(data.encode())

    def receive(self, size=MAX):
        #todo wait for new line
        while True:
            data = ''
            try:
                data += self.socketobj.recv(MAX).decode()
                while data:
                    if '\n' in data:
                        lines = data.splitlines()
                        if len(lines) == 1:
                            self.received(lines[0])
                            data = ''
                        else:
                            for line in lines[:-1]:
                                if len(line.strip()) != 0:
                                    self.received(line)
                            data = lines[-1]
                    data += self.socketobj.recv(MAX).decode()
                if data == '':
                    self.received('disconnected')
                    return
            except Exception as ex:
                print('tcp error:' + str(ex))
                try:
                    #self.connect()
                    self.received('disconnected')
                except Exception as ex1:
                    print('another error' + str(ex1))
                    self.received('disconnected')
                return

if __name__ == '__main__':
    pass
