#!/usr/bin/env python3
from setuptools import setup


def get_version():
    return 1 #import os
    import re
    import subprocess
    dot_git = os.path.join(os.path.dirname(__file__), '.git')
    changelog = os.path.join(os.path.dirname(__file__), 'debian/changelog')
    if os.path.exists(dot_git):
        cmd = ['git', 'rev-list', 'HEAD', '--count']
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        rev = int(stdout) - 267
        return u'%s' % rev
    elif os.path.exists(changelog):
        f = open(changelog)
        head = f.read().strip().split('\n')[0]
        f.close()
        rev = re.compile('\d+\.\d+\.(\d+)').findall(head)
        if rev:
            return u"%s" % rev[0]
    return u'unknown'


setup(
    name="pandora_client",
    version="0.3.%s" % get_version(),
    description="pandora_client is a commandline client for pan.do/ra. You can use it to import videos into a pan.do/ra system. It is currently known to work on Linux and Mac OS X.",
    author="j",
    author_email="j@mailb.org",
    url="http://wiki.0x2620.org/wiki/pandora_client",
    license="GPLv3",
    scripts=[
        'bin/pandora_client',
    ],
    packages=[
        'pandora_client'
    ],
    install_requires=[
        'ox >= 2.3.804,<3',
        'six',
        'requests >= 1.1.0',
        'zeroconf',
        'netifaces',
    ],
    keywords=[],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License (GPL)',
    ],
)
