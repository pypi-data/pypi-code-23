#!/usr/bin/python3
# -*- coding: utf-8 -*-


import setuptools


with open('./README.rst', 'r') as file:
    long_desc = file.read()


# set-up script for pip distribution
setuptools.setup(
    name = 'jspcapy',
    version = '0.1.1',
    author = 'Jarry Shaw',
    author_email = 'jarryshaw@icloud.com',
    url = 'https://github.com/JarryShaw/jspcap/jspcapy/',
    license = 'GNU General Public License v3 (GPLv3)',
    keywords = 'computer-networking pcap-analyzer pcap-parser',
    description = 'Project Assignment of Python 101 & Computer Networking (SJTU)',
    long_description = long_desc,
    python_requires = '>=3.4',
    py_modules = ['jspcap', 'jsformat'],
    entry_points = {
        'console_scripts': [
            'jspcapy = src.jspcapy:main',
        ]
    },
    packages = [
        'src',
        'src.jsformat',
        'src.jspcap',
        'src.jspcap.protocols',
        'src.jspcap.protocols.application',
        'src.jspcap.protocols.internet',
        'src.jspcap.protocols.link',
        'src.jspcap.protocols.transport',
        'src.jspcap.reassembly',
    ],
    package_data = {
        '': [
            'LICENSE.txt',
            'README.md',
            'README.rst',
        ],
        'jsformat': ['*.py'],
        'jspcap': ['*.py'],
    },
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: MacOS X',
        'Environment :: Win32 (MS Windows)',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Operating System :: MacOS',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: System :: Networking',
        'Topic :: Utilities',
    ]
)
