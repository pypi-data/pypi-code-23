# -*- coding: utf-8 -*-
from setuptools import setup as st_setup
from setuptools import find_packages as st_find_packages
import sys
import os
import platform
import shutil

try:
    c_os = platform.system()
    if (c_os not in ['Windows', 'Linux']):
        raise SystemError('Unsupported operating system: {0}'.format(c_os))
except Exception as exc:
    print(str(exc))
    exit(1)

with open("README.rst", "r") as f:
    readme = f.read()

classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Environment :: Console",
    "Environment :: Other Environment",
    "Intended Audience :: Developers",
    "License :: Freely Distributable",
    "Operating System :: OS Independent",
    "License :: OSI Approved :: BSD License",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2.6",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3.3",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: Implementation",
    "Programming Language :: Python :: Implementation :: CPython",
    "Programming Language :: Python :: Implementation :: PyPy",
    "Topic :: Software Development :: Libraries :: Application Frameworks",
    "Topic :: Utilities"
]

packages = st_find_packages('src')

requires = [
    'pyyaml>=3.11',
    'jedi>=0.10.2',
    'GitPython>=2.1.8'
]

entry_points = {
    'console_scripts': [
        'htkclient = hydratk.client:main'
    ]
}

etc_dir = os.path.join(sys.prefix, 'etc/hydratk').replace('\\', '/')
if (not os.path.exists(etc_dir)):
    os.makedirs(etc_dir)
shutil.copy2('etc/hydratk/hydratk-client.conf', etc_dir)

var_dir = os.path.join(sys.prefix, 'var/local/hydratk/client/log').replace('\\', '/')
if (not os.path.exists(var_dir)):
    os.makedirs(var_dir)

st_setup(
    name='hydratk-client',
    version='0.1.0',
    description='GUI client for HydraTK',
    long_description=readme,
    author='Petr Rašek, HydraTK team',
    author_email='bowman@hydratk.org, team@hydratk.org',
    url='http://extensions.hydratk.org/client',
    license='BSD',
    packages=packages,
    package_dir={'': 'src'},
    package_data={'': ['*.gif']},
    install_requires=requires,
    classifiers=classifiers,
    zip_safe=False,
    entry_points=entry_points,
    keywords='hydratk,gui client,editor,yoda test design',
    requires_python='>=2.6,!=3.0.*,!=3.1.*,!=3.2.*',
    platforms='Windows,Linux'
)
