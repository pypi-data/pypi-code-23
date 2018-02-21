from __future__ import print_function
try:
    import builtins
except ImportError:
    import __builtin__ as builtins
import os

from sys import version_info

import pytest

from mock import call

from spaceminator import app
from spaceminator.app import File
from spaceminator.app import Spaceminator

PY3 = version_info.major == 3


@pytest.mark.parametrize('method, exp_type', [
    ('isdir', 'Dir'),
    ('isfile', 'File'),
    ('islink', 'Symlink'),
])
def test_File(mocker, method, exp_type):
    mocker.patch('spaceminator.app.os.path.{}'.format(method)).return_value = True
    f = File('dummy file.txt', '/home/user/')
    assert f.name == 'dummy file.txt'
    assert f.path == '/home/user/'
    assert f.full_path == '/home/user/dummy file.txt'
    assert f.type == exp_type


def test_File_raises(mocker):
    mocker.spy(builtins, 'print')
    with pytest.raises(KeyError):
        File('unknown type of file', '/home/user/')
    print.assert_called_with('Unknown file type (not a dir, file or symlink)')


def _get_File(tmp_file):
    return File(tmp_file.basename, tmp_file.dirpath().strpath)


@pytest.fixture
def get_tmp_files(tmpdir):
    f1 = tmpdir.join('top file')
    f1.write('content')
    d = tmpdir.mkdir('top dir')
    f2 = d.join('file inside dir')
    f2.write('content')
    symlink = tmpdir.join('sym link')
    symlink.mksymlinkto(f1)
    return _get_File(f1), _get_File(d), _get_File(symlink), _get_File(f2)


@pytest.mark.parametrize('list_only, quiet, char, recursive, file_type', [
    (True, False, '_', True, 'File'),
    (True, False, '_', True, 'Dir'),
    (True, False, '_', True, 'Symlink'),
    (True, False, '_', True, None),

    (False, False, '_', True, 'File'),
    (False, False, '_', True, 'Dir'),
    (False, False, '_', True, 'Symlink'),
    (False, False, '_', True, None),

    (True, True, '_', True, 'File'),
    (True, True, '_', True, 'Dir'),
    (True, True, '_', True, 'Symlink'),
    (True, True, '_', True, None),

    (True, False, '_', False, 'File'),
    (True, False, '_', False, 'Dir'),
    (True, False, '_', False, 'Symlink'),
    (True, False, '_', False, None),

    (False, True, '_', True, 'File'),
    (False, True, '_', True, 'Dir'),
    (False, True, '_', True, 'Symlink'),
    (False, True, '_', True, None),

    (False, False, '_', False, 'File'),
    (False, False, '_', False, 'Dir'),
    (False, False, '_', False, 'Symlink'),
    (False, False, '_', False, None),
])
def test_Spaceminator__init__(mocker, tmpdir, get_tmp_files, list_only, quiet, char, recursive, file_type):
    mocked__get_list_of_files = mocker.patch('spaceminator.app.Spaceminator._get_list_of_files')
    mocked__get_list_of_files.return_value = list(get_tmp_files)

    with tmpdir.as_cwd():
        s = Spaceminator(os.getcwd(), list_only, quiet, char, recursive, file_type)

    assert s.path == tmpdir
    assert s.recursive is recursive
    mocked__get_list_of_files.assert_called_with(file_type)
    assert s.files_list == list(get_tmp_files)
    assert s.list_only is list_only
    assert s.quiet is quiet
    assert s.char == char


@pytest.mark.parametrize('file_type, recursive', [
    ('File', False),
    ('Dir', False),
    ('Symlink', False),
    (None, False),

    ('File', True),
    ('Dir', True),
    ('Symlink', True),
    (None, True),
])
def test_Spaceminator__get_list_of_files(mocker, tmpdir, get_tmp_files, file_type, recursive):
    f1, d, sym, f2 = get_tmp_files
    mocker.spy(app.os, 'listdir')
    mocker.spy(app.os, 'walk')

    with tmpdir.as_cwd():
        files_list = Spaceminator(os.getcwd(), True, False, '_', recursive, file_type)._get_list_of_files(file_type)

    if recursive:
        assert app.os.walk.called
        if PY3:
            assert not app.os.listdir.called
        else:
            assert app.os.listdir.called
        if not file_type:
            assert all(f in files_list for f in [f1, d, f2, sym])
        elif file_type == 'File':
            assert files_list == [f2, f1]
    else:
        assert not app.os.walk.called
        assert app.os.listdir.called
        if not file_type:
            assert all(f in files_list for f in [f1, d, sym]) and f2 not in files_list
        elif file_type == 'File':
            assert files_list == [f1]

    if file_type == 'Dir':
        assert files_list == [d]
    elif file_type == 'Symlink':
        assert files_list == [sym]


@pytest.mark.parametrize('file_type, recursive', [
    (None, False),
    (None, True),
])
def test_Spaceminator_list_files(mocker, tmpdir, get_tmp_files, file_type, recursive):
    mocker.spy(builtins, 'print')
    with tmpdir.as_cwd():
        Spaceminator(os.getcwd(), True, False, '_', recursive, file_type).list_files()

    if recursive:
        print.assert_has_calls(
            [
                call("{}: '{}'".format(f.type, f.full_path)) for f in get_tmp_files
            ], any_order=True)
    else:
        print.assert_has_calls(
            [
                call("{}: '{}'".format(f.type, f.full_path)) for f in get_tmp_files[:-1]
            ], any_order=True)


@pytest.mark.parametrize('quiet', [
    (True,),
    (False,),
])
def test_Spaceminator_rename_files(mocker, tmpdir, get_tmp_files, quiet):
    mocker.spy(builtins, 'print')
    mocker.spy(app.os, 'rename')
    with tmpdir.as_cwd():
        Spaceminator(
            os.getcwd(), list_only=False, quiet=quiet, char='_', recursive=True, file_type=None
        ).rename_files()

    app.os.rename.assert_has_calls(
        [
            call(f.full_path, os.path.join(f.path, f.name.replace(' ', '_'))) for f in get_tmp_files
        ], any_order=True)

    if not quiet:
        print.assert_has_calls(
            [
                call("Renamed {} '{}' -> '{}'".format(f.type, f.full_path, f.name.replace(' ', '_'))) for f in get_tmp_files
            ], any_order=True)
    else:
        assert not print.called


@pytest.mark.parametrize('list_only', [
    True, False,
])
def test_Spaceminator_spaceminate(mocker, tmpdir, list_only):
    mocker.spy(app.Spaceminator, 'list_files')
    mocker.spy(app.Spaceminator, 'rename_files')
    with tmpdir.as_cwd():
        Spaceminator(
            os.getcwd(), list_only=list_only, quiet=False, char='_', recursive=True, file_type=None
        ).spaceminate()

    if list_only:
        assert app.Spaceminator.list_files.called
        assert not app.Spaceminator.rename_files.called
    elif not list_only:
        assert not app.Spaceminator.list_files.called
        assert app.Spaceminator.rename_files.called
