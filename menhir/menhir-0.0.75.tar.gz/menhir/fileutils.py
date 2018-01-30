import json
import os
import os.path
import subprocess
import sys

from collections import OrderedDict

import ruamel.yaml
from ruamel.yaml import YAML

from os import pathsep, walk
from os.path import (
    abspath,
    exists,
    join,
    normpath,
)

from menhir.utils import reductions


YAML_STR = u'tag:yaml.org,2002:str'


def yaml_dumper():
    yaml = YAML(typ='safe')
    yaml.representer.add_representer(str, yaml_repr_str)
    # Represent OrderedDict as a dict (with stable key ordering)
    yaml.representer.add_representer(
        OrderedDict,
        ruamel.yaml.representer.RoundTripRepresenter.represent_dict)

    yaml.width = 80
    yaml.indent = 2
    yaml.default_flow_style = False
    return yaml


def yaml_repr_str(dumper, data):
    if '\n' in data:
        return dumper.represent_scalar(YAML_STR, data, style='|')
    return dumper.represent_scalar(YAML_STR, data, style='')


def find_file_in_parents(file_name, base_dir=None):
    """From base_dir, look for a file in parent directories.

    Returns the full oath to the file found.

    `base_dir` defaults to the current directory.
    """
    dir = base_dir or os.getcwd()
    while True:
        f = os.path.join(dir, file_name)
        if os.path.exists(f):
            return f
        else:
            parent_dir = os.path.dirname(dir)
            if dir == parent_dir:  # if dir is root dir
                return None
            else:
                dir = parent_dir


def load_yaml(path):
    """Load the yaml at the specified path.

    If the path doesn't exist, return None.
    """
    yaml = YAML(typ='safe')
    if path == '-':
        return yaml.load(sys.stdin)
    if exists(path):
        with open(path, 'r') as stream:
            return yaml.load(stream)


def load_json(json_file):
    try:
        if json_file != "-":
            with open(json_file) as f:
                return json.load(f)
        return json.load(sys.stdin)
    except Exception:
        print('Failed to load JSON file.')
        raise


def load_encrypted(path, key):
    """Load an encrypted file into memory, decrypting it."""
    cmd = ["openssl", "aes-256-cbc", "-a", "-k", key,  "-in", path, "-d"]
    ps = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    return ps.communicate()[0].decode('utf-8')


def directory_graph(base_dir, ignore):
    """Return a graph of directories."""
    stop_dirs = {'__pycache__'}.union(set(ignore))
    graph = {}
    for root, subdirs, files in walk(base_dir):
        prune = [subdir for subdir in subdirs
                 if subdir in stop_dirs or subdir.startswith('.')]
        for subdir in prune:
            subdirs.remove(subdir)
        root = normpath(root)
        for subdir in subdirs:
            graph[root] = [normpath(join(root, subdir)) for subdir in subdirs]
    return graph


def paths_between(parent, child):
    """Return a list of path segments between parent and child."""
    if parent == child:
        return []
    parent = normpath(abspath(parent))
    child = normpath(abspath(child))
    assert child.startswith(parent)
    paths = child[len(parent)+1:].split(pathsep)
    paths.pop()
    return [parent] + list(reductions(join, paths, parent))


def slurp(path):
    """Read the specified file into a string."""
    with open(path) as f:
        return f.read()


def slurp_bytes(path):
    """Read the specified file into a byte array."""
    with open(path, 'rb') as f:
        return f.read()


def spit(path, data):
    """Write the specified file with a string."""
    with open(path, 'w+') as f:
        return f.write(data)


def spit_bytes(path, data):
    """Write the specified file with a byte array."""
    with open(path, 'w+b') as f:
        return f.write(data)
