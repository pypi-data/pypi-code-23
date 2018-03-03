""" This module contains helper functions for manipulating files """
import os
import shutil
import hashlib
import inspect
import json
from glob import glob

if os.name == 'posix':  # mac
    TRASH_PATH = '/'.join(os.getcwd().split('/')[:3] + ['.Trash'])
else:
    TRASH_PATH = '.'  # todo implement for other os


def mkdir(path):
    if not isinstance(path, str):
        path = str(path)
    if os.path.exists(os.path.abspath(path)):
        return
    path_directories = os.path.abspath(path).replace('\\', '/').split('/')
    full_path = ''
    for directory in path_directories[1:]:
        full_path += '/' + directory
        if not os.path.exists(full_path):
            os.mkdir(full_path)
    assert os.path.exists(path), "Failed to make directory: %s" % path


def mkdir_for_file(path):
    path = path if os.path.isdir(path) else os.path.dirname(path)
    mkdir(path)


def file_list(file_wildcard = '*.*', path=None):
    frm = inspect.currentframe().f_back
    path = path or os.path.split(frm.f_code.co_filename)[0]
    ret = []
    for root, subs, files in os.walk(os.path.abspath(path)):
        ret += glob(os.path.join(root, file_wildcard))
    return ret


def clear_path(path):
    """
        This will move a path to the Trash folder
    :param path: str of the path to remove
    :return:     None
    """
    from time import time
    if not os.path.exists(path):
        return
    if TRASH_PATH == '.':
        shutil.rmtree(path, ignore_errors=True)
    else:
        shutil.move(path, '%s/%s_%s' % (
            TRASH_PATH, os.path.basename(path), time()))


def get_filename(filename, trash=False):
    if trash:
        filename = os.path.join(TRASH_PATH, filename)

    full_path = os.path.abspath(filename)
    if not os.path.exists(os.path.split(full_path)[0]):
        mkdir(os.path.split(full_path)[0])
    if os.path.exists(full_path):
        os.remove(full_path)
    return full_path


def sync_folder(source_folder, destination_folder, soft_link=True,
                only_files=False):
    clear_path(destination_folder)
    mkdir(destination_folder)
    for root, subs, files in os.walk(source_folder):
        for file in files:
            file = os.path.join(root, file)
            copy_file(file, file.replace(source_folder, destination_folder),
                      soft_link=bool(soft_link))
        if only_files:
            break
        for sub in subs:
            mkdir(sub.replace(source_folder, destination_folder))


def _md5_of_file(sub_string):
    """
        This will return the md5 of the file in sub_string
    :param sub_string: str of the path or relative path to a file
    :return: str
    """
    md5 = hashlib.md5()
    file_path = sub_string
    if not os.path.exists(file_path):
        file_path = os.path.join(os.environ['CAFE_DATA_DIR_PATH'], file_path)
    if not os.path.exists(file_path):
        file_path = file_path.replace(' ', '_')
    assert (os.path.exists(file_path)), "File %s doesn't exist" % file_path
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            md5.update(chunk)
    return md5.hexdigest()


def read_local_file(filename):
    """
        This will read a file in the same directory as the calling function
    :param filename: str of the basename of the file
    :return: str of the content of the file
    """
    frm = inspect.currentframe().f_back
    if frm.f_code.co_name == 'run_code':
        frm = frm.f_back
    path = os.path.split(frm.f_code.co_filename)[0]
    return read_file(os.path.join(path, filename))


def relative_path(sub_directory='', function_index=1):
    """
        This will return the file relative to this python script
    :param subd_irectory:  str of the relative path
    :param function_index: int of the number of function calls to go back
    :return:               str of the full path
    """
    frm = inspect.currentframe()
    for i in range(function_index):
        frm = frm.f_back
    if frm.f_code.co_name == 'run_code':
        frm = frm.f_back

    if not isinstance(sub_directory, list):
        sub_directory = sub_directory.replace('\\','/').split('/')

    path = os.path.split(frm.f_code.co_filename)[0]
    if sub_directory:
        path = os.path.abspath(os.path.join(path, *sub_directory))
    return path


def mdate(filename):
    """
    :param filename: str of the file
    :return: float of the modified date of the file
    """
    return os.stat(filename).st_mtime


def read_file(full_path):
    assert os.path.exists(full_path), "File '%s' doesn't exist" % full_path
    with open(full_path, 'r') as f:
        ret = f.read()
    if full_path.endswith('.json'):
        try:
            json.loads(ret)
        except Exception:
            raise Exception("%s is not valid JSON" % full_path)
    return ret


def copy_file(source_file, destination_file, soft_link=False):
    """
    :param source_file: str of the full path to the source file
    :param destination_file: str of the full path to the destination file
    :param soft_link: bool if True will soft link if possible
    :return: None
    """
    if not os.path.exists(source_file):
        raise IOError("No such file: %s" % source_file)
    mkdir_for_file(destination_file)
    if os.path.exists(destination_file):
        os.remove(destination_file)

    if os.name == 'posix' and soft_link:
        try:
            os.symlink(source_file, destination_file)
        except:
            shutil.copy(source_file, destination_file)
    else:
        try:
            shutil.copy(source_file, destination_file)
        except Exception:
            raise


def read_folder(folder, ext='*', uppercase=False, replace_dot='.', parent=''):
    """
        This will read all of the files in the folder with the extension equal
        to ext
    :param folder: str of the folder name
    :param ext: str of the extension
    :param uppercase: bool if True will uppercase all the file names
    :param replace_dot: str will replace "." in the filename
    :param parent: str of the parent folder
    :return: dict of basename with the value of the text in the file
    """
    ret = {}
    if os.path.exists(folder):
        for file in os.listdir(folder):
            if os.path.isdir(os.path.join(folder, file)):
                child = read_folder(os.path.join(folder, file),
                                    ext, uppercase, replace_dot,
                                    parent=parent + file + '/')
                ret.update(child)
            else:
                if ext == '*' or file.endswith(ext):
                    key = file.replace('.', replace_dot)
                    key = uppercase and key.upper() or key
                    ret[parent + key] = read_file(os.path.join(folder, file))
    return ret


class FileNotFoundError(Exception):
    pass


def find_path(target, from_path=None, direction='both', depth_first=False):
    """
    Finds a file or subdirectory from the given
    path, defaulting to a breadth-first search.
    :param target:      str of file or subdirectory to be found
    :param from_path:   str of path from which to search (defaults to relative)
    :param direction:   str enum of up, down, both
    :param depth_first: bool of changes search to depth-first
    :return:            str of path to desired file or subdirectory
    """
    from_path = from_path if from_path else relative_path('', 2)

    if direction == 'up' or direction == 'both':
        path = from_path
        for i in range(100):
            try:
                file_path = os.path.abspath(os.path.join(path, target))
                if os.path.exists(file_path):
                    return file_path
                path = os.path.split(path)[0]
                if len(path) <= 1:
                    break
            except Exception:
                break
        if os.path.exists(os.path.join(path, target)):
            return os.path.join(path, target)

    if direction == 'down' or direction == 'both':
        check = ['']
        while len(check) != 0:
            dir = check.pop(0)
            try:
                roster = os.listdir(os.path.join(from_path, dir))
            except Exception:
                continue    # ignore directories that are inaccessible
            if target in roster:
                return os.path.join(from_path, dir, target)
            else:
                stack = [os.path.join(from_path, dir, i)
                         for i in roster if '.' not in i]
                if depth_first:
                    check = stack + check
                else:
                    check += stack

    raise FileNotFoundError("Failed to find file: %s from %s", file, from_path)