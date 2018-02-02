"""Single-request network server classes.

Example:
    >>> from dtplib.requesthandler import RequestHandler, getResponse
    >>> server = RequestHandler(lambda request: request.swapcase())
    >>> server.start()
    >>> addr = server.getAddr()
    >>> getResponse("Hello", addr)
    'hELLO'
    >>> getResponse("World!", addr)
    'wORLD!'
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

class RequestHandlerError(Exception):
    pass

def getResponse(request, addr):
    """Send a request to a server and receive a response."""
    (host, port) = addr
    s = socket.socket(sockFamily, sockType)
    s.connect((host, port))
    cPub, cPriv = newKeyPair()
    sPub = ""
    while len(sPub) % buffersize == 0:
        chunk = s.recv(buffersize)
        if not chunk:
            s.close()
            raise RequestHandlerError("socket connection broken")
        sPub += chunk
    sPub = pickle.loads(sPub)
    cPub = pickle.dumps(cPub)
    if len(cPub) % buffersize == 0:
        cPub += " "
    s.send(cPub)
    s.recv(1)
    request = pickle.dumps(request)
    request = encrypt(request, sPub)
    request = binascii.hexlify(request)
    request += " "
    s.send(request)
    response = ""
    while True:
        chunk = s.recv(buffersize)
        if not chunk:
            s.close()
            raise RequestHandlerError("socket connection broken")
        response += chunk
        if " " in chunk:
            response = response[:response.index(" ")]
            break
    response = binascii.unhexlify(response)
    response = decrypt(response, cPriv)
    response = pickle.loads(response)
    return response

class RequestHandler:
    """Receive requests from clients and send responses back.

    'handler' is a function which takes the request argument and
    returns the response.
    Leave port = 0 for an arbitrary, unused port.
    Server.host can be changed to '', 'localhost', etc. before the
    start method is called.
    """
    def __init__(self, handler, port = 0):
        self.handler = handler
        self.host = socket.gethostname()
        self.port = port
        self.running = False
        self.serveThread = None
        self.sock = None
        self.clients = []

    def start(self):
        """Start the server."""
        if self.running:
            raise RequestHandlerError("server already running")
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
                        raise RequestHandlerError("socket connection broken")
                    cPub += chunk
            except RequestHandlerError:
                continue
            cPub = pickle.loads(cPub)
            conn.send(" ")
            self.clients.append((conn, addr, cPub, sPriv))
            t = threading.Thread(target = self.handle, args = (conn, addr, cPub, sPriv))
            t.daemon = True
            t.start()

    def handle(self, conn, addr, pubKey, privKey):
        request = ""
        while True:
            chunk = conn.recv(buffersize)
            if not chunk:
                self.remove(conn)
                return
            request += chunk
            if " " in chunk:
                request = request[:request.index(" ")]
                break
        request = binascii.unhexlify(request)
        request = decrypt(request, privKey)
        request = pickle.loads(request)
        response = self.handler(request)
        response = pickle.dumps(response)
        response = encrypt(response, pubKey)
        response = binascii.hexlify(response)
        response += " "
        conn.send(response)
        self.remove(conn)

    def remove(self, conn):
        """Remove a client."""
        conn.close()
        for i in range(len(self.clients)):
            if conn is self.clients[i][0]:
                del self.clients[i]

    def getAddr(self):
        """Get the address of the server in the format (host, port)."""
        return self.sock.getsockname()
