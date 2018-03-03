#!/usr/bin/env python3
import argparse
import datetime
from functools import lru_cache
import logging
import os.path
import errno
import stat

from fuse import FUSE, FuseOSError, Operations, LoggingMixIn
import requests_cache

from opengrokfs.opengrok import File, OpenGrok


class OpenGrokFs(LoggingMixIn, Operations):
    def __init__(self, opengrok):
        self.opengrok = opengrok
        self.pseudofile = '.opengrokfs'
        self.files = {}
        self.data = {}
        self.fd = 0
        self.list = {}
        self.today = datetime.datetime.today()
        self.files['/'] = File('', date=self.today, dir=True, size=0)

    @lru_cache(maxsize=4096)
    def _get_file(self, path):
        self._readdir(os.path.dirname(path) + '/')
        try:
            file = self.files[path]
        except KeyError:
            raise FuseOSError(errno.ENOENT)

        return file

    def getattr(self, path, fh=None):
        file = self._get_file(path)

        info = {
            'st_mode': 0o644 | (stat.S_IFDIR if file.dir else stat.S_IFREG),
            'st_ctime': file.date.timestamp(),
            'st_nlink': 2 if file.dir else 1,
            'st_size': 0 if file.dir else file.size,
        }

        info['st_mtime'] = info['st_atime'] = info['st_ctime']
        return info

    def _get_projects(self):
        return [f.name for f in self._readdir('/') if f.dir]

    @lru_cache(maxsize=4096)
    def _read(self, path):

        parts = path.strip('/').split('/')
        if self.pseudofile and parts[-1] == self.pseudofile:
            if len(parts) == 1:
                strip = '/'
                projects = self._get_projects()
            else:
                projects = [parts[0]]
                strip = '/' + '/'.join(parts[:-1]) + '/'

            args = ['--url', self.opengrok.url,
                    '--strip', strip]
            for project in projects:
                args.extend(('--project', project))

            data = '\n'.join(args).encode('utf-8')
        else:
            data = self.opengrok.get(path).encode('utf-8')

        file = self._get_file(path)
        if len(data) < file.size:
            # file.size reports larger sizes to compensate rounding in the OpenGrok UI,
            # fill the remaining bytes with whitespace instead of leaving it unfilled
            # to print junk and errors in vim and gedit due to \0 bytes
            adjust = file.size - len(data)
            data += ((adjust - 1) * ' ' + '\n').encode('utf-8')

        return data

    def read(self, path, size, offset, fh):
        data = self._read(path)
        return data[offset:offset + size]

    @lru_cache(maxsize=4096)
    def _readdir(self, path):
        files = self.opengrok.list(path)

        if self.pseudofile:
            files.append(File(self.pseudofile, date=self.today, size=1024))

        for file in files:
            self.files[path + file.name] = file

        return files

    def readdir(self, path, fh):
        if not path.endswith('/'):
            path += '/'

        return ['.'] + [f.name for f in self._readdir(path)]


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--cache', nargs='?', const='opengrokfs',
                        help="Cache network requests persistently")
    parser.add_argument('url')
    parser.add_argument('mountpoint')

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    if args.cache:
        requests_cache.install_cache(args.cache)

    FUSE(OpenGrokFs(OpenGrok(args.url)), args.mountpoint, foreground=True)


if __name__ == '__main__':
    main()
