from __future__ import absolute_import, print_function, unicode_literals
"""
"""

import contextlib
import ctxlogger
import datetime
import logging
import os
import paramiko
import re

from . import TransferException

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class sftp(object):

    _conn = None
    _user = ''
    _password = ''
    _host = ''
    _port = 22
    _source = '.'
    _destination = '.'
    _processed = ''
    _debug = False
    _permissions = 0o777

    """
    Secure (via SSH) FTP
    """
    def __init__(self,
        host,
        user,
        password,
        port = 22,
        source = '.',
        destination = '.',
        processed = None,
        debug = False,
        permissions = None,
    ):
        """
        host - the server name
        user - the SFTP username
        password - the SFTP password
        port - the server port (default 22)
        source - the remote directory to look for files (default '.')
        destination - the remote directory to put files (default '.')
        processed - the remote directory to move fetched files to (optional)
        debug - leave remote files after fetching (default False)
        permissions - chmod mask for uploaded files (default None)
        """
        self._address = 'sftp://{}:{}/{}'.format(
            self._host, self._port, self._destination
        )

        self._user = user
        self._password = password
        self._host = host
        self._port = port

        self._source = source
        self._destination = destination
        self._processed = processed

        self._debug = debug
        self._permissions = permissions

    def __str__(self):
        return self._address

    def put(self, data, name, rename = True):
        # automatically try to format current timestamp in name
        # if no date format strings, will return original
        name = datetime.datetime.now().strftime(name)

        with ctxlogger.context('address', self._address):
            self.connect()

            with ctxlogger.context('file', name):

                outfn = os.path.join(self._destination, name)

                logger.info('Putting')

                if not rename:
                    try:
                        rfh = self._conn.file(outfn, 'wb')
                        rfh.write(data)
                        rfh.close()
                    except Exception as e:
                        ctxlogger.exception(
                            TransferException,
                            "Could not write data: {}".format(str(e)),
                            orig_exc = e,
                        )
                else:
                    tmpfn = '{}.uploading'.format(outfn)

                    # write date to a temporary filename first
                    # to minimise risk of partially sent file
                    # being picked up
                    try:
                        rfh = self._conn.file(tmpfn, 'wb')
                        rfh.write(data)
                        rfh.close()
                    except Exception as e:
                        ctxlogger.exception(
                            TransferException,
                            "Could not write data: {}".format(str(e)),
                            orig_exc = e
                        )

                    # then rename once we're done (an atomic op)
                    logger.debug('Renaming temporary file')
                    try:
                        self._conn.rename(tmpfn, outfn)
                    except Exception as e:
                        ctxlogger.exception(
                            TransferException,
                            "Could not rename file: {}".format(str(e)),
                            orig_exc=e
                        )

                if self._permissions:
                    try:
                        self._conn.chmod(outfn, self._permissions)
                    except Exception as e:
                        ctxlogger.exception(
                            TransferException,
                            "Could not set permissions to {}: {}".format(
                                self._permissions, str(e),
                            ),
                            orig_exc=e
                        )

    def get(self, pattern = '.*'):
        """
        pattern - a regexp to pick remote files (default '.*')
        """
        data = {}

        with ctxlogger.context('address', self._address):
            self.connect()
            pattern = re.compile(pattern)

            for remotef in self._conn.listdir(self._source):
                with ctxlogger.context('file', remotef):

                    if not pattern.match(remotef):
                        logger.debug('Ignoring')
                        continue

                    logger.info('Getting')

                    remotep = os.path.join(self._source, remotef)
                    try:
                        rfh = self._conn.file(remotep, 'rb')
                        data[ remotef ] = rfh.read()
                        rfh.close()
                    except Exception as e:
                        ctxlogger.exception(
                            TransferException,
                            "Could not read data: {}".format(str(e)),
                            orig_exc = e
                        )

                    if not self._debug:
                        if self._processed:
                            logger.debug(
                                'Moving to {}'.format(self._processed)
                            )

                            destp = os.path.join(self._processed, remotef)
                            try:
                                self._conn.rename(remotep, destp)
                            except Exception as e:
                                ctxlogger.exception(
                                    TransferException,
                                    'Could not move: {}'.format(str(e)),
                                    orig_exc=e
                                )
                        else:
                            logger.debug('Deleting')
                            try:
                                self._conn.remove(remotep)
                            except Exception as e:
                                ctxlogger.exception(
                                    TransferException,
                                    "Could not delete: {}".format(str(e)),
                                    orig_exc=e
                                )

        return data

    def connect(self):
        if self._conn:
            return

        try:
            transport = paramiko.Transport(
                '{}:{}'.format(self._host, self._port)
            )
            transport.connect(
                username=self._user, password=self._password
            )
            self._conn = paramiko.SFTPClient.from_transport(transport)
        except Exception as e:
            ctxlogger.exception(
                TransferException,
                "Could not connect: {}".format(str(e)),
                orig_exc=e
            )
