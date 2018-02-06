# # from setuptools import setup
# #
# # setup(
# #     name = "campbel",
# #     version = "0.0.1",
# #     author = "Ryuichi Furuya",
# #     author_email = "campbel2525@gmail.com",
# #     description = ("Convenient tool"),
# #     license = "RYU",
# #     keywords = "campbel aws rds s3",
# #     url = "https://github.com/campbel2525/campbel",
# #     packages=['campbel']
# #     # package_data = {
# #     #     'nbupload': ['FileUploaderView.js'],
# #     # },
# # )
#
#
#!/usr/bin/env python
# -*- coding:utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals
import os

from setuptools import setup, find_packages

try:
    with open('./README.md') as f:
        readme = f.read()
except IOError:
    readme = ''

def _requires_from_file(filename):
    return open(filename).read().splitlines()

# version
here = os.path.dirname(os.path.abspath(__file__))
version = next((line.split('=')[1].strip().replace("'", '')
                for line in open(os.path.join(here,
                                              'campbel',
                                              '__init__.py'))
                if line.startswith('__version__ = ')),
               '0.0.dev0')

setup(
    name="campbel",
    version="0.0.10",
    url='https://github.com/campbel2525/campbel',
    author='Ryuichi Furuya',
    author_email='campbel2525@gmail.com',
    maintainer='Ryuichi Furuya',
    maintainer_email='campbel2525@gmail.com',
    description='Convenient tool"),',
    long_description=readme,
    packages=find_packages(),
    install_requires=['pymysql', 'boto'],
    license="MIT",
    classifiers=[
        # 'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        # 'Programming Language :: Python :: 3',
        # 'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.6',
        # 'License :: OSI Approved :: MIT License',
    ],
    entry_points="""
      # -*- Entry points: -*-
      [console_scripts]
      pkgdep = campbel.scripts.command:main
    """,
)


# from setuptools import setup
#
# setup(
#     name = "campbel",
#     version = "0.0.1",
#     author = "Ryuichi Furuya",
#     author_email = "campbel2525@gmail.com",
#     description = ("An IPython Notebook widget for letting users upload a file"),
#     license = "MIT",
#     keywords = "AWS S3 RDS",
#     url = "https://github.com/edvakf/nbupload",
#     packages=['campbel'],
#     # package_data = {
#     #     'nbupload': ['FileUploaderView.js'],
#     # },
# )
