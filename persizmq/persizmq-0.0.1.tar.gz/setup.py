#! /usr/bin/env python3
"""
A setuptools based setup module.
"""

import setuptools

setuptools.setup(
    name='persizmq',

    version='0.0.1',

    description='Persistent handling of zeromq messages.',

    url='https://bitbucket.org/parqueryopen/persizmq',

    author='Dominik Walder',
    author_email='dominik.walder@parquery.com',

    license='MIT License',

    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',

        'Programming Language :: Python :: 3.5',
    ],

    keywords='persistent zeromq',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=setuptools.find_packages(exclude=[]),

)
