# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name="ump",
    version='0.1.27',
    zip_safe=False,
    platforms='any',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    scripts=['ump/bin/umpctl'],
    install_requires=['redis', 'click', 'setproctitle', 'netkit'],
    url="https://github.com/dantezhu/ump",
    license="MIT",
    author="dantezhu",
    author_email="zny2008@gmail.com",
    description="upload data safer",
)
