from __future__ import print_function

import os

from collections import namedtuple

_File = namedtuple('File', ['name', 'path'])


class File(_File):
    def __new__(cls, name, path):
        self = super(File, cls).__new__(cls, name, path)
        self.full_path = os.path.join(self.path, self.name)
        file_types = {
            os.path.isdir(self.full_path): 'Dir',
            os.path.isfile(self.full_path): 'File',
            os.path.islink(self.full_path): 'Symlink',
        }
        try:
            self.type = file_types[True]
        except KeyError as e:
            print('Unknown file type (not a dir, file or symlink)')
            raise e
        return self


class Spaceminator(object):
    def __init__(self, path, list_only, quiet, char, recursive, file_type):
        self.path = os.path.abspath(path)
        self.recursive = recursive
        self.files_list = self._get_list_of_files(file_type)
        self.list_only = list_only
        self.quiet = quiet
        self.char = char

    def _get_list_of_files(self, file_type):
        if self.recursive:
            all_files = [
                File(name=el, path=path) for path, dirs, files in os.walk(self.path, topdown=False)
                for el in [d for d in dirs if ' ' in d] + [f for f in files if ' ' in f]
            ]
        else:
            all_files = [File(name=el, path=self.path) for el in os.listdir(self.path) if ' ' in el]
        if file_type:
            return [f for f in all_files if f.type == file_type]
        return all_files

    def list_files(self):
        for file in self.files_list:
            print("{}: '{}'".format(file.type, file.full_path))

    def rename_files(self):
        for file in self.files_list:
            new_name = file.name.replace(' ', self.char)
            os.rename(file.full_path, os.path.join(file.path, new_name))
            if not self.quiet:
                print("Renamed {} '{}' -> '{}'".format(file.type, file.full_path, new_name))

    def spaceminate(self):
        if self.list_only:
            self.list_files()
        else:
            self.rename_files()
