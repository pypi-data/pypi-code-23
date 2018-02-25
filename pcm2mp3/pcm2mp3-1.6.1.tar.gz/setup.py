from __future__ import print_function
'''
Created on 1 Dec 2017

@author: julianporter
'''
from setuptools import setup, Extension
from setuptools.config import read_configuration
import utils
from collections import namedtuple
from sys import exit


checker=utils.CheckLibrary("mp3lame")
checker.test()
if not checker['mp3lame']:
    print("Cannot build pcm2mp3 unless libmp3lame is installed and on the compiler path")
    exit(1)

configuration=read_configuration('setup.cfg')
metadata=configuration['metadata']

#package=metadata['name']


wsrc=['python/Lame.cpp']
lsrc=utils.Scanner('./src/pylame/')()
lsrc.extend(wsrc)

Version = namedtuple('Version',['major','minor','maintenance'])
def processVersion():
    version=metadata['version']
    parts=version.split('.')
    if len(parts)<3: parts.extend([0,0,0])
    return Version(*(parts[:3]))

def makeExtension(module,src):
    print('Making {} with {}'.format(module,src))
    
    v=processVersion()
    return Extension(module,
                    define_macros = [('MAJOR_VERSION', v.major),
                                     ('MINOR_VERSION', v.minor),
                                     ('MAINTENANCE_VERSION', v.maintenance)],
                    sources = src,
                    language = 'c++',
                    include_dirs=['/usr/include','src/','src/pylame'],
                    libraries = ['mp3lame'],
                    library_dirs = ['/usr/lib/x86_64-linux-gnu'])

coder = makeExtension('pcm2mp3',lsrc)

with open('README.rst') as readme:
    longDescription = readme.read()

setup (
    ext_modules = [coder],
    long_description = longDescription ,
    cmdclass = {
        'deepclean' : utils.Cleaner
        }
)
