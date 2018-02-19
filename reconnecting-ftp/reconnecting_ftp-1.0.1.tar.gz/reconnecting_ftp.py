#!/usr/bin/env python3
"""
Classes helping inputries to download from FTP servers.
"""

import ftplib
from typing import Optional, Callable, TypeVar  # pylint: disable=unused-import


class Access:
    """
    Represents access information to the FTP server.
    """

    def __init__(self):
        self.hostname = ''
        self.port = 0
        self.user = ''
        self.password = ''


T = TypeVar('T')


class Client:
    """
    Reconnects to the FTP server if the connection has been closed. The current working directory is cached
    in between the sessions. When you re-connect, it changes first to the last available CWD.
    """

    def __init__(self,
                 hostname: str,
                 port: int,
                 user: str,
                 password: str,
                 max_reconnects: int = 10,
                 timeout: int = 10,
                 FTP=ftplib.FTP) -> None:
        # pylint: disable=too-many-arguments
        self.access = Access()
        self.access.hostname = hostname
        self.access.port = port
        self.access.user = user
        self.access.password = password

        self.connection = None  # type: Optional[ftplib.FTP]
        self.last_pwd = None  # type: Optional[str]
        self.max_reconnects = max_reconnects
        self.timeout = timeout

        self.FTP = FTP  # pylint: disable=invalid-name

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def connect(self) -> None:
        """ Connects to the server if not already connected. """
        if self.connection.file is None:
            self.connection = None

        if self.connection is None:
            conn_refused = None  # type: Optional[ConnectionRefusedError]
            try:
                self.connection = self.FTP(timeout=self.timeout)
                self.connection.connect(host=self.access.hostname, port=self.access.port)
                self.connection.login(user=self.access.user, passwd=self.access.password)
            except ConnectionRefusedError as err:
                conn_refused = err

            if conn_refused:
                raise ConnectionRefusedError("Failed to connect to {}:{}: {}".format(
                    self.access.hostname, self.access.port, conn_refused))

            if self.last_pwd is not None:
                self.connection.cwd(self.last_pwd)

    def close(self) -> None:
        """ Closes the connection. """
        if self.connection is not None:
            self.connection.close()

    def __wrap_reconnect(self, method: Callable[[ftplib.FTP], T]) -> T:
        """
        Dispatches the method to the connection and reconnects if needed.

        :param method: to be dispatched
        :return: response from the method
        """
        ftperr = None  # type: Optional[ftplib.error_temp]

        for _ in range(0, self.max_reconnects):
            try:
                if self.connection is None:
                    self.connect()

                assert self.connection is not None, "Expected connect() to either raise or create a connection"
                return method(self.connection)

            except ftplib.error_temp as err:
                self.connection.close()
                self.connection = None
                ftperr = err

        assert ftperr is not None, 'Expected either an error or a previous return'
        raise ftplib.error_temp(
            "Failed to execute a command on {}:{} after {} reconnect(s), the last error was: {}".format(
                self.access.hostname, self.access.port, self.max_reconnects, ftperr))

    def __wrap(self, method: Callable[[ftplib.FTP], T]) -> T:
        """
        Dispatches the method to the connection, reconnects if needed and observes the last working directory.

        :param method: to be dispatched
        :return: response from the method
        """
        resp = self.__wrap_reconnect(method=method)
        self.last_pwd = self.pwd()
        return resp

    def transfercmd(self, cmd, rest=None):
        """ See ftplib documentation """
        return self.__wrap(method=lambda conn: conn.transfercmd(cmd, rest))

    def retrbinary(self, cmd, callback, blocksize=8192, rest=None):
        """ See ftplib documentation """
        return self.__wrap(method=lambda conn: conn.retrbinary(cmd, callback, blocksize, rest))

    def retrlines(self, cmd, callback=None):
        """ See ftplib documentation """
        return self.__wrap(method=lambda conn: conn.retrlines(cmd, callback))

    def storbinary(self, cmd, fp, blocksize=8192, callback=None, rest=None):
        """ See ftplib documentation """
        # pylint: disable=invalid-name, too-many-arguments
        return self.__wrap(method=lambda conn: conn.storbinary(cmd, fp, blocksize, callback, rest))

    def storlines(self, cmd, fp, callback=None):
        """ See ftplib documentation """
        # pylint: disable=invalid-name
        return self.__wrap(method=lambda conn: conn.storlines(cmd, fp, callback))

    def acct(self, password):
        """ See ftplib documentation """
        return self.__wrap(method=lambda conn: conn.acct(password))

    def nlst(self, *args):
        """ See ftplib documentation """
        return self.__wrap(method=lambda conn: conn.nlst(*args))

    def dir(self, *args):
        """ See ftplib documentation """
        return self.__wrap(method=lambda conn: conn.dir(*args))

    def mlsd(self, path="", facts=None):
        """ See ftplib documentation """
        facts_lst = [] if facts is None else facts
        return self.__wrap(method=lambda conn: conn.mlsd(path, facts_lst))

    def rename(self, fromname, toname):
        """ See ftplib documentation """
        return self.__wrap(method=lambda conn: conn.rename(fromname, toname))

    def delete(self, filename):
        """ See ftplib documentation """
        return self.__wrap(method=lambda conn: conn.delete(filename))

    def cwd(self, dirname):
        """ See ftplib documentation """
        return self.__wrap(method=lambda conn: conn.cwd(dirname))

    def size(self, filename):
        """ See ftplib documentation """
        return self.__wrap(method=lambda conn: conn.size(filename))

    def mkd(self, dirname):
        """ See ftplib documentation """
        return self.__wrap(method=lambda conn: conn.mkd(dirname))

    def rmd(self, dirname):
        """ See ftplib documentation """
        return self.__wrap(method=lambda conn: conn.rmd(dirname))

    def pwd(self):
        """ See ftplib documentation """
        self.last_pwd = self.__wrap_reconnect(method=lambda conn: conn.pwd())
        return self.last_pwd

    def quit(self):
        """ See ftplib documentation """
        resp = self.__wrap(method=lambda conn: conn.quit())
        self.connection = None
        return resp
