import sys

import fuse

from tagfs.arguments import ArgumentParser, function_wrapper
from tagfs.ops import TagFS
from .db import Database


HELP_TEXT = """\
Usage: python -m tagfs FILE.tfs COMMAND ARGS...
Where command is:
  help, --help, -h        Show this message and exit
  mount DIR OPTIONS...    Mount tagfs to DIRectory
    -X                    Disable xattrs
    -A                    Disable __ALL__ tag
    -a                    Mount without tags (all files)
"""


@function_wrapper(name='mount.default')
def default(db: str, path: str) -> None:
    """Mount tagfs"""
    db = Database(db)
    fuse.FUSE(TagFS(db), path)


@function_wrapper
def mount(options: str, db: str, path: str) -> None:
    """Mount tagfs with options"""
    kw = {}

    for i in options.split(','):
        i = i.strip()
        n = i.find('=')
        if n == -1:
            kw[i] = True
        else:
            kw[i[n - 1:]] = i[:n]

    db = Database(db)
    fuse.FUSE(TagFS(db), path, raw_fi=False, **kw)


def main():
    p = ArgumentParser()

    p.add(('mount', 'default', ), default)
    p.add(('mount', ), mount)
    p.add_types(Database.CURSOR_TYPES, init_type=Database)
    if not p.parse(sys.argv):
        sys.exit(1)


if __name__ == '__main__':
    main()
