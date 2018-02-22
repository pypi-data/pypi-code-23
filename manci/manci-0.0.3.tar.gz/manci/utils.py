from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from datetime import datetime
from itertools import izip_longest, imap
import os
from os.path import splitext
import sys


__all__ = [
    'dump',
    'grouper',
    'initalise_dirac',
]


def initalise_dirac():
    for module in ['XRootD', 'LHCbDIRAC', 'DIRAC']:
        if module in sys.modules:
            print('WARNING: urban_baracle should be imported before', module)
            print('Access to DIRAC may not function correctly')

    try:
        from LHCbDIRAC.DataManagementSystem.Client.DMScript import Script  # NOQA
    except ImportError:
        raise ImportError('Unable to import LHCbDIRAC, try using "lb-run LHCbDIRAC/prod python -m manci ..."')

    argv, sys.argv = sys.argv, []
    Script.parseCommandLine()
    os.environ['XrdSecPROTOCOL'] = 'gsi,unix,krb5'
    sys.argv = argv
    # TODO Check for grid proxy


def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3) --> ABC DEF G
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx
    args = [iter(iterable)] * n
    return imap(lambda x: list(filter(bool, x)),
                izip_longest(fillvalue=fillvalue, *args))


def dump(obj, filename):
    """Dump an object to a file

    Dumps obj to filename, with automated detection for the filetype and
    encoding of datetime objects.
    """
    _, ext = splitext(filename)

    encoded_obj = {
        lfn: {k: (v.isoformat() if isinstance(v, datetime) else v)
              for k, v in metadata.items()}
        for lfn, metadata in obj.items()
    }

    if ext == '.json':
        import json
        with open(filename, 'wt') as fp:
            json.dump(encoded_obj, fp, default=make_object_serialisable)
    elif ext == '.yaml':
        import yaml
        with open(filename, 'wt') as fp:
            yaml.dump(encoded_obj, fp, default=make_object_serialisable)
    else:
        raise NotImplementedError('Unrecognised file extension ' + ext)


def make_object_serialisable(obj):
    from .structures import Replica

    if isinstance(obj, Replica):
        return {
            'SE': obj._se,
            'PFN': obj._pfn,
        }
    else:
        raise NotImplementedError(obj.__class__)
