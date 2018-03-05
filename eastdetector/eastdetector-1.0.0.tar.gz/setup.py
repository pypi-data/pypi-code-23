#! /usr/bin/env python3
"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""


import setuptools


setuptools.setup(
    name='eastdetector',

    version='1.0.0',

    description='EAST text detector',

    # The project's main homepage.
    url='https://bitbucket.org/parqueryopen/east-detector',

    # Author details
    author='argmen (boostczc@gmail.com) is code author, '
           'Dominik Walder (dominik.walder@parquery.com) and Marko Ristin (marko@parquery.com) only packaged '
           'and wrapped the code',
    author_email='devs@parquery.com',

    # Choose your license
    license='GNU General Public License v3.0',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 5 - Production/Stable',

        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',

        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',

        'Programming Language :: Python :: 3.5',
    ],

    keywords='east text detector',

    packages=setuptools.find_packages(exclude=[]),

    install_requires=["numpy", "lanms", "tensorflow", "opencv-python"],
)
