from __future__ import absolute_import, print_function, unicode_literals
"""
"""

import contextlib
import ctxlogger
import datetime
import os
import logging
import re
import ssl
import sys
import ftplib

from io import BytesIO

from . import TransferException

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class ftp(object):

    _conn = None
    _host = ''
    _port = 21
    _user = ''
    _password = ''
    _source = '.'
    _destination = '.'
    _processed = ''
    _timeout = 30
    _ftps = False
    _debug = False
    _file_contents = ''

    """
    Basic (non-secure) FTP transport
    """
    def __init__(self,
        host,
        user,
        password,
        port = 21,
        source = '.',
        destination = '.',
        processed = None,
        debug = False,
        timeout = 30,
        ftps = False,
    ):
        """
        host - the server name
        port - the server port (default 21)
        user - the FTP username
        password - the FTP password
        source - the remote directory to get files (default '.')
        destination - the remote directory to put files (default '.')
        processed - the remote directory to move files to
            after being fetched (optional)
        debug - leave remote files when fetched (default False)
        timeout - timeout wait period in seconds (default 30)
        """
        self._address = 'ftp://{}:{}/{}'.format(host, port, destination)

        self._host = host
        self._port = port
        self._timeout = timeout
        self._user = user
        self._password = password

        self._source = source
        self._destination = destination
        self._processed = processed

        self._ftps = ftps

        self._debug = debug

    def __str__(self):
        return self._address

    def _connect(self):
        if self._conn != None:
            return

        if not self._ftps:
            self._conn = ftplib.FTP()
        else:
            self._conn = ftplib.FTP_TLS()
            self._conn.ssl_version = ssl.PROTOCOL_SSLv23

        with ctxlogger.context('address', self._address):
            logger.info('Connecting')
            try:
                self._conn.connect(self._host, self._port, self._timeout)
                self._conn.login(self._user, self._password)
            except Exception as e:
                ctxlogger.exception(TransferException, str(e), orig_exc = e)

        if self._ftps:
            self._conn.prot_p()

    def put(self, data, name, rename = True):
        # automatically try to format current timestamp in
        # if no date format strings, will return original
        name = datetime.datetime.now().strftime( name )

        self._connect()

        with contextlib.nested(
            ctxlogger.context('address', self._address),
            ctxlogger.context('file', name)
        ):

            outfn = os.path.join(self._destination, name)

            logger.info('Putting')
            if rename:
                tmpfn = '{}.uploading'.format(outfn)

                try:
                    # write file to temporary name to minimise chance
                    # of being picked up mid-upload
                    self._conn.storbinary(
                        'STOR {}'.format(tmpfn),
                        BytesIO(data)
                    )

                    # now rename file (an atmoic op) once we're done
                    logger.debug('Renaming')
                    self._conn.rename(tmpfn, outfn)
                except Exception as e:
                    ctxlogger.exception(TransferException, str(e), orig_exc = e)
            else:
                try:
                    self._conn.storbinary(
                        'STOR {}'.format(outfn),
                        BytesIO(data)
                    )
                except Exception as e:
                    ctxlogger.exception(TransferException, str(e))

    def get(self, pattern = '.*'):
        """
        pattern - a regexp to pick remote files (default '.*')
        """
        data = {}

        self._connect()

        with ctxlogger.context('address', self._address):

            pattern = re.compile(pattern)

            for f in self._conn.nlst(self._source):
                with ctxlogger.context('file', f):

                    remotef = os.path.basename(f.replace('\\', '/'))
                    if not pattern.match(remotef):
                        logger.debug('Ignoring, does not match pattern')
                        continue

                    logger.info('Getting')

                    self._file_contents = ''
                    try:
                        self._conn.retrbinary(
                            'RETR {}'.format(f), self._download
                        )
                    except Exception as e:
                        ctxlogger.exception(
                            TransferException, str(e), orig_exc = e
                        )

                    data[remotef] = self._file_contents

                    if not self._debug:
                        if self._processed:
                            logger.info(
                                'Moving to {}'.format(self._processed)
                            )

                            destp = os.path.join(self._processed, remotef)
                            try:
                                self._conn.rename(f, destp)
                            except Exception as e:
                                ctxlogger.exception(
                                    TransferException, str(e), orig_exc = e
                                )
                        else:
                            logger.info('Deleting')
                            try:
                                self._conn.delete(f)
                            except Exception as e:
                                ctxlogger.exception(
                                    TransferException, str(e), orig_exc = e
                                )

        return data

    def _download(self, data):
        self._file_contents += data
