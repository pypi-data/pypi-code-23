import random, os
from Crypto.Util import number
from Crypto.Random import random
from pycube import CubeKDF
import socket

class AlphaDHE:
    def __init__(self, keylen=16,socket=None, psize=1024, iterations=10):
        self.keylen = keylen
        if socket != None:
            self.sock = socket
        self.prime_size = psize
        self.iterations = iterations

    def bytestoAZ(self, bts):
        letters = []
        for b in bts:
            letters.append(chr((ord(b) % 26) + 65))
        return "".join(letters)

    def numtoAZ(self, num):
        letters = []
        for n in str(num):
            letters.append(chr(int(n) + 65))
        return "".join(letters)

    def AZtonum(self, letters):
        num = []
        for l in letters:
            num.append(str(ord(l) - 65))
        return int("".join(num))

    def gen_prime(self):
        return number.getStrongPrime(self.prime_size)

    def gen(self):
        g = self.gen_prime()
        p = self.gen_prime()
        secret = random.StrongRandom.randrange(0, (p - 1))
        return g, p, secret

    def srv_exchange(self, client):
        g, p, secret = self.gen()
        client.send(self.numtoAZ(g)+":"+self.numtoAZ(p))
        step = pow(g, secret, p)
        client.send(self.numtoAZ(step))
        step2 = self.AZtonum(client.recv(2048))
        key = number.long_to_bytes(pow(step2, secret, p))
        k = self.bytestoAZ(key)
        return k

    def cli_exchange(self):
        secret = self.gen_prime()
        gp = self.sock.recv(2048)
        g = self.AZtonum(gp.split(":")[0])
        p = self.AZtonum(gp.split(":")[1])
        step = pow(g, secret, p)
        step2 = self.AZtonum(self.sock.recv(2048))
        self.sock.send(self.numtoAZ(step))
        key = number.long_to_bytes(pow(step2, secret, p))
        k = self.bytestoAZ(key)
        return k

    def client(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        self.key = self.cli_exchange()

    def server(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((host, port))
        self.sock.listen(5)
        while True:
            client, addr = self.sock.accept()
            self.key = self.srv_exchange(client)

    def wrapsocket(self, socket):
        self.sock = socket
    
    def init(self):
        g = self.gen_prime()
        p = self.gen_prime()
        secret = self.gen_prime()
        return self.numtoAZ(g), self.numtoAZ(p), self.numtoAZ(secret)
    
    def _step1(self, g, p, secret):
        step1 = pow(self.AZtonum(g), self.AZtonum(secret), self.AZtonum(p))
        return self.numtoAZ(step1)

    def _step2(self, step1, p, secret):
        key = number.long_to_bytes(pow(self.AZtonum(step1), self.AZtonum(secret), self.AZtonum(p)))
        k = self.bytestoAZ(key)
        return CubeKDF(keysize=self.keylen, iterations=self.iterations).genkey(k)
