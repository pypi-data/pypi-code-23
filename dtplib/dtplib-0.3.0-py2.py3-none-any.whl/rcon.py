"""Remote Console network server classes.

Example:
    >>> from dtplib.rcon import Server, Client
    >>> server = Server(lambda cmd: cmd.swapcase())
    >>> server.addUser("myusername", "password123")
    >>> server.start()
    >>> addr = server.getAddr()
    >>> client = Client()
    >>> client.login(addr, "myusername", "password123")
    >>> print client.send("Hello World!")
    hELLO wORLD!
    >>> print client.send("Foo Bar")
    fOO bAR
    >>> client.logout()
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
from .userdb import UserDB

buffersize = 4096
sockFamily = socket.AF_INET
sockType = socket.SOCK_STREAM

class RConError(Exception):
    pass

class Client:
    """Connect to a server with a valid username and password. Send
    commands and receive responses.

    Any Python object can be passed through the send method, as it
    supports serialization.
    """
    def __init__(self):
        self.sock = None
        self.host = None
        self.port = None
        self.running = False
        self.sock = None
        self.pubKey = None
        self.privKey = None

    def login(self, addr, username, password):
        """Log in to a server."""
        (host, port) = addr
        if self.running:
            raise RConError("already connected to server")
        self.sock = socket.socket(sockFamily, sockType)
        self.sock.connect((host, port))
        cPub, cPriv = newKeyPair()
        sPub = ""
        while len(sPub) % buffersize == 0:
            chunk = self.sock.recv(buffersize)
            if not chunk:
                self.disconnect()
                raise RConError("socket connection broken")
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
        if not self.send((username, password)):
            self.logout()
            raise RConError("login failed")
        self.host = host
        self.port = port

    def logout(self):
        """Log out of the server."""
        self.running = False
        self.sock.close()
        self.sock = None
        self.pubKey = None
        self.privKey = None

    def getAddr(self):
        """Get the address of the client in the format (host, port)."""
        return self.sock.getsockname()

    def getServerAddr(self):
        """Get the address of the server in the format (host, port)."""
        return self.sock.getpeername()

    def send(self, command):
        """Send commands to the server and receive responses."""
        if not self.running:
            raise RConError("not connected to a server")
        command = pickle.dumps(command)
        command = encrypt(command, self.pubKey)
        command = binascii.hexlify(command)
        command += " "
        self.sock.send(command)
        result = ""
        while True:
            chunk = self.sock.recv(buffersize)
            if not chunk:
                self.disconnect()
                raise RConError("socket connection broken")
            result += chunk
            if " " in chunk:
                result = result[:result.index(" ")]
                break
        result = binascii.unhexlify(result)
        result = decrypt(result, self.privKey)
        result = pickle.loads(result)
        return result

class Server:
    """Continuously serve clients with valid login information.

    'handler' is a function which takes the command argument. If
    something is returned, it will be sent to the client.
    Leave port = 0 for an arbitrary, unused port.
    'dbFileName' is the file in which the user database is stored.
    """
    def __init__(self, handler, port=0, dbFileName="users.db"):
        self.handler = handler
        self.sock = None
        self.host = socket.gethostname()
        self.port = port
        self.running = False
        self.serveThread = None
        self.sock = None
        self.clients = []
        self.users = UserDB(dbFileName)

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
                        self.disconnect()
                        raise RConError("socket connection broken")
                    cPub += chunk
            except RConError:
                continue
            cPub = pickle.loads(cPub)
            conn.send(" ")
            login = ""
            try:
                while True:
                    chunk = conn.recv(buffersize)
                    if not chunk:
                        conn.close()
                        raise RConError("socket connection broken")
                    login += chunk
                    if " " in chunk:
                        login = login[:login.index(" ")]
                        break
            except RConError:
                continue
            login = binascii.unhexlify(login)
            login = decrypt(login, sPriv)
            login = pickle.loads(login)
            isValid = self.users.validLogin(*login)
            valid = pickle.dumps(isValid)
            valid = encrypt(valid, cPub)
            valid = binascii.hexlify(valid)
            valid += " "
            conn.send(valid)
            if isValid:
                self.clients.append((conn, addr, cPub, sPriv))
                t = threading.Thread(target = self.handle, args = (conn, addr, cPub, sPriv))
                t.daemon = True
                t.start()
            else:
                conn.close()

    def handle(self, conn, addr, pubKey, privKey):
        while True:
            command = ""
            while True:
                chunk = conn.recv(buffersize)
                if not chunk:
                    self.remove(conn)
                    return
                command += chunk
                if " " in chunk:
                    command = command[:command.index(" ")]
                    break
            command = binascii.unhexlify(command)
            command = decrypt(command, privKey)
            command = pickle.loads(command)
            result = self.handler(command)
            result = pickle.dumps(result)
            result = encrypt(result, pubKey)
            result = binascii.hexlify(result)
            result += " "
            conn.send(result)

    def remove(self, conn):
        """Remove a client."""
        conn.close()
        for i in range(len(self.clients)):
            if conn is self.clients[i][0]:
                del self.clients[i]

    def getAddr(self):
        """Get the address of the server in the format (host, port)."""
        return self.sock.getsockname()

    def addUser(self, username, password, data=None):
        """Create a new user with specified username, password, and
        data (optional).
        """
        self.users.new(username, password, data)

    def delUser(self, username):
        """Delete a user from the database."""
        self.users.remove(username)

    def getUsers(self):
        """Get a list of all users in the database."""
        return self.users.getUsers()

    def getUserData(self, username, password):
        """Get the data of a user. If no data exists, a NoneType is
        returned.
        """
        return self.users.getData(username, password)

    def setUserData(self, username, password, data):
        """Set the data of a user."""
        self.users.setData(username, password, data)

    def delDB(self):
        """Delete the database."""
        self.users.delete()
        self.users = None
