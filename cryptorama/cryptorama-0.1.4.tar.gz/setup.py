#   This file is part of the program cryptorama.
#
#   Copyright (C) 2017 by Bonnie Saunders, Marc Culler and others. 
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#   Project homepage: https://bitbucket.org/bonnie_saunders/cryptorama/
#   Author homepage: https://math.uic.edu/~saunders
#   Author homepage: https://marc-culler.info

from setuptools import setup, Command
from codecs import open
from subprocess import call, check_call
import os, sys, shutil

try:
    assert sys.version_info.major == 3 and sys.version_info.minor >= 5
except AssertionError:
    print('Please use Python >= 3.5.')
    sys.exit()

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

with open(os.path.join(here, 'cryptorama', 'version.py'), encoding='ascii') as f:
    exec(f.read())
    
def clean():
    html = os.path.join('documentation', 'html')
    doctrees = os.path.join('documentation', 'doctrees')
    for dir in ['build', 'dist', 'cryptorama.egg-info', html, doctrees]:
        if os.path.exists(dir):
            shutil.rmtree(dir)

class Release(Command):
    user_options = []
    def initialize_options(self):
        pass 
    def finalize_options(self):
        pass
    def run(self):
        clean()
        python = 'python3'
        check_call([python, 'setup.py', 'build_sphinx'])
        check_call([python, 'setup.py', 'bdist_wheel'])
        check_call([python, 'setup.py', 'sdist'])

class Clean(Command):
    user_options = []
    def initialize_options(self):
        pass 
    def finalize_options(self):
        pass
    def run(self):
        clean()
        
from cryptorama import __version__

setup(
    name='cryptorama',
    version=__version__,
    description='Tools for working with classical ciphers.',
    long_description=long_description,
    url='https://bitbucket.org/bonnie_saunders/cryptorama',
    author='Bonnie Saunders, Marc Culler',
    author_email='saunders.bss@gmail.com',
    license='GPL',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Education',
        'Topic :: Education',
        'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='cryptography cipher vigenere affine',
    packages=['cryptorama'],
    include_package_data=True,
    install_requires=[],
    cmdclass =  {'release': Release, 'clean': Clean},
    command_options={
        'build_sphinx': {
            'source_dir': ('setup.py', 'documentation/source'),
            'build_dir': ('setup.py', 'documentation'),
            }
        },
)
