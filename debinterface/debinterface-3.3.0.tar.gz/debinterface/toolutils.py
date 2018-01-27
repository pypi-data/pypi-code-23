# -*- coding: utf-8 -*-
from __future__ import print_function, with_statement, absolute_import
import os
import stat
import tempfile
from contextlib import contextmanager
import subprocess


def safe_subprocess(command_array):
    """Executes shell command. Do not raise

        Args:
            command_array (list): ideally an array of string elements, but
                may be a string. Will be converted to an array of strings

        Returns:
            bool, str: True/False (command succeeded), command output
    """

    try:
        # Ensure all args are strings
        if isinstance(command_array, list):
            command_array_str = [str(x) for x in command_array]
        else:
            command_array_str = [str(command_array)]
        return True, subprocess.check_output(command_array_str,
                                             stderr=subprocess.STDOUT)
    except OSError as ex:
        return False, ex.__str__()
    except subprocess.CalledProcessError as ex:
        return False, ex.output


@contextmanager
def atomic_write(filepath):
    """
        Writeable file object that atomically updates a file
            (using a temporary file).

        Args:
            filepath (str): the file path to be opened
    """
    # Put tmp file to same directory as target file, to allow atomic move
    realpath = os.path.realpath(filepath)
    tmppath = os.path.dirname(realpath)
    with tempfile.NamedTemporaryFile(dir=tmppath, delete=False) as tempf:
        with open(tempf.name, mode='w+') as tmp:
            yield tmp
            tmp.flush()
            os.fsync(tmp.fileno())
        os.rename(tempf.name, realpath)
        os.chmod(realpath,
                 stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)
