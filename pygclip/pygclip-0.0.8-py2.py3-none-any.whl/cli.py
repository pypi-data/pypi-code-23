"""
    pygclip.cli
    ~~~~~~~~~~~

    A simple command line application to run pygclip.

    :copyright: © 2018 by Bryan Lee McKelvey.
    :license: MIT, see LICENSE for more details.
"""

import argparse
import os.path
import sys
from textwrap import dedent
from typing import Union

from pygclip.html import generate_html
from pygclip.io import write_html_to_clipboard
from pygclip.logging import setup_logging


def _process_arguments(
    lexer: Union[str, None],
    style: Union[str, None],
    path: Union[str, None],
    clipboard: bool,
) -> None:
    html = generate_html(lexer=lexer, style=style, path=path, clipboard=clipboard)
    write_html_to_clipboard(html)


def main(argv=None) -> None:
    if argv is None:
        argv = sys.argv[1:]
    parser = argparse.ArgumentParser(description=dedent('''\
        Convert input code text into syntax-highlighted HTML in your clipboard.
    '''))
    parser.add_argument('-d', '--debug', dest='debug', action='store_true', help='debug output')
    parser.add_argument('-l', '--lexer', metavar='<lexer>', dest='lexer', help='lexer name')
    parser.add_argument('-s', '--style', metavar='<style>', dest='style', help='style name')
    parser.add_argument('-c', '--clipboard', dest='clipboard', action='store_true', help='read from clipboard')
    parser.add_argument('path', nargs='?', help='input file path')
    args = parser.parse_args(argv)

    setup_logging(args.debug)

    if args.path is not None and not os.path.isfile(args.path):
        raise FileNotFoundError('File does not exist: {}'.format(args.path))

    _process_arguments(
        lexer=args.lexer,
        style=args.style,
        path=args.path,
        clipboard=args.clipboard,
    )


if __name__ == '__main__':
    main()
