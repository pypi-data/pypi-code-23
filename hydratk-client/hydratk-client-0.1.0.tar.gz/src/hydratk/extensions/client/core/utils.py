# -*- coding: utf-8 -*-
"""Utilities

.. module:: client.core.utils
   :platform: Windows, Unix
   :synopsis: Utilities
.. moduleauthor:: Petr Rašek <bowman@hydratk.org>

"""

def fix_path(path):
    """Method fixes Windows path

    Args:
        none

    Returns:
        str

    """
    
    path = path.replace('\\', '/')
    return path
