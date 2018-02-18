# coding=utf-8

import elib
from pathlib import Path
from mockito import when, contains, verifyStubbedInvocationsAreUsed

from edlm import external_tools


def test_pandoc():
    pandoc = external_tools.Pandoc()
    exe = Path('exe')
    when(pandoc).get_exe().thenReturn(exe)
    when(elib).run(contains('--version'), mute=True).thenReturn(('pandoc version\ntext', 0))
    assert pandoc.get_version() == 'version'
    assert pandoc.get_version() == 'version'
    verifyStubbedInvocationsAreUsed()
