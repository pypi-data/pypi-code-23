from deke import __version__
from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='Deke',
    version=__version__,
    description='A convenient HockeyApp API package making it easier than '
                'ever to manage apps, gather specific app statistics, '
                'and download builds.',
    long_description=long_description,
    url='https://github.com/misternate/deke',
    author='Nate Edwards',
    author_email='nathan.d.edwards@gmail.com',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='hockeyapp app center distribution ci',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=['requests', 'tqdm'],
    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # `pip` to create the appropriate form of executable for the target
    # platform.
    #
    # For example, the following would provide a command called `sample` which
    # executes the function `main` from this package when invoked:
    entry_points={  # Optional
        'console_scripts': [
            'sample=sample:main',
        ],
    },
)