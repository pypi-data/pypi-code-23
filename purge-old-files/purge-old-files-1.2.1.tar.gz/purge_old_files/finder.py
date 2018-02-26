from datetime import datetime
import logging
from os import walk, stat
from os.path import join


LOGGER = logging.getLogger(__name__)


class File:
    """A file found by the finder.
    """

    def __init__(self, path):
        self.path = path
        self._stat = None

    def __eq__(self, other):
        """Test if 2 file objects are identical.
        """
        return self.path == other.path

    def __gt__(self, other):
        """Test if self > other.
        """
        return self.path > other.path

    def __str__(self):
        """String representation.
        """
        return self.path

    def __repr__(self):
        """REPL representation.
        """
        return 'File(%r)' % self.path

    @property
    def stat(self):
        if self._stat is None:
            self._stat = stat(self.path, follow_symlinks=False)
        return self._stat

    @property
    def mtime(self):
        return datetime.fromtimestamp(self.stat.st_mtime)


def find(base_dir, filters=tuple()):
    """Find all files in ``base_dir`` that are older than ``min_age``.
    """
    LOGGER.info('Looking for files in %s', base_dir)

    result = []

    for parent_directory, _, files in walk(base_dir):
        for filename in files:
            filepath = join(parent_directory, filename)
            file_ = File(filepath)

            for filter_ in filters:
                if not filter_(file_):
                    break
            else:
                result.append(file_)

    return result
