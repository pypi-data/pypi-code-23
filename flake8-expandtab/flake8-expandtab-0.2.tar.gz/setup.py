#!/usr/bin/env python

from setuptools import setup


def get_long_description():
    try:
        import pypandoc
        return pypandoc.convert("README.md", "rst")
    except ImportError:
        with open("README.md") as f:
            return f.read()


setup(
    name='flake8-expandtab',
    version='0.2',
    description='flake8 for tab junkies',
    long_description=get_long_description(),
    author='Chow Loong Jin',
    author_email='hyperair@debian.org',
    url='https://www.github.com/hyperair/flake8-expandtab',
    license='MIT',
    entry_points={
        'flake8.extension': [
            'expandtab = flake8_expandtab:TabExpander',
        ],
    },
    py_modules=['flake8_expandtab'],
    data_files=['README.md'],
    tests_require=['mock', 'flake8'],
    test_suite='tests',
    classifiers=[
        "Framework :: Flake8",
        "Intended Audience :: Developers",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Quality Assurance",
        "Operating System :: OS Independent"
    ]
)
