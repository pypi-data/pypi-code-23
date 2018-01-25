# coding: utf-8
"""
chiji
~~~~~~~~
CI/CD tool of Chongqing Parsec Corp.
Setup
-----
.. code-block:: bash
    > pip install chiji
    > chiji -h

"""

from setuptools import setup, find_packages  # Always prefer setuptools over distutils
from codecs import open  # To use a consistent encoding
from os import path
from setuptools.command.install import install
import re
import ast

_version_re = re.compile(r'__version__\s+=\s+(.*)')
version = str(ast.literal_eval(
    _version_re.search(
        open('chiji/__init__.py').read()
    ).group(1)
))
here = path.abspath(path.dirname(__file__))


class MyInstall(install):
    def run(self):
        print("-- installing... --")
        install.run(self)

setup(
        name = 'arms',
        version=version,
        description='CI/CD tool of Chongqing Parsec Corp.',
        long_description='\npip install arms\n\n'
                         'arms -h',
        url='https://pypi.python.org/pypi/arms',
        author='qorzj',
        author_email='inull@qq.com',
        license='MIT',
        platforms=['any'],

        classifiers=[
            ],
        keywords='chiji arms armstrong',
        packages = ['chiji'],
        install_requires=['lesscli', 'requests', 'Jinja2'],

        cmdclass={'install': MyInstall},
        entry_points={
            'console_scripts': [
                'arms = chiji.main:entrypoint'
                ],
            },
    )
