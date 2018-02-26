# -*- coding: utf-8 -*-

from setuptools import setup as st_setup
from setuptools import find_packages as st_find_packages
from sys import argv, version_info
from platform import python_implementation
import hydratk.lib.install.task as task
import hydratk.lib.system.config as syscfg

try:
    os_info = syscfg.get_supported_os()
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
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: Implementation",
    "Programming Language :: Python :: Implementation :: CPython",
    "Programming Language :: Python :: Implementation :: PyPy",
    "Topic :: Software Development :: Libraries :: Application Frameworks",
    "Topic :: Utilities"
]


def version_update(cfg, *args):

    major = version_info[0]
    if (python_implementation() != 'PyPy'):
        cfg['modules'].append({'module': 'matplotlib', 'version': '>=2.0.0', 'profile': 'math'})
        cfg['modules'].append({'module': 'scipy', 'version': '>=0.19.0', 'profile': 'math'})

config = {
    'pre_tasks': [
        version_update,
        task.install_modules
    ],

    'modules': [
        {'module': 'hydratk', 'version': '>=0.5.0', 'profile': 'basic'},
        {'module': 'numpy',   'version': '>=1.12.1', 'profile': 'basic'},
        {'module': 'sympy',   'version': '>=1.0',    'profile': 'math'}
    ]
}

task.run_pre_install(argv, config)

st_setup(
    name='hydratk-lib-numeric',
    version='0.1.1',
    description='Libraries for numerical computing, data analysis',
    long_description=readme,
    author='Petr Rašek, HydraTK team',
    author_email='bowman@hydratk.org, team@hydratk.org',
    url='http://libraries.hydratk.org/numeric',
    license='BSD',
    packages=st_find_packages('src'),
    package_dir={'': 'src'},
    classifiers=classifiers,
    zip_safe=False,
    keywords='hydratk,numerical computing,data analysis',
    requires_python='>=2.6,!=3.0.*,!=3.1.*,!=3.2.*',
    platforms='Linux,FreeBSD'
)
