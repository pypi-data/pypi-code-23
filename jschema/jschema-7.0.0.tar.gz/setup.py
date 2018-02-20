#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
from setuptools import setup

sys.path.insert(0, os.path.dirname(__file__))
from jschema.version import __version__

setup(
    name="jschema",
    version=__version__,
    description="Json Schema compiler",
    license="MIT",
    author="Stepan Perlov",
    author_email="stepanperlov@gmail.com",
    url="https://github.com/stepan-perlov/jschema",
    install_requires=["PyYAML", "jinja2"],
    packages=["jschema", "jschema.docs", "jschema.node"],
    package_data={
        "jschema.docs": [
            "templates/*.j2",
            "vendor/*.css",
            "vendor/*.js"
        ]
    },
    entry_points={
        "console_scripts": [
            "jschema = jschema.main:jschema",
            "jschema-docs = jschema.main:jschemaDocs"
        ]
    },
    python_requires='>=3',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3'
    ],
    platforms=["linux"]
)
