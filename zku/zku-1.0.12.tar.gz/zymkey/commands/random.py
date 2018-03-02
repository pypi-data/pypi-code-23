from __future__ import absolute_import

from cmdline import settings

from ..utils import get_random


def main():
    print(get_random(settings.NUM_BYTES))
