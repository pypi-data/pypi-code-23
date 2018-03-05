from .base import ObjectOnFileSystem, FileSystem
from .path import Path
import fs
from .conf import mc


class NotAFileError(Exception):
    def __init__(self, path: str):
        super().__init__("{} is not a file.".format(path))


class File(ObjectOnFileSystem):
    """
    Representation of File.
    """

    def __init__(self, path: Path, filesystem: FileSystem=None):
        super().__init__(filesystem, path)

    def name(self):
        return self.path.n

    def suffix(self):
        return self.path.suffix

    def load(self) -> 'File':
        """
        Returns:

        - contents loaded by assuming file as binary str.
        """
        if not self.exists():
            raise FileNotFoundError(self.path.abs)
        with self.filesystem.open() as fs:
            with fs.open(self.path.s, 'rb') as fin:
                return fin.read()

    def save(self, data: str):
        with self.filesystem.open() as fs:
            with fs.open(self.path.s, 'wb') as fout:
                return fout.write(data)

    def exists(self):
        result = super().exists()
        if not result:
            return result
        with self.filesystem.open() as fs:
            if not fs.isfile(self.path.s):
                raise NotAFileError(self.path.s)
        return result

    def copy_to(self, target_path: Path):
        with self.filesystem.open() as fs:
            fs.copy(self.path.s, target_path.s)
        return File(target_path, self.filesystem)
