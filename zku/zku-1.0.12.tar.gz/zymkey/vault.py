import os

import zymkey

from .exceptions import VaultError
from .utils import check_outfile, open_with_perms


def lock(outfile, content=None, infile=None, remove_infile=False):
    """
    Locks content into a zymkey-protected file

    Args:
        outfile (str): where to write the content
        content (bytearray): optional bytes to lock; if not provided, must provide infile
        infile (str): optional path to find content; if not provided, must provide content
        remove_infile (bool): whether to remove the original file

    Returns: None
    """
    # ensure only content or infile are provided
    if content and infile:
        raise VaultError('cannot provide content and infile')

    check_outfile(outfile)

    # Get content from infile when there is no content
    if not content:
        with open(infile, 'rb') as fh:
            content = fh.read()

    content = bytearray(content)

    encrypted = zymkey.client.lock(content)

    with open_with_perms(outfile, 'wb', 0o400) as fh:
        fh.write(encrypted)

    if remove_infile:
        os.remove(infile)


def unlock(infile):
    """
    Unlocks the content from the zymkey-protected file

    Args:
        infile (str): path to locked file

    Returns (bytearray):
        Unlocked content
    """
    with open(infile, 'rb') as fh:
        encrypted = bytearray(fh.read())

    return zymkey.client.unlock(encrypted)
