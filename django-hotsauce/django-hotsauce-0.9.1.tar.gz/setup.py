#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
PY3K = sys.version_info[0] == 3
import os
import posixpath
import glob

# see bootstrap for installing thoses requirements
# using easy_install (err Distribute)
try:
    import yaml 
except ImportError as e:
    raise e
    #raise ImportError("Please run the ./bootstrap script first.")

workdir = os.getcwd()
admindir = posixpath.join(workdir, 'admin')

# adds 'lib' to sys.path 
#sys.path.insert(0, posixpath.join(workdir, 'lib'))
#import notmm
#DEVELOPMENT_RELEASE = False
#buildName = notmm.getBuildName(release=isRelease)

from setuptools import setup, find_packages, Extension
#from pkg_resources import resource_stream

# Do import buildutils commands if available!
try:
    import buildutils
except ImportError:
    print('Consider installing the buildutils module!')

libs = find_packages(where='lib')

# Meta info in YAML data format for improved readability
meta = yaml.load(open(posixpath.join(admindir, 'PKG-INFO.in')))

scripts_data = glob.glob('tools/schevo-*') + ['tools/httpserver.py']

staticdir = posixpath.abspath(os.path.join(admindir, 'static'))

classifiers = [
    (str(item)) for item in open(posixpath.abspath(os.path.join(staticdir, \
    'classifiers.txt'))).read().split('\n') if item is not '']

setup(
    name=meta['Name'],
    version=meta['Version'],
    description=meta['Summary'], 
    #long_description=meta['Description'],
    long_description=__doc__, #hack (we require reStructuredText support..)
    author=meta['Author'],
    author_email=meta['Author-email'],
    license=meta['License'],
    keywords=meta['Keywords'],
    url=meta['Homepage'],
    #maintainer=meta['Maintainer'],
    #maintainer_email=meta['Maintainer-email'],
    scripts=scripts_data,

    # Include stuff which belong in SVN or mentioned in MANIFEST.in
    include_package_data=True,

    # Location where packages lives
    package_dir={'': 'lib'},
    packages=libs,

    # Package classifiers are read from static/classifiers.txt
    classifiers=classifiers,

    # Add Cython compiled extensions
    #cmdclass={'build_ext': build_ext},
    #ext_modules=ext_modules,
    
    # Minimal packages required when doing `python setup.py install`.
    install_requires=[
        #'Django>=1.11.1',     # Maintainers should not need this :)
        'pytz>=2017.2',
        'Beaker>=1.9.0',
        'configobj>=4.7.2', # in notmm.utils.configparse (required)
        'argparse>=1.1',    # used by tools/httpserver.py
        'demjson>=2.2.4',   # in YAMLFixture
        'Mako>=1.0.7',      # for legacy compat with makoengine.py
        #'feedparser>=5.1.2'# rss (feedapp)
        #'docutils>=0.8.1', # HTMLPublisher (restapp)
        #'cogen>=0.2.1',    # XXX what for ?
        #'python-epoll>=1.0', # for epoll support; linux only?
        'pytidylib>=0.2.1',
        'WebOb>=1.7.3',      # HTTPResponse,HTTPRequest
        'python-memcached>=1.58',
        'Werkzeug>=0.12.2',
        #'gevent>=1.2.2',
        #'ZODB>=5.3.0',
        #'ZEO>=5.1.0'
        
    ],
    zip_safe=False
)

