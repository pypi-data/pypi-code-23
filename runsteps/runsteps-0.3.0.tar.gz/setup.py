from setuptools import setup, find_packages
from codecs import open
from os import path

with open(path.join(path.abspath(path.dirname(__file__)), 'README.rst'),
          encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='runsteps',

    description='A tool for executing a set of ordered instructions',
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/jhuntwork/runsteps',

    # Author details
    author='Jeremy Huntwork',
    author_email='jhuntwoarrk@lightcubesolutions.com',
    license='MIT',

    version='0.3.0',
    zip_safe=True,

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],

    keywords='scripting automation',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),

    entry_points={'console_scripts': ['runsteps=runsteps:main']}
)
