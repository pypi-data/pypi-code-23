import os
from distutils.core import setup


setup(
    name = 'epyphany',
    version = '0.1.3',
    packages=['epyphany'],
    description = ('A script for facilitating network service discovery.'),
    python_requires='>=3.5.3',

    author = 'Stumblinbear',
    author_email = 'stumblinbear@gmail.com',

    license = 'GNU',
    keywords = 'network discovery discover service broadcast packet',
    url = 'https://github.com/Secret-Web/epyphany',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: AsyncIO',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Topic :: System :: Networking'
    ],
)
