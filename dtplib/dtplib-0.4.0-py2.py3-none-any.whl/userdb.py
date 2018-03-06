"""User database classes.

Example:
    >>> from dtplib.userdb import UserDB
    >>> database = UserDB("users.db")
    >>> database.new("myname", "password123")
    >>> database.validLogin("myname", "password123")
    True
    >>> database.validLogin("wrongname", "wrongpassword")
    False
    >>> database.getUsers()
    ['myname']
    >>> database.getData("myname")
    None
    >>> database.setData("myname", "password123", ("foo", "bar"))
    >>> database.getData("myname", "password123")
    ('foo', 'bar')
    >>> database.remove("myname")
    >>> database.getUsers()
    []
    >>> database.delete()
"""

import os
try:
    import cPickle as pickle
except ImportError:
    import pickle
from .encrypt import hashText, passwordToKey, symmetricEncrypt, symmetricDecrypt

class UserDBError(Exception):
    pass

class UserDB:
    """Create user databases with hashed passwords.

    'filename' is the file in which the user database is stored.
    """
    def __init__(self, filename):
        self.filename = filename
        if os.path.isfile(filename):
            with open(filename, "rb") as f:
                try:
                    self.users = pickle.load(f)
                except:
                    self.users = {}
        else:
            open(filename, "wb").close()
            self.users = {}

    def validLogin(self, username, password):
        """Check if a username password combination is valid."""
        if username not in self.users:
            return False
        password = password.encode()
        hashedPassword = hashText(password)
        return self.users[username][0] == hashedPassword

    def new(self, username, password, data=None):
        """Create a new user with specified username, password, and
        data (optional).
        """
        if username in self.users:
            raise UserDBError("user already exists")
        password = password.encode()
        hashedPassword = hashText(password)
        data = pickle.dumps(data)
        data = symmetricEncrypt(data, passwordToKey(password))
        self.users[username] = [hashedPassword, data]
        open(self.filename, "wb").close()
        with open(self.filename, "wb") as f:
            pickle.dump(self.users, f)

    def remove(self, username):
        """Delete a user from the database."""
        if username not in self.users:
            raise UserDBError("user does not exist")
        self.users.pop(username)
        open(self.filename, "wb").close()
        with open(self.filename, "wb") as f:
            pickle.dump(self.users, f)

    def getUsers(self):
        """Get a list of all users in the database."""
        return self.users.keys()

    def getData(self, username, password):
        """Get the data of a user."""
        if username not in self.users:
            raise UserDBError("user does not exist")
        if not self.validLogin(username, password):
            raise UserDBError("invalid login")
        data = symmetricDecrypt(self.users[username][1], passwordToKey(password))
        data = pickle.loads(data)
        return data

    def setData(self, username, password, data):
        """Set the data of a user."""
        if username not in self.users:
            raise UserDBError("user does not exist")
        if not self.validLogin(username, password):
            raise UserDBError("invalid login")
        data = pickle.dumps(data)
        self.users[username][1] = symmetricEncrypt(data, passwordToKey(password))
        open(self.filename, "wb").close()
        with open(self.filename, "wb") as f:
            pickle.dump(self.users, f)

    def delete(self):
        """Delete the database."""
        os.remove(self.filename)
        self.users = None
