import sys
from sty import fg


def eprint(string):
    string = fg.li_red + string + fg.rs
    print(string, file=sys.stderr)
