import glob
import os
import tarfile
import tempfile
from contextlib import contextmanager
from fnmatch import fnmatch


@contextmanager
def create_tar_from_folder():
    """Create a tar.gz from the current folder."""
    no_hidden = set(glob.glob("*", recursive=True))
    hidden = set(glob.glob(".*", recursive=True))
    files = no_hidden.union(hidden)

    fp = tempfile.TemporaryFile()

    with tarfile.open(mode='w:gz', fileobj=fp) as tarobj:
        if ".gitignore" in files:
            with open('.gitignore', 'r') as fh:
                ignore_list = fh.read().splitlines()

        for filename in files:
            if os.path.isdir(filename):
                if any(fnmatch(filename + "/", pattern) for pattern in ignore_list):
                    continue
            else:
                if any(fnmatch(filename, pattern) for pattern in ignore_list):
                    continue
            tarobj.add(filename)

    fp.seek(0)

    yield fp

    fp.close()
