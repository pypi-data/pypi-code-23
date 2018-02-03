#!/usr/bin/env python3.6
"""Distribution and installation of Astrality."""

from pathlib import Path

from setuptools import find_packages, setup

def readme() -> str:
    p = Path(__file__).absolute()
    with open(Path(__file__).absolute().parents[1] / 'README.md') as file:
        return file.read()

setup(
    name='astrality',
    version='0.0.1',
    packages=find_packages(),
    install_requires=[
        'astral',
        'pyyaml',
        'Jinja2',
    ],
    python_requires='>=3.6',

    # metadata for upload to PyPI
    author='Jakob Gerhard Martinussen',
    author_email='jakobgm@gmail.com',
    description='A dynamic configuration file manager.',
    long_description=readme(),
    license="MIT",
    keywords="unix configuration management",
    url="http://github.com/JakobGM/astrality",

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: Unix',
        'Programming Language :: Python :: 3.6',
        'Topic :: Desktop Environment :: File Managers',
        'Topic :: Text Processing',
    ]
)
