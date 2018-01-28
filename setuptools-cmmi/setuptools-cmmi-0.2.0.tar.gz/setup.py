import os
import logging
import sys
try:
    import multiprocessing
except:
    pass
# nose requires multiprocessing and logging to be initialized before the setup
# call, or we'll get a spurious crash on exit.
from setuptools import setup, find_packages
from setuptools.dist import Distribution


def read(fname):
    '''Utility function to read the README file.'''
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

Distribution(dict(
    setup_requires=['versioner'],
    dependency_links=['http://pypispandex.in.zillow.net/simple/versioner/']))

# figure out what the install will need
install_requires = ["setuptools >=0.5", "mock"]

setup(
    name="setuptools-cmmi",
    version="0.2.0",
    author="padev",
    author_email="padev@zillowgroup.com",
    description="Egg to handle the CMMI custom task in setuptools.",
    url="https://github.com/zillow/setuptools-cmmi",
    packages=find_packages(),
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],
    install_requires=install_requires,
    tests_require=install_requires,
    test_suite="nose.collector",
    entry_points={
        'distutils.setup_keywords': [
            'cmmi=setuptools_cmmi:cmmi_entry_point'
        ]
    }
    )
