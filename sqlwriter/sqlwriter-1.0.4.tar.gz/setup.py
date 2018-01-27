# -*- coding: utf-8 -*-
import os
import shutil

from setuptools import find_packages, setup

base_dir = os.path.dirname(__file__)


def remove_build_files():
    for f in ('build', 'dist', 'sqlwriter.egg-info'):
        if os.path.exists(f):
            shutil.rmtree(f)


with open(os.path.join(base_dir, "README.rst")) as f:
    long_description = f.read()


def do_setup():
    remove_build_files()
    setup(
        name='sqlwriter',
        version='1.0.4',
        license="MIT",
        description="Writes pandas DataFrame to several flavors of sql database",
        long_description=long_description,
        packages=find_packages(),
        include_package_data=True,
        install_requires=[
            'pandas==0.21.0',
            'numpy==1.13.3'
        ],
        author='Sebastian Estenssoro',
        author_email='seb.estenssoro@gmail.com',
        url='https://github.com/estenssors/sqlwriter'
    )


if __name__ == '__main__':
    do_setup()
