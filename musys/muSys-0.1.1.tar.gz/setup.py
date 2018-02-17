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


from setuptools import setup, find_packages
setup(
    name="muSys",
    version="0.1.1",
    description="A simple network attatched memory module",
    author="Josh Bosley",
    author_email="bosley117@gmail.com",
    license="MIT",
    classifiers = [
        "Programming Language :: Python",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Topic :: Database" ],
    packages=find_packages(),
    install_requires=['dill']
    )
