import os
from functools import partial

from .dropbox import filepath as dropbox_filepath

data_filepath = r'E:\Data'

def data_path(subpath):
    return os.path.join(data_filepath, subpath)

def data_path_func(subpath):
    return path_func(subpath, data_path)

def dropbox_path(subpath):
    return os.path.join(dropbox_filepath, subpath)

def dropbox_path_func(subpath):
    return path_func(subpath, dropbox_path)

def path_func(subpath, path_func):
    new_path = path_func(subpath)
    new_path_func = partial(os.path.join, new_path)
    return new_path_func

#### Project paths

etf_project_path = dropbox_path_func('UF\Andy\ETF Project')
etf_path_func = lambda subpath: path_func(subpath, etf_project_path)