#!/usr/bin/env python

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import json
import pickle

class FileExistsError(Exception):
    pass

def load_pickle(fp):
    """Returns python object from pickle at path fp"""
    with open(fp, 'rb') as f:
        return pickle.load(f)

def dump_pickle(pyobj, fp, overwrite=True):
    """Saves python object pyobj to path fp"""
    if not overwrite:
        import os.path
        if os.path.isfile(fp):
            raise FileExistsError(fp)
    with open(fp, 'wb') as f:
        pickle.dump(pyobj, f)


def load_json(fp):
    """Returns python object from json at path fp"""
    with open(fp, 'r') as f:
        return json.load(f)


def dump_json(pyobj, fp, overwrite=True, indent=None,
         sort_keys=False):
    """Saves python object pyobj to relative path filename

    Args:
        pyobj: a dict, list, or combination thereof
        fp: str, the filepath to save the json under
        overwrite: boolean, whether to overwrite an existing file.
                   This does not pass silently.
        indent: int, indent sent to the json.dumps() function
        sort_keys: boolean, whether to do so

    Returns:
        None

    Raises:
        AssertionError if overwrite=False and path exists
    """
    if not overwrite:
        import os.path
        if os.path.isfile(fp):
            raise FileExistsError(fp)
    with open(fp, 'w+') as f:
        f.write(json.dumps(pyobj, indent=indent, sort_keys=sort_keys))

