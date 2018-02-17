"""
gherkindb
--------

gherkindb is lightweight, fast, and simple database based on pickledb

```````````````

::

import gherkindb

db = gherkindb.load('test1.db', True)

db.set('key', 'value')

# Outputs: value
print(db.get('key'))

# Added serialization functionality
def my_func():
    print("Much better!")

db.sset('func', my_func)

# Outputs: Much better!
db.sget('func')()

# Also :

# Outputs: Much better!
reborn = db.sget('func')

reborn()


And Easy to Install
```````````````````

::

    $ pip3 install gherkindb


"""

from distutils.core import setup

setup(name = "gherkindb",
    version="0.1.2",
    description="A lightweight and simple database using dill.",
    author="Josh Bosley",
    author_email="bosley117@gmail.com",
    license="three-clause BSD",
    url="https://github.com/joshbosley/gherkindb",
    long_description=__doc__,
    classifiers = [
        "Programming Language :: Python",
        "License :: OSI Approved :: BSD License",
        "Intended Audience :: Developers",
        "Topic :: Database" ],
    py_modules=['gherkindb'],
    install_requires=['dill'])
