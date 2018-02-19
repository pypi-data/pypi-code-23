#!/usr/bin/python3

class TemplateSet(object):
    def __init__(self):
        self.variable = {}
        self.constant = {}

    def _add_file(self, source_path, destination_path):
        if destination_path.endswith('.~'):
            self.variable[destination_path[:-2]] = source_path
        else:
            self.constant[destination_path] = source_path

    def add_path(self, path):
        from os import walk
        from os.path import abspath
        from os.path import basename
        from os.path import isdir
        from os.path import isfile
        from os.path import join
        from os.path import normpath

        path = abspath(normpath(path))

        if isdir(path):
            for root, dirs, files in walk(path):
                for file in files:
                    full_path = join(root, file)
                    self._add_file(full_path, full_path[len(path) + 1:])
        elif isfile(path):
            self._add_file(path, basename(path))

