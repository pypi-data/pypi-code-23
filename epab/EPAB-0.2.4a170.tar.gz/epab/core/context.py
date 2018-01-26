# coding=utf-8
"""
Global runtime CTX
"""


class CTX:
    """
    Global EPAB context
    """
    run_once = {}
    dry_run = False
    known_executables = {}
    repo = None
    next_version = None
    stash = True

    @staticmethod
    def _reset():
        CTX.known_executables = {}
        CTX.dry_run = False
        CTX.run_once = {}
        CTX.repo = None
        CTX.next_version = None
        CTX.stash = True
