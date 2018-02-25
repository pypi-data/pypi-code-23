import os
import yaml

from codebox import dir_tools
from codebox import dict_tools

def load(path, recursive=False):
    """Loads and parses a file or a folder containing yaml files.
    All existing dictorinaries will be deeply merged.
    
    Args:
        path (str): File or directory path.
        recursive (bool, optional): Defaults to False. Whether or not to include subdirectoties.
    
    Returns:
        dict
    """

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
