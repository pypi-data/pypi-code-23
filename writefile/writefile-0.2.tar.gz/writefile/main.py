#!/usr/bin/env python

import os
import sys
import errno
import argparse


BUFSIZE = 2**20


def main(args=sys.argv[1:]):
    """
    Write stdin to a given PATH. When options imply potential file
    creation, any intermediate directories are created as necessary.
    """
    (path, shouldexist, contentpolicy) = parse_args(args)

    if shouldexist != 'yes':
        ensure_dir_exists(os.path.dirname(os.path.abspath(path)))

    try:
        fd = os.open(path, calculate_mode(shouldexist, contentpolicy))
    except os.error as e:
        if e.errno == errno.EEXIST:
            assert shouldexist == 'no', shouldexist
            raise SystemExit(
                '{} (writefile --exists=no causes this error condition.)'
                .format(e)
            )
        elif e.errno == errno.ENOENT:
            assert shouldexist == 'yes', shouldexist
            raise SystemExit(
                '{} (writefile --exists=yes causes this error condition.)'
                .format(e)
            )
        elif e.errno == errno.EISDIR:
            raise SystemExit(str(e))
        else:
            # reraise unexpected errors:
            raise

    with os.fdopen(fd, 'w') as f:
        buf = sys.stdin.read(BUFSIZE)
        while buf:
            f.write(buf)
            buf = sys.stdin.read(BUFSIZE)


def parse_args(args):
    p = argparse.ArgumentParser(description=main.__doc__)

    p.add_argument(
        '--exists',
        dest='EXISTS',
        choices=['yes', 'no', 'maybe'],
        default='no',
        help=(
            'Require PATH does, does not, or might exist, respectively. '
            '(Default: no)'
        ),
    )

    modemeg = p.add_mutually_exclusive_group()
    modemeg.add_argument(
        '--overwrite',
        action='store_true',
        help=(
            'Overwrite existing contents, if any. '
            'Default only when --exists=no.'
        ),
    )
    modemeg.add_argument(
        '--append',
        action='store_true',
        help=(
            'Append to existing contents, if any. '
            'Default unless --exists=no.'
        ),
    )

    p.add_argument(
        'PATH',
        help='The PATH to write.',
    )

    opts = p.parse_args(args)
    assert not (opts.overwrite and opts.append), opts

    contentpolicy = 'overwrite' if opts.overwrite else 'append'

    if opts.EXISTS == 'no':
        if opts.append:
            p.error('Nonsensical combination --exists=no with --append.')
        else:
            # Switch the default behavior in this one case:
            contentpolicy = 'overwrite'

    return (opts.PATH, opts.EXISTS, contentpolicy)


def calculate_mode(shouldexist, contentpolicy):
    openflags = os.O_WRONLY

    openflags |= {
        'maybe': os.O_CREAT,
        'no': os.O_CREAT | os.O_EXCL,
        'yes': 0,
    }[shouldexist]

    if contentpolicy == 'append':
        openflags |= os.O_APPEND

    return openflags


def ensure_dir_exists(path):
    try:
        os.makedirs(path)
    except os.error as e:
        if e.errno != errno.EEXIST:
            raise


if __name__ == '__main__':
    main()
