"""Continuous-stream network server classes.

Example:
    >>> from dtplib.clientserver import Server, Client
    >>> def serverHandle(data, conn, addr):
    ...     print data.swapcase()
    ...
    >>> def clientHandle(data):
    ...     print data[::-1]
    ...
    >>> server = Server(serverHandle)
    >>> server.start()
    >>> addr = server.getAddr()
    >>> client = Client(clientHandle)
    >>> client.connect(addr)
    >>> client.send("Hello World!")
    hELLO wORLD!
    >>> server.sendAll("foo bar")
    rab oof
    >>> client.disconnect()
    >>> server.stop()
"""

import socket
import threading
try:
    import cPickle as pickle
except ImportError:
    import pickle
import binascii
from .encrypt import newKeyPair, encrypt, decrypt

buffersize = 4096
sockFamily = socket.AF_INET
sockType = socket.SOCK_STREAM

class ClientServerError(Exception):
    pass

class Client:
    """Connect to a server and send and receive information
    continuously.

    'handler' is a function which takes the data packet argument.
    Any Python object can be passed through the send method, as it
    supports serialization.
    """
    def __init__(self, handler):
        self.handler = handler
        self.sock = None
        self.host = None
        self.port = None
        self.running = False
        self.serveThread = None
        self.sock = None
        self.pubKey = None
        self.privKey = None

    def connect(self, addr):
        """Connect to a server."""
        (host, port) = addr
        if self.running:
            raise ClientServerError("already connected to server")
        self.sock = socket.socket(sockFamily, sockType)
        self.sock.connect((host, port))
        cPub, cPriv = newKeyPair()
        sPub = ""
        while len(sPub) % buffersize == 0:
            chunk = self.sock.recv(buffersize)
            if not chunk:
                self.disconnect()
                raise ClientServerError("socket connection broken")
            sPub += chunk
        sPub = pickle.loads(sPub)
        cPub = pickle.dumps(cPub)
        if len(cPub) % buffersize == 0:
            cPub += " "
        self.sock.send(cPub)
        self.sock.recv(1)
        self.pubKey = sPub
        self.privKey = cPriv
        self.running = True
        self.host = host
        self.port = port
        self.serveThread = threading.Thread(target = self.handle)
        self.serveThread.daemon = True
        self.serveThread.start()

    def disconnect(self):
        """Disconnect from the server."""
        self.running = False
        self.sock.close()
        self.sock = None
        self.pubKey = None
        self.privKey = None

    def handle(self):
        extra = ""
        while True:
            packet = ""
            while True:
                if extra:
                    chunk = extra
                else:
                    chunk = self.sock.recv(buffersize)
                    if not chunk:
                        self.disconnect()
                        raise ClientServerError("socket connection broken")
                if " " in chunk:
                    extra = chunk[chunk.index(" ") + 1:]
                    chunk = chunk[:chunk.index(" ")]
                    packet += chunk
                    break
                packet += chunk
            packet = binascii.unhexlify(packet)
            packet = decrypt(packet, self.privKey)
            packet = pickle.loads(packet)
            self.handler(packet)

    def getAddr(self):
        """Get the address of the client in the format (host, port)."""
        return self.sock.getsockname()

    def getServerAddr(self):
        """Get the address of the server in the format (host, port)."""
        return self.sock.getpeername()

    def send(self, packet):
        """Send data packets to the server."""
        if not self.running:
            raise ClientServerError("not connected to a server")
        packet = pickle.dumps(packet)
        packet = encrypt(packet, self.pubKey)
        packet = binascii.hexlify(packet)
        packet += " "
        self.sock.send(packet)

class Server:
    """Serve clients continuously.

    'handler' is a function which takes the data packet, client socket
    object, and client address arguments.
    Leave port = 0 for an arbitrary, unused port.
    Server.host can be changed to '', 'localhost', etc. before the
    start method is called.
    Any Python object can be passed through the send method, as it
    supports serialization.
    """
    def __init__(self, handler, port=0):
        self.handler = handler
        self.sock = None
        self.host = socket.gethostname()
        self.port = port
        self.running = False
        self.serveThread = None
        self.sock = None
        self.clients = []
        self.pubKey = None
        self.privKey = None

    def start(self):
        """Start the server."""
        if self.running:
            raise ClientServerError("server already running")
        self.sock = socket.socket(sockFamily, sockType)
        self.sock.bind((self.host, self.port))
        self.sock.listen(5)
        self.running = True
        self.serveThread = threading.Thread(target = self.serve)
        self.serveThread.daemon = True
        self.serveThread.start()

    def stop(self):
        """Stop the server."""
        self.running = False
        for client in self.clients:
            client[0].close()
        self.clients = []
        killsock = socket.socket(sockFamily, sockType)
        killsock.connect(self.getAddr())
        killsock.close()
        self.sock.close()
        self.sock = None
        self.pubKey = None
        self.privKey = None

    def serve(self):
        while True:
            conn, addr = self.sock.accept()
            if not self.running:
                break
            sPub, sPriv = newKeyPair()
            sPub = pickle.dumps(sPub)
            if len(sPub) % buffersize == 0:
                sPub += " "
            conn.send(sPub)
            cPub = ""
            try:
                while len(cPub) % buffersize == 0:
                    chunk = conn.recv(buffersize)
                    if not chunk:
                        conn.close()
                        raise ClientServerError("socket connection broken")
                    cPub += chunk
            except ClientServerError:
                continue
            cPub = pickle.loads(cPub)
            conn.send(" ")
            self.clients.append((conn, addr, cPub, sPriv))
            t = threading.Thread(target = self.handle, args = (conn, addr, cPub, sPriv))
            t.daemon = True
            t.start()

    def handle(self, conn, addr, pubKey, privKey):
        extra = ""
        while True:
            packet = ""
            while True:
                if extra:
                    chunk = extra
                else:
                    chunk = conn.recv(buffersize)
                    if not chunk:
                        self.remove(conn)
                        return
                if " " in chunk:
                    extra = chunk[chunk.index(" ") + 1:]
                    chunk = chunk[:chunk.index(" ")]
                    packet += chunk
                    break
                packet += chunk
            packet = binascii.unhexlify(packet)
            packet = decrypt(packet, privKey)
            packet = pickle.loads(packet)
            self.handler(packet, conn, addr)

    def remove(self, conn):
        """Remove a client."""
        conn.close()
        for i in range(len(self.clients)):
            if conn is self.clients[i][0]:
                del self.clients[i]

    def getAddr(self):
        """Get the address of the server in the format (host, port)."""
        return self.sock.getsockname()

    def getClientAddr(self, conn):
        """Get the address of the client in the format (host, port)."""
        return self.sock.getpeername()

    def send(self, packet, conn):
        """Send data packets to a client. Use this instead of
        socket.send().
        """
        if conn not in [client[0] for client in self.clients]:
            raise ClientServerError("must be a valid, open client socket")
        packet = pickle.dumps(packet)
        for i in range(len(self.clients)):
            if conn is self.clients[i][0]:
                packet = encrypt(packet, self.clients[i][2])
                break
        packet = binascii.hexlify(packet)
        packet += " "
        conn.send(packet)

    def sendAll(self, packet):
        """Send data packets to all clients."""
        for client in self.clients:
            self.send(packet, client[0])
