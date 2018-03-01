import sys
from sty import fg
from cmdi import print_summary, print_status, print_title


def eprint(string):
    string = fg.li_red + string + fg.rs
    print(string, file=sys.stderr)
