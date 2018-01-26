# coding=utf-8


import os
from pathlib import Path

import pytest
from mockito import ANY, and_, contains, mock, verify, when

import epab.cmd
import epab.cmd._appveyor
import epab.linters
import epab.utils
from epab.core import CONFIG, CTX


@pytest.fixture(autouse=True, name='setup')
def _all():
    ctx = mock()
    repo = mock()
    CTX.repo = repo
    when(ctx).invoke(...)
    when(CTX.repo).get_current_branch().thenReturn('branch')
    when(epab.utils).get_git_version_info().thenReturn('next_version')
    when(CTX.repo).is_dirty(untracked=True).thenReturn(False)
    when(CTX.repo).tag(...)
    when(CTX.repo).remove_tag(...)
    when(CTX.repo).commit(...)
    when(CTX.repo).push(...)
    when(epab.utils).run(...)
    yield ctx, repo


@pytest.mark.parametrize(
    'branch_coverage',
    [True, False],
)
def test_appveyor(setup, monkeypatch, branch_coverage):
    if branch_coverage:
        av_file = Path('appveyor.yml')
        av_file.touch()
    monkeypatch.setitem(os.environ, 'APPVEYOR_REPO_BRANCH', 'branch')
    monkeypatch.setitem(os.environ, 'APPVEYOR_REPO_COMMIT', 'commit')
    monkeypatch.setitem(os.environ, 'APPVEYOR_BUILD_NUMBER', 'build')
    # when(epab.cmd._appveyor)._appveyor_update_build(...)
    ctx, repo = setup
    epab.cmd._appveyor._appveyor(ctx)
    verify(ctx).invoke(epab.cmd.release)
    verify(epab.utils).run('pip install --upgrade codacy-coverage')
    verify(epab.utils).run('python-codacy-coverage -r coverage.xml')
    verify(epab.utils).run('appveyor UpdateBuild -Version next_version-build-commit')
    verify(epab.utils).get_git_version_info()
    if branch_coverage:
        assert not av_file.exists()
    # verify(epab.cmd._appveyor)._appveyor_update_build('next_Version')
