import sys
from setuptools import find_packages
# Python 2 install
if sys.version_info[0] >= 3:
    from distutils.core import setup
else:
    from setuptools import setup

setup(
    name='mig-utils',
    version='0.1.0',
    description='Minimum Intrusion Grid (MiG) Utilities library',
    author='Rasmus Munk',
    author_email='munk1@live.dk',
    packages=find_packages(),
    install_requires=[
        'fs.sshfs>=0.7.1',
        'fs>=2.0.7',
        'six>=1.10'
    ],
    tests_require=[
        'pytest',
    ]
)
