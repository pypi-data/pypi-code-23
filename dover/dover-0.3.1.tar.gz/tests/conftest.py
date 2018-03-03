from pathlib import Path
from tempfile import mkdtemp
import pytest


class Namespace(object):
    pass


def create_file(files, pth_name, content):
    setattr(files, pth_name + '_content', content)
    pth = getattr(files, pth_name)
    with pth.open(mode='w') as _fh:
        _fh.write(content)


def write_content(files):

    create_file(files, 'setup_cfg', '''[metadata]
name = newd
version = 0.3.0

[dover:file:setup.py]
[dover:file:setup.cfg]
[dover:file:newd/cli.py]
[dover:file:README.md]

[bdist_wheel]
universal = true
''')

    create_file(files, 'setup_py', '''#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

__version__ = '0.3.0'

''')

    create_file(files, 'readme', '''#### newd app v0.3.0

''')

    create_file(files, 'init_py', '')

    create_file(files, 'cli_py', '''import os

__version__ = '0.3.0'

def main():
    pass

''')


@pytest.fixture
def files():
    _files = Namespace()
    _files.temp_dir = _dir = Path(mkdtemp())
    _files.setup_cfg = Path(_dir, 'setup.cfg')
    _files.setup_py = Path(_dir, 'setup.py')
    _files.readme = Path(_dir, 'README.md')

    _files.package_dir = package = Path(_dir, 'newd')

    package.mkdir()

    _files.init_py = Path(package, '__init__.py')
    _files.cli_py = Path(package, 'cli.py')

    write_content(_files)

    yield _files

    _files.cli_py.unlink()
    _files.init_py.unlink()
    _files.readme.unlink()
    _files.setup_py.unlink()
    _files.setup_cfg.unlink()
    _files.package_dir.rmdir()
    _files.temp_dir.rmdir()


@pytest.fixture
def missmatch_files():
    _files = Namespace()
    _files.temp_dir = _dir = Path(mkdtemp())
    _files.setup_cfg = Path(_dir, 'setup.cfg')
    _files.setup_py = Path(_dir, 'setup.py')
    _files.readme = Path(_dir, 'README.md')

    _files.package_dir = package = Path(_dir, 'newd')

    package.mkdir()

    _files.init_py = Path(package, '__init__.py')
    _files.cli_py = Path(package, 'cli.py')

    write_content(_files)

    create_file(_files, 'cli_py', '''import os

__version__ = '6.6.6'

def main():
    pass

''')

    yield _files

    _files.cli_py.unlink()
    _files.init_py.unlink()
    _files.readme.unlink()
    _files.setup_py.unlink()
    _files.setup_cfg.unlink()
    _files.package_dir.rmdir()
    _files.temp_dir.rmdir()
