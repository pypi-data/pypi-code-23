import os
from .config import MAKEFILE_TEMPLATE

class Makefile():

    def __init__(self, name, path):
        self.name = name
        self.path = os.path.abspath(path)

    def write_makefile(self):
        with open("{}/Makefile".format(self.path), 'w') as f:
            f.write(MAKEFILE_TEMPLATE.format(name=self.name))
