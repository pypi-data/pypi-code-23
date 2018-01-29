#!/usr/bin/env python

from setuptools import setup, find_packages
from dao_deploy.config import VERSION

setup(
    name='dao-deploy',
    version=VERSION,
    description='DaoCloud Service 2.0 deploy tools',
    author='DaoCloud',
    author_email='hypo.chen@daocloud.io',
    url='http://www.daocloud.io',
    install_requires=[
        'requests==2.18.4',
        'six==1.11.0',
        'Jinja2>=2.4',
        'itsdangerous>=0.21',
    ],
    packages=find_packages(),
    classifiers=[  # Optional
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
