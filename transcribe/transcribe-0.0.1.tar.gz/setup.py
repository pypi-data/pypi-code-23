#!/usr/bin/env python
# http://docs.python.org/distutils/setupscript.html
# http://docs.python.org/2/distutils/examples.html
from setuptools import setup, find_packages
import re
import os
from codecs import open


name = "transcribe" # TODO give me a name
###############################################################################
# REMOVE WHEN FLESHED OUT
#name = os.path.splitext(os.path.basename(os.path.dirname(__file__)))[0].lstrip("_").lower()
#import subprocess
filepath = "{}.py".format(name)
if not os.path.isfile(filepath):
    with open(filepath, 'w') as f:
        f.write("\n__version__ = '0.0.1'\n")

#subprocess.check_call("touch {}.py".format(name), shell=True)
###############################################################################
with open(os.path.join("{}.py".format(name)), encoding='utf-8') as f:
#with open(os.path.join(name, "__init__.py"), encoding='utf-8') as f:
    version = re.search("^__version__\s*=\s*[\'\"]([^\'\"]+)", f.read(), flags=re.I | re.M).group(1)

long_description = ""
if os.path.isfile('README.rst'):
    with open('README.rst', encoding='utf-8') as f:
        long_description = f.read()

setup(
    name=name,
    version=version,
    description='PLACEHOLDER',
    long_description=long_description,
    author='Jay Marcyes',
    author_email='jay@marcyes.com',
    url='http://github.com/Jaymon/{}'.format(name),
    py_modules=[name], # files
    # packages=find_packages(), # folders
    license="MIT",
#     install_requires=[''],
    classifiers=[ # https://pypi.python.org/pypi?:action=list_classifiers
        'Development Status :: 1 - Planning',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
    ],
#     entry_points = {
#         'console_scripts': [
#             '{} = {}:console'.format(name, name),
#         ],
#     }
)
