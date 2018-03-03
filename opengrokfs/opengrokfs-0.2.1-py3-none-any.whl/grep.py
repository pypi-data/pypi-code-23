#!/usr/bin/env python3
import argparse
import logging
import sys

from opengrokfs.opengrok import OpenGrok


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--url', required=True)
    parser.add_argument('--project', action='append')
    parser.add_argument('--strip')

    parser.add_argument('-n', '--line-number', action='store_true')
    parser.add_argument('pattern')

    try:
        with open('.opengrokfs') as f:
            argv = [l.rstrip() for l in f.readlines()]
    except FileNotFoundError:
        argv = []

    args = parser.parse_args(argv + sys.argv[1:])

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    og = OpenGrok(args.url, projects=args.project, strip=args.strip)
    results = og.search({'q': args.pattern})

    for r in results:
        if args.line_number:
            print('%s:%d:%s' % (r.path, r.line, r.text))
        else:
            print('%s:%s' % (r.path, r.text))

    sys.exit(0 if results else 1)


if __name__ == '__main__':
    main()
