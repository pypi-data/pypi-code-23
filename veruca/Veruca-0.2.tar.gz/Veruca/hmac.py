from Veruca import Veruca
from MASHHASH import MASH
from pycube import CubeRandom, CubeKDF

class VerucaHMAC:
    def __init__(self, mac_length=32, nonce_length=10):
        self.nonce_length = nonce_length
        self.mac_length = mac_length

    def encrypt(self, data, key):
        k1 = CubeKDF().genkey(key)
        k2 = CubeKDF().genkey(k1)
        nonce = CubeRandom().random(self.nonce_length)
        c = Veruca(k2).encrypt(data, nonce)
        h1 = MASH(length=self.mac_length).digest(nonce+c, k2)
        mac = MASH(length=self.mac_length).digest(h1, k1)
        return mac+nonce+c

    def decrypt(self, data, key):
        k1 = CubeKDF().genkey(key)
        k2 = CubeKDF().genkey(k1)
        mac = data[:self.mac_length]
        nonce = data[self.mac_length:self.mac_length+self.nonce_length]
        c = data[self.mac_length+self.nonce_length:]
        h1 = MASH(length=self.mac_length).digest(nonce+c, k2)
        mac_check = MASH(length=self.mac_length).digest(h1, k1)
        if mac_check == mac:
            p = Veruca(k2).decrypt(c, nonce)
            return p
        else:
            raise ValueError('HMAC FAILED: Message has been tampered with.')
