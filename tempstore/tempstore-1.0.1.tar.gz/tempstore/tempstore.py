import os
import tempfile
import shutil
from collections import OrderedDict


class TempStore(object):
    def __init__(self, name=None):
        self.name = name
        self.objs = OrderedDict()
        self.dir = tempfile.TemporaryDirectory()

    def cleanup(self):
        """Cleanup all objects in this TempStore

        :return: None
        """
        for obj in self.objs.values():
            try:
                obj.cleanup()
            except AttributeError:
                obj.close()
            except FileNotFoundError:
                pass
        self.objs = OrderedDict()

    @property
    def paths(self):
        """Returns an OrderedDict that includes the paths to each object

        :return: OrderedDict
        """
        return OrderedDict([(n, obj.name) for n, obj in self.objs.items()])

    def create(self, name):
        """Creates a new tempfile and returns the path

        :param name: Name of the file to create
        :return: str
        """
        fp = tempfile.NamedTemporaryFile(dir=self.dir.name)
        self.objs[name] = fp
        return fp.name

    def copy(self, path, exist_ok=False):
        """Copy all objects in the TempStore to another location

        :param path: Path to a directory where they will be copied
        :param exist_ok: Ignore errors if the path already exists
        :return: None
        """
        if self.name is not None:
            os.makedirs(path, exist_ok=exist_ok)
            path = os.path.join(path, self.name)

        for name, obj in self.objs.items():
            src = obj.name
            dest = os.path.join(path, name)
            shutil.copy(src, dest)
    