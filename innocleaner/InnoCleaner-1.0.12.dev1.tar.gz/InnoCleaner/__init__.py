#!/usr/bin/python

import sys

# Custom Imports
from InnoCleaner import cleaningUtility as cleanUtil


def __main__():
    """
    Entry Point to InnoCleaner Application
    :return: None
    """
    cleanUtil.CleaningUtility().main()


__main__()
