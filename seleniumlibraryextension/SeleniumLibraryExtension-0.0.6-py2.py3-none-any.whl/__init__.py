#!/usr/bin/env python
# -*- coding: utf-8 -*-


from robot.libraries.BuiltIn import BuiltIn
from SeleniumLibrary import SeleniumLibrary

from SeleniumLibraryExtension.decorators import DocInherit
from SeleniumLibraryExtension.version import get_version

from SeleniumLibraryExtension.keywords import ElementKeywordsExtension

from SeleniumLibraryExtension.base.contextpatch import ContextPatch

__version__ = get_version()


@DocInherit
class SeleniumLibraryExtension(SeleniumLibrary, ContextPatch):
    # ROBOT_EXIT_ON_FAILURE = True
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LIBRARY_VERSION = __version__
    def __init__(self, implicit_wait=15.0, **kwargs):

        self._builtin = BuiltIn()
        SeleniumLibrary.__init__(self, implicit_wait=implicit_wait, **kwargs)
        ContextPatch.__init__(self)
        # self.add_library_components([ElementKeywordsExtension(self)])

if __name__=='__main__':
    esl = SeleniumLibraryExtension()
    print(dir(esl))
    print(esl.__init__.__doc__)
