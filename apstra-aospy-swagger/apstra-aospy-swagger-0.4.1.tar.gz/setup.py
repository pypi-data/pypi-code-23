#!/usr/bin/env python
# Copyright 2014-present, Apstra, Inc. All rights reserved.
#
# This source code is licensed under End User License Agreement found in the
# LICENSE file at http://www.apstra.com/community/eula

from setuptools import setup, find_packages
from pip.req.req_file import parse_requirements
from pip.download import PipSession

setup(
    name='apstra-aospy-swagger',
    packages=find_packages(),
    version='0.4.1',
    description="Python Swagger client for AOS Server",
    # TODO long_description=read('README.rst'),
    author='Apstra, Inc.',
    author_email='community@apstra.com',
    url='https://github.com/Apstra/aospy-swagger',
    include_package_data=True,
    license='Apache 2.0',
    zip_safe=False,
    install_requires=[
        item.name
        for item in parse_requirements(
            'requirements.txt',
            session=PipSession())],
    keywords=('serialization', 'rest', 'json', 'api', 'marshal',
              'marshalling', 'deserialization', 'validation', 'schema',
              'jsonschema', 'swagger', 'openapi', 'networking', 'automation'),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2.7',
    ]
)
