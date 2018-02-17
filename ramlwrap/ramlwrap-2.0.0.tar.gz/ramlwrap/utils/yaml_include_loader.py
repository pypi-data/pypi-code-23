"""
Loads include files in yaml.
"""

import yaml
import os.path
from .exceptions import FatalException


class Loader(yaml.Loader):

    def __init__(self, stream):

        self._root = os.path.split(stream.name)[0]

        super(Loader, self).__init__(stream)

    def include(self, node):

        filename = os.path.join(self._root, self.construct_scalar(node))
        if os.path.isfile(filename):
            with open(filename, 'r') as f:
                return yaml.load(f, Loader)
        else:
            raise FatalException("Could not find %s" % filename)

    def template(self, node):

        filename = os.path.join(self._root, self.construct_scalar(node))
        if os.path.isfile(filename):
            with open(filename, 'r') as f:
                return f.read()
        else:
            raise FatalException("Could not find %s" % filename)

Loader.add_constructor('!include', Loader.include)
Loader.add_constructor('!template', Loader.template)
