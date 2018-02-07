import shutil
from traitlets.config import Application, LoggingConfigurable
from traitlets import Unicode

class Provider(LoggingConfigurable):
    name = Unicode(help="Name of the provider")
    description = Unicode(help="Description of the provider")

    def provide(self, identifier, dest):
        """
        Fetch the content provided by `identifier` into path dest
        """
        raise NotImplementedError("Needs to be overridden by subclasses")


class FileSystemProvider(Provider):
    name = "fs"

    description = """Copy repo contents from a local filesystem path"""

    def provide(self, identifier, dest):
        """
        Assume 'identifier' is a local file system path
        """
        return dest
