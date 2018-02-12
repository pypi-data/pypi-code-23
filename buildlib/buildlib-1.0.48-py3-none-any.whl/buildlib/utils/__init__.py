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
            if '[OK]' in result.summary:
                print(fg.li_green + result.summary + fg.rs)
            elif '[ERR' in result.summary:
                print(fg.li_red + result.summary + fg.rs)
            else:
                print(fg.li_magenta + result.summary + fg.rs)
        else:
            print('')
