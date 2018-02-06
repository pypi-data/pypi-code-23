from __future__ import absolute_import, print_function, unicode_literals
"""
While technically this isn't "transferring" anything,
it's behaves the same way - create it, then put or get
multiple named files to or from it, so it's included in
here.

There's definitely an argument that it doesn't belong here...
(But you'd be wrong :)
"""

import ctxlogger
import datetime
import logging
import re

from io import BytesIO
from zipfile import ZipFile

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class zipfile(object):

    def __init__(self, initial_data=None, password=None):
        self._fh = BytesIO()
        if initial_data:
            self._fh.write(initial_data)
        self.password = password

    def __str__(self):
        return 'zip file'

    def put(self, data, name):
        # automatically try to format current timestamp in name
        # if no date format strings, will return original
        name = datetime.datetime.now().strftime(name)

        with ZipFile(self._fh, 'a') as zfh:
            zfh.writestr(name, data)

        return self._fh.getvalue()

    def get(self, pattern=r'.*'):

        data = {}
        pattern = re.compile(pattern)

        with ZipFile(self._fh, 'r') as zfh:
            for zfile in zfh.namelist():
                with ctxlogger.context('file', zfile):
                    if pattern.match(zfile):
                        logger.debug('Getting')
                        data[zfile] = zfh.read(zfile, pwd=self.password)
                    else:
                        logger.debug('Ignoring')

        return data
