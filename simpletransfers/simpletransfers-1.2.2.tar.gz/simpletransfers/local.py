from __future__ import absolute_import, print_function, unicode_literals
"""
"""

import contextlib
import ctxlogger
import datetime
#import inotify
import logging
import os
import re
import threading
import time

#from inotify import watcher

from . import TransferException

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class local(object):
    """
    Input from or output to a local directory
    """
    def __init__(self,
        source = '.',
        destination = '.',
        processed = None,
        perms = 0o600,
        debug = False
    ):
        """
        source - the directory to put or get files (default '.')
        destination - the directory to put files (default '.')
        processed - the directory to move collected files to (default None)
        perms - default permissions on created files (default '0600')
        debug - leave files as we process them? (default False)
        """
        self._source = os.path.abspath(source)
        self._destination = os.path.abspath(destination)
        if processed != None and not os.path.isabs(processed):
            self._processed = os.path.join(self._source, processed)
        else:
            self._processed = processed
        self._perms = perms
        self._debug = debug

    def __str__(self):
        return 'file://{}'.format(self._source or self.self._destination)

    def put(self, data, name):
        # automatically try to format current timestamp in name
        # if no date format strings, will return original
        name = datetime.datetime.now().strftime(name)

        with ctxlogger.context('address', self._destination):
            if not os.path.exists(self._destination):
                try:
                    os.makedirs(self._destination)
                except Exception as e:
                    ctxlogger.exception(
                        TransferException,
                        "Could not create: {}".format(str(e)),
                        orig_exc=e
                    )

            with ctxlogger.context('file', name):
                fullpath = os.path.join(self._destination, name)
                try:
                    with open(fullpath, 'w') as outfile:
                        outfile.write(data)
                except Exception as e:
                    ctxlogger.exception(
                        TransferException,
                        "Could not write data: {}".format(str(e)),
                        orig_exc=e
                    )
                try:
                    os.chmod(fullpath, self._perms)
                except Exception as e:
                    ctxlogger.exception(
                        TransferException,
                        "Could not set permissions: {}".format(str(e)),
                        orig_exc=e,
                    )

    def get(self, pattern = '.*'):
        """
        pattern - a regexp to pick remote files (default '.*')
        """
        data = {}

        with ctxlogger.context('address', self._source):
            if not os.path.exists(self._source):
                ctxlogger.exception(
                    TransferException, 'Path does not exist'
                )

            if not os.path.isdir(self._source):
                ctxlogger.exception(
                    TransferException, 'Path is not a directory'
                )

            pattern = re.compile(pattern)
            for f in os.listdir(self._source):
                with ctxlogger.context('file', f):

                    infile = os.path.join(self._source, f)
                    if pattern.match(f):
                        with open(infile) as indata:
                            data[f] = indata.read()
                    else:
                        logger.debug('Ignoring')
                        continue

                    if self._debug:
                        continue

                    if self._processed:
                        if not os.path.exists(self._processed):
                            try:
                                os.makedirs(self._processed)
                            except Exception as e:
                                ctxlogger.exception(
                                    TransferException,
                                    "Could not create {}: {}".format(
                                        self._processed,
                                        str(e)
                                    ),
                                    orig_exc=e
                                )

                        dest = os.path.join(self._processed, f)
                        logger.info(
                            'Moving to {}'.format(self._processed)
                        )

                        try:
                            os.rename(infile, dest)
                        except Exception as e:
                            ctxlogger.exception(
                                TransferException,
                                "Move failed: {}".format(str(e)),
                                orig_exc=e
                            )
                    else:
                        logger.debug('Deleting')
                        try:
                            os.unlink(infile)
                        except Exception as e:
                            ctxlogger.exception(
                                TransferException,
                                "Deletion failed: {}".format(str(e)),
                                orig_exc=e
                            )

        return data

## EXPERIMENTAL
#class local_dispatcher( threading.Thread ):
#    """
#    A threaded class that uses linux inotify support
#    to trigger events when local files are created.
#    """

#    def __init__( self, **kwargs ):
#        super().__init__( **kwargs )
#        self.watcher = watcher.Watcher()
#        self.handlers = {}

#    def register( self, path, callobj ):
#        if not path in self.handlers:
#            self.handlers[ path ] = []
#        self.handlers[ path ].append( callobj )
#        self.watcher.add( path, inotify.IN_CLOSE_WRITE )

#    def run( self ):
#        while True:
#            for event in self.watcher.read(0):
#                if event.path in self.handlers:
#                    for callobj in self.handlers[ event.path ]:
#                        callobj()
#            time.sleep(1)
