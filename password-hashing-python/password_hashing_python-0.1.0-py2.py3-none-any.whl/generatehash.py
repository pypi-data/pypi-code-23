#!/usr/bin/env python

import sys
from six import print_

import password_hashing


def main():
    args = sys.argv
    if len(args) < 2:
        print_('Usage: {0} [PASSWORD]'.format(args[0]))
        sys.exit(1)

    print_(password_hashing.create_hash(args[1]))


if __name__ == "__main__":
    main()
