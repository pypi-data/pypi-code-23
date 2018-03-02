from __future__ import absolute_import

import os
import subprocess
import sys
import time

from cmdline import settings

from .. import vault
from ..exceptions import CommandError
from ..utils import check_outfile, open_with_perms


def main():
    infile = settings.UNLOCK_INFILE
    outfile = settings.UNLOCK_OUTFILE
    command = settings.UNLOCK_COMMAND
    shell = settings.UNLOCK_SHELL

    check_outfile(outfile)

    if outfile == '-' and command:
        raise CommandError('cannot specify command when outfile is stdout')

    content = vault.unlock(infile)

    status = 0

    # if the outfile is a dash, print to the screen and exit
    if outfile == '-':
        print(content)

        return status

    with open_with_perms(outfile, 'wb', 0o400) as fh:
        fh.write(content)

    try:
        if command:
            status = subprocess.call([shell, '-c', command])
        else:
            sys.stderr.write('Hit ctrl+c when ready to remove unlocked file')
            while True:
                time.sleep(1.0)
    except KeyboardInterrupt:
        pass

    os.remove(outfile)

    return status


