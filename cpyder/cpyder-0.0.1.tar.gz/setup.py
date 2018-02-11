# /usr/bin/python
# encoding=utf8
# author=spenly
# mail=i@spenly.com


import sys
from setuptools import setup, find_packages


def setup_package():
    setup(
        name='cpyder',
        version="0.0.1",
        description='one simple but powerful crawler!',
        url="https://github.com/spenly/cpyder",
        long_description="one simple but powerful crawler!",
        author='spenly',
        author_email='i@spenly.com',
        packages=find_packages(),
        install_requires=["lxml", "requests"],
        # entry_points={
        #     'console_scripts': [
        #         'cpyder=cpyder.cpyder:main',
        #     ]
        # },
    )


if __name__ == "__main__":
    setup_package()
