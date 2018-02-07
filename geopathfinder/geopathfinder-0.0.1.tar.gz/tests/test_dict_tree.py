# Copyright (c) 2018, Vienna University of Technology (TU Wien), Department
# of Geodesy and Geoinformation (GEO).
# All rights reserved.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL VIENNA UNIVERSITY OF TECHNOLOGY,
# DEPARTMENT OF GEODESY AND GEOINFORMATION BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
Module managing folder tree structure.
"""

import os
from functools import reduce


def get_directory_structure(root_path):
    """
    Creates a nested dictionary that represents the folder structure
    of root path.

    Parameters
    ----------
    root_path : str
        Root path.

    Returns
    -------
    dir_dict : dict
        Directory tree stored in nested dictionary.
    """
    dir_dict = {}
    root_path = root_path.rstrip(os.sep)
    start = root_path.rfind(os.sep) + 1

    for path, dirs, files in os.walk(root_path):
        folders = path[start:].split(os.sep)
        subdir = dict.fromkeys(files)
        parent = reduce(dict.get, folders[:-1], dir_dict)
        parent[folders[-1]] = subdir

    return dir_dict


def nested_lookup(key, document, wild=False):
    """
    Lookup a key in a nested document, yield a value.

    Parameters
    ----------
    key : str
        Key string.
    document : dict
        Nested dictionary.
    wild : bool, optional
        If True case insensitive key lookup (default: False).

    Returns
    -------
    result : dict
        Yielding files/folder results.
    """
    if isinstance(document, list):
        for d in document:
            for result in nested_lookup(key, d, wild=wild):
                yield result

    if isinstance(document, dict):
        for k, v in document.items():
            if key == k or (wild and key.lower() in k.lower()):
                yield v
            elif isinstance(v, dict):
                for result in nested_lookup(key, v, wild=wild):
                    yield result
            elif isinstance(v, list):
                for d in v:
                    for result in nested_lookup(key, d, wild=wild):
                        yield result


# def flatten_dict(d):
#     def items():
#         for key, value in d.items():
#             if isinstance(value, dict):
#                 for subkey, subvalue in flatten_dict(value).items():
#                     yield key + "." + subkey, subvalue
#             else:
#                 yield key, value
#     return dict(items())


class SmartTree():
    """
    Class managing folder tree.

    Parameters
    ----------
    root_path : str
        Root path.
    """

    def __init__(self, root_path):
        self.dir_dict = get_directory_structure(root_path)

    def find_key(self, key, wild=False):
        """
        Find string in directory structure.

        Parameters
        ----------
        key : str
             Search string.

        Returns
        -------
        result : list of dict
            List of files/folders.
        """
        return list(nested_lookup(key, self.dir_dict, wild=wild))

    def iter_find_key(self, key, wild=False):
        """
        Lookup a key in a nested document, return a list of values.

        Parameters
        ----------
        key : str
            Key string.
        document : dict
            Dictionary.
        wild : bool, optional
            Wild (default: False).

        Returns
        -------
        result : list of dict
            List of files/folders.
        """
        return nested_lookup(key, self.dir_dict)

    def make_tree(self, tree_dict):
        """
        Make directory structure.

        Parameters
        ----------
        tree_dict : dict
            Nested dictionary defining folder tree.
        """
        pass


def test_smarttree():
    """
    Simple SmartTree test.
    """
    root_path = os.path.join('/home', 'shahn', 'shahn',
                             'home', 'documents', 'shahn')

    stree = SmartTree(root_path)
    result = stree.find_key('test')
    print(result)


if __name__ == '__main__':
    test_smarttree()
