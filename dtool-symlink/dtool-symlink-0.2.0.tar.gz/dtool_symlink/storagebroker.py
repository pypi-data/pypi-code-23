"""Symbolic link storage broker module."""

import os

from dtoolcore.storagebroker import DiskStorageBroker


class SymLinkStorageBroker(DiskStorageBroker):
    """SymLinkStorageBroker class."""

    key = "symlink"

    def __init__(self, uri, config_path=None):
        super(SymLinkStorageBroker, self).__init__(uri, config_path)
        self._essential_subdirectories = [
            self._dtool_abspath,
            self._overlays_abspath
        ]

    def create_structure(self):
        super(SymLinkStorageBroker, self).create_structure()
        try:
            if not os.path.isdir(self.symlink_path):
                message = "No such directory: '{}'".format(self.symlink_path)  # NOQA
                raise(IOError(message))

        except AttributeError:
            message = "The 'symlink_path' attribute needs to be added to the 'SymLinkStorageBroker' instance before calling the 'create_structure' method"  # NOQA
            raise(AttributeError(message))
        os.symlink(self.symlink_path, self._data_abspath)

    def put_item(self, fpath, relpath):
        raise(NotImplementedError())
