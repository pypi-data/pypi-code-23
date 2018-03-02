from __future__ import absolute_import

from cmdline import settings

from .. import vault


def main():
    infile = settings.LOCK_INFILE
    outfile = settings.LOCK_OUTFILE

    vault.lock(outfile, infile=infile, remove_infile=settings.LOCK_REMOVE_ORIGINAL)
