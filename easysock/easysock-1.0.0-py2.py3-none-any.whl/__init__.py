

'''Easysock is a easy socket interface'''
from socket import *
import sys,time

class Esocket():
    def __init__(self,PORT):
        self.socket=s = socket(AF_INET, SOCK_DGRAM)
        self.socket.bind(('', PORT))
        self.PORT = PORT
    
    def bind(self,PORT):
        self.socket=s = socket(AF_INET, SOCK_DGRAM)
        self.socket.bind(('', PORT))
        self.PORT = PORT
    
    #reciveing code:
    def recive(self,timeout=1):
        start=time.time()
        while start-time.time() < timeout:
            data, wherefrom = self.socket.recvfrom(1500, 0)
            sys.stdout.write(data)
    
    #send code:
    def send(self, data):
        self.socket.sendto(str(data), (SO_BROADCAST, self.PORT))

    
    #closeing code:
    def close(self):
        self.close()
__version__='1.0.0'