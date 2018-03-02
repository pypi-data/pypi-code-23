from __future__ import absolute_import

from cmdline import settings

from .. filesystem import Filesystem


def main():
    root = settings.FILESYSTEM_ROOT
    name = settings.FILESYSTEM_NAME
    automount = settings.FILESYSTEM_AUTOMOUNT

    filesystem = Filesystem(root, name)
    filesystem.mount(automount=automount)
