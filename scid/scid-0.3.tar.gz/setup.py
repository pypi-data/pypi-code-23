from __future__ import with_statement
from setuptools import setup

setup(
    name='scid',
    version='0.3',
    description='Tool for installing solr config files',
    url='https://github.com/ryantownshend/solr_config_installer_device',
    author='Ryan Townshend',
    author_email='citizen.townshend@gmail.com',
    install_requires=[
        'click>=6.7',
        'click-log>=0.2.1',
    ],
    py_modules=['scid'],
    entry_points={
        'console_scripts': [
            'scid = scid:main'
        ],
    },
)
