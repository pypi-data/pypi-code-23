#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup

version = "1.1.1"
desc = "Display, log and plot CPU utilization and network throughput"
longdesc = desc
author_name = "Mario Hock"
author_email_addr = "mario.hock@kit.edu"


setup(
        name = "cpunetlog",
        packages = [
            "cpunetlog"
            ],
        entry_points = {
            "console_scripts": [
                'cpunetlog = cpunetlog.main:main'
                ],
            },
        version = version,
        description = desc,
        long_description = longdesc,
        author =  author_name,
        author_email = author_email_addr,
        maintainer = author_name,
        maintainer_email = author_email_addr,
        url = "https://git.scc.kit.edu/CPUnetLOG/CPUnetLOG",
        license = "BSD",
        platforms = "Linux",
        zip_safe = False,
        install_requires = [
            'psutil',
            'netifaces'
        ],
        keywords = [
            'cpu',
            'throughput',
            'utilization',
            'plot',
            'log',
            'display',
            'analyze',
            'network',
            'traffic'
        ],
        classifiers = [
            'Development Status :: 5 - Production/Stable',
            'License :: OSI Approved :: BSD License',
            'Programming Language :: Python :: 3',
            'Operating System :: POSIX :: Linux',
            'Environment :: Console',
            'Environment :: Console :: Curses',
            'Natural Language :: English',
            'Intended Audience :: Education',
            'Intended Audience :: Information Technology',
            'Intended Audience :: Science/Research',
            'Intended Audience :: System Administrators',
            'Intended Audience :: Telecommunications Industry',
            'Topic :: Scientific/Engineering',
            'Topic :: Internet',
            'Topic :: System :: Logging',
            'Topic :: System :: Networking',
            'Topic :: System :: Networking :: Monitoring',
            'Topic :: System :: Operating System Kernels :: Linux',
            'Topic :: Utilities'
        ]
        )
