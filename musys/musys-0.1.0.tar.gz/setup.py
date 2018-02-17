"""
musys
--------

musys is an XML-RPC memory storage application

```````````````

::

import musys



And Easy to Install
```````````````````

::

    $ pip3 install musys


"""

from distutils.core import setup

setup(name = "musys",
    version="0.1.0",
    description="A simple network attatched memory module",
    author="Josh Bosley",
    author_email="bosley117@gmail.com",
    license="MIT",
    long_description=__doc__,
    classifiers = [
        "Programming Language :: Python",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Topic :: Database" ],
    packages=['musys'],
    install_requires=['dill'])
