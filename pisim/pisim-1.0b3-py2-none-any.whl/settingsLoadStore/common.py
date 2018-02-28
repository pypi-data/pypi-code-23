# -*- coding: utf-8 -*-

"""Module implementing I/O APIs for app settings.

Settings storage is based on Python's shelve package.

Module's content
================

"""

import shelve
import pickle
import os
from ..dataLoadStore import configRootDir


class SettingsLoadStoreError(Exception):
    """Base module's exception class."""

    def __str__(self):
        """Error message."""
        return "Errore generico di database nell'accesso ai settings"


class SettingsIo:
    """Settinge I/O class."""

    def __init__(self):
        """Constructor."""
        #: On-disk repository descriptor.
        try:
            self._db = shelve.open(
                os.path.join(configRootDir, 'settings'),
                protocol=pickle.HIGHEST_PROTOCOL)
        except IOError:
            raise SettingsLoadStoreError

    def load(self, sName):
        """Load the setting.

        :param str sName: setting name.
        :returns: The loaded setting, if found, None otherwise.
        :rtype: setting-dependent.
        """
        try:
            return self._db[sName]
        except KeyError:
            return None

    def save(self, s, sName):
        """Dump the setting on file.

        :param s: The setting to be saved.
        :param str sName: Setting name.
        """
        self._db[sName] = s

    def delete(self, sName):
        """Delete the setting.

        :param str sName: The name of the setting to remove.
        """
        try:
            del self._db[sName]
        except KeyError:
            pass
