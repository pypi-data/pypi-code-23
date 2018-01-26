import sys, os
from .config import C_SOURCE_TEMPLATE

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from chestella.directory.Directory import Directory
from chestella.makefile.Makefile import Makefile

class ProjectAlreadyExistsException(Exception):
    def __init__(self, *args, **kwargs):
        super(ProjectAlreadyExistsException, self).__init__(self, *args, **kwargs)


class Project():
    def __init__(self, path):
        self.path = path
        self.name = os.path.basename(os.path.normpath(self.path))

        try:
            self.root_directory = Directory(self.path)
        except:
            raise ProjectAlreadyExistsException("A directory called '{}' exists already!".format(
                self.name
            ))

        self.bin_directory = Directory("{path}/bin".format(path=self.root_directory.path))
        self.obj_directory = Directory("{path}/obj".format(path=self.root_directory.path))
        self.src_directory = Directory("{path}/src".format(path=self.root_directory.path))

        self.src_directory.write_file("{}.c".format(self.name), C_SOURCE_TEMPLATE)

        self.makefile = Makefile(self.name, path=self.path)
        self.makefile.write_makefile()
