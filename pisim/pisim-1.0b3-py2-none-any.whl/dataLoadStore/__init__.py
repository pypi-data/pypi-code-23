# -*- coding: utf-8 -*-

"""APIs to load/store info descriptors handled by the app.

List of sub-packages
====================

.. autosummary::
   :toctree: _autosummary

   common
   inflazione
   dipendente
   pensione
   salario
   fondoPensione.base
   fondoPensione.accumulo
   fondoPensione.rendita
   reports
   factoryDescs

Module's members
================

"""

from appdirs import AppDirs
import os

#: Root dir where all app-related data are saved.
configRootDir = AppDirs(appname='pisim', appauthor='').user_data_dir


def checkRootDir():
    """Check the presence of the data dir.

    Data dir is stored in :py:data:`configRootDir`.
    It's created if not existing.
    """
    try:
        os.makedirs(configRootDir)
    except os.error:
        # Exception raised when leaf dir already exists or dir
        # cannot be created. Supposing latter never happens,
        # code goes here because of the former.
        # If so exception can be silently ignored.
        pass
