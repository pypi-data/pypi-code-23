#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import subprocess
from setuptools import setup


version = '2018.2.27'
frozen_name = 'SNBLToolBox/frozen.py'
url = 'https://soft.snbl.eu/_sources/toolbox.rst.txt'
token = '.. SNBLToolBox Versions'
text = ('A new version of SNBL Toolbox is available at '
        '<a href=https://soft.snbl.eu/toolbox.html#download>soft.snbl.eu</a>')
we_run_setup = False
if not os.path.exists(frozen_name):
    we_run_setup = True
    hash_ = subprocess.Popen(['hg', 'id', '-i'], stdout=subprocess.PIPE).stdout.read().decode().strip()
    print(f'SNBLToolBox mercurial hash is {hash_}')
    print('Creating frozen.py...\n', '*' * 40)
    with open(frozen_name, 'w') as frozen:
        s = (f'# -*- coding: utf-8 -*-\n\nhg_hash = "{hash_}"\nversion = "{version}"\nurl = "{url}"\ntoken = "{token}"'
             f'\ntext = "{text}"\n')
        frozen.write(s)
        print(s, '*' * 40)
        print('Done')

setup(
    name='snbl-toolbox',
    version=version,
    description='SNBL Toolbox',
    author='Vadim Dyadkin',
    author_email='dyadkin@gmail.com',
    url='https://soft.snbl.eu/toolbox.html',
    license='GPLv3',
    install_requires=[
        'numpy',
        'cryio',
        'crymon',
        'qtsnbl',
        'scipy',
    ],
    entry_points={
        'gui_scripts': [
            f'snbl=SNBLToolBox.__init__:main',
        ],
    },
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
    packages=[
        'SNBLToolBox',
        'SNBLToolBox.roerik',
        'SNBLToolBox.ui',
    ],
)

if we_run_setup:
    print('Remove frozen.py')
    os.remove(frozen_name)
