# coding: utf-8

import pbr.version

from cfgtree.models import ConfigBaseModel


def version():
    """Returns the PEP440 version of the cfgtree package"""
    return pbr.version.VersionInfo('cfgtree').release_string()


__all__ = [
    'version',
    'ConfigBaseModel',
]
