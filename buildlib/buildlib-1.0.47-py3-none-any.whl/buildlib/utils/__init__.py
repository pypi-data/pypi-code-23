from typing import List
import sys
from cmdinter import CmdFuncResult
from sty import fg


def eprint(string):
    string = fg.li_red + string + fg.rs
    print(string, file=sys.stderr)


def print_summary(results: List[CmdFuncResult]):
    for result in results:
        if hasattr(result, 'summary'):
            print(result.summary)
        else:
            print('')
