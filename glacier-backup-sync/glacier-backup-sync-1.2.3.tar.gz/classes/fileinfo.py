"""Provides a container object for misc. file information"""
from datetime import datetime
import os

class FileInfo(object):
    """Provides a container object for misc. file information"""
    path = ""
    name = ""
    created = 0

    def __init__(self, path, created):
        self.path = path
        self.name = os.path.basename(path)
        self.created = datetime.fromtimestamp(created)

    def __repr__(self):
        return '<%s: %s %s>' % (self.__class__.__name__, self.path,
                                self.created.strftime('%Y-%m-%d %H:%M:%S'))
