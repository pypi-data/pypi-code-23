"""
DHKeyman
--------

DHKeyman Description

```````````````

::

import dhkeyman

```````````````````

::

    $ pip3 install dhkeyman


"""

from distutils.core import setup

setup(name = "dhkeyman",
    version="0.1.0",
    description="A python-based key manager.",
    author="Josh Bosley",
    author_email="bosley117@gmail.com",
    license="MIT",
    url="",
    long_description=__doc__,
    classifiers = [
        "Programming Language :: Python",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Topic :: Security :: Cryptography"],
    py_modules=['dhkeyman'],
    install_requires=['gherkindb'])
