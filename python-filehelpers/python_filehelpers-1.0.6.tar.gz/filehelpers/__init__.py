"""
    file helpers
    ~~~~~~~~~~~~~

    A set of various filesystem helpers.

    :copyright: (c) 2016 by Dusty Gamble.
    :license: MIT, see LICENSE for more details.
"""

__version__ = '1.0.6'



import os
import shutil
import hashlib
from natsort import natsorted


def file_extension(filepath):
    filename, file_extension = os.path.splitext(filepath)
    return file_extension


def absolute_delete(filepath):
    try:
        os.remove(filepath)
    except OSError:
        try:
            shutil.rmtree(filepath, ignore_errors=True)
        except OSError:
            pass


def get_dir_contents_filepaths(dirname):
    files = []
    dirname += '/'

    try:
        for filename in os.listdir(dirname):
            filepath = os.path.normpath(dirname + filename)
            files.append(filepath)
    except OSError:
        pass

    return files


def delete_dir_extra_files(dirname, needs_files):
    has_files = [os.path.normpath(f) for f in get_dir_contents_filepaths(dirname)]
    needs_files = [os.path.normpath(f) for f in needs_files]

    extra_files = set(has_files) - set(needs_files)

    for filepath in extra_files:
        absolute_delete(filepath)

    return extra_files


def get_dir_symlinks(dirname, recursive=False):
    # Reference: http://stackoverflow.com/questions/6184849
    symlinks = {}
    for filepath in get_dir_contents_filepaths(dirname, ):
        try:
            if os.path.islink(filepath):
                symlinks[filepath] = os.path.realpath(filepath)
        except OSError:
            # If the file was deleted before we inspected it, don't bother.
            pass

    return symlinks


def md5_file(filepath):
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def get_subdirs(root_dirpath):
    dirs = []
    root_dirpath = os.path.realpath(root_dirpath) + '/'
    try:
        for filename in os.listdir(root_dirpath):
            filepath = root_dirpath + filename
            filepath = os.path.normpath(filepath)
            if os.path.isdir(filepath):
                dirs.append(filepath)
        dirs = natsorted(dirs)
    except FileNotFoundError:
        pass
    return dirs


def get_dir_files(dirname, *, extensions=None):
    """
    :param str dirname: path to directory
    :param list extensions: list of extensions to look for
    :return: a list of filepaths
    """
    filepaths = []

    try:
        for filename in os.listdir(dirname):
            if extensions and os.path.splitext(filename)[1].lower() not in extensions:
                continue
            filepath = os.path.join(dirname, filename)
            filepath = os.path.normpath(filepath)
            filepaths.append(filepath)
        filepaths = natsorted(filepaths)
    except FileNotFoundError:
        pass
    return filepaths


def least_common_directory(files):
    '''
    Finds the closest directory that all files share.
    '''
    for filepath in files:
        pass
    raise NotImplementedError
