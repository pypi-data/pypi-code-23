#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import subprocess
from setuptools import setup


package_name = 'bubble'
version = '2018.3.7'
url = 'https://soft.snbl.eu/_sources/bubble.rst.txt'
token = '.. Bubble Versions'
text = 'A new Bubble version is available at <a href=https://soft.snbl.eu/bubble.html#download>soft.snbl.eu</a>'
frozen_name = 'bubble/frozen.py'
we_run_setup = False
if not os.path.exists(frozen_name):
    we_run_setup = True
    hash_ = subprocess.Popen(['hg', 'id', '-i'], stdout=subprocess.PIPE).stdout.read().decode().strip()
    print(f'Bubble mercurial hash is {hash_}')
    print('Creating frozen.py...\n', '*' * 40)
    with open(frozen_name, 'w') as frozen:
        s = (f'# -*- coding: utf-8 -*-\n\nhg_hash = "{hash_}"\nversion = "{version}"\nurl = "{url}"\ntoken = "{token}"'
             f'\ntext = "{text}"\n')
        frozen.write(s)
        print(s, '*' * 40)
        print('Done')


setup(
    name='bubble-dubble',
    version=version,
    description='Azimuthal powder integration',
    author='Vadim Dyadkin',
    author_email='dyadkin@gmail.com',
    url='https://hg.3lp.cx/bubble',
    license='GPLv3',
    install_requires=[
        'numpy',
        'cryio',
        'integracio',
        'decor',
        'pyqtgraph',
        'Pillow',
        'scipy',
        'qtsnbl',
    ],
    entry_points={
        'console_scripts': [
            f'bubbles={package_name}.bserver.__init__:main',
        ],
        'gui_scripts': [
            f'bubblec={package_name}.bclient.__init__:main',
        ],
    },
    packages=[
        'bubble',
        'bubble.bclient',
        'bubble.bclient.ui',
        'bubble.bcommon',
        'bubble.bserver',
    ],
)


if we_run_setup:
    print('Remove frozen.py')
    os.remove(frozen_name)
