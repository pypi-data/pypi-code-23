#!/usr/bin/env python3
import argparse
import cmd
import logging
import sys

from opengrokfs.opengrok import OpenGrok


class OpenGrokCscope(cmd.Cmd):
    prompt = '>> '

    def __init__(self, opengrok):
        super().__init__()
        self.opengrok = opengrok

    def do_q(self, arg):
        return True

    def default(self, line):
        try:
            field = int(line[0])
        except ValueError:
            print("cscope: unknown command '%s'" % line)
            return

        q = line[1:]

        if field == 0:
            params = {'refs': q}
        elif field == 1:
            params = {'defs': q}
        elif field == 4:
            params = {'q': q}
        elif field == 7:
            params = {'path': q}
        else:
            params = None

        results = []
        if params:
            results = self.opengrok.search(params)

        print('cscope: %d lines' % len(results))

        for r in results:
            function = r.function if r.function else '<unknown>'
            line = r.line if r.line else 1
            text = r.text if r.text else '<unknown>'

            print('%s %s %d %s' % (r.path, function, line, text))


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--url', required=True)
    parser.add_argument('--project', action='append')
    parser.add_argument('--strip')

    # Ignored, for compatibility with cscope
    parser.add_argument('-d')
    parser.add_argument('-f')
    parser.add_argument('-l')

    try:
        with open('.opengrokfs') as f:
            argv = [l.rstrip() for l in f.readlines()]
    except FileNotFoundError:
        argv = []

    args = parser.parse_args(argv + sys.argv[1:])

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    og = OpenGrok(args.url, projects=args.project, strip=args.strip)
    OpenGrokCscope(og).cmdloop()


if __name__ == '__main__':
    main()
