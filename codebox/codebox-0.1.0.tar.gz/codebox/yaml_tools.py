import os
import yaml

from codebox import dir_tools
from codebox import dict_tools

def load(path, recursive=False):
    files = []
    if os.path.isdir(path):                
        files = dir_tools.list_files(path, recursive)
    else:
        files = [path]

    data = dict()
    for _file in files:
        with open(_file) as f:            
            data = dict_tools.merge(data, yaml.load(f.read()))

    return data

if __name__ == '__main__':
    print(load('examples/yml/'))
