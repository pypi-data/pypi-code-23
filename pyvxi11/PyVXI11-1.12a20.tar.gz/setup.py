#!/usr/bin/env python
"""
Author:Noboru Yamamoto, KEK, Japan (c) 2009-2013

contact info: http://gofer.kek.jp/
or https://plus.google.com/i/xW1BWwWsj3s:2rbmfOGOM4c

Thanks to:
   Dr. Shuei Yamada for improved vxi11scan.py
"""
import os,platform,re,sys

extra=dict()
if sys.version_info >= (3,):
    extra['use_2to3'] = True

   
from Cython.Distutils.extension import Extension
from Cython.Distutils import build_ext
from Cython.Build import cythonize

try:
   from distutils.command.build_py import build_py_2to3 as build_py #for Python3
except ImportError:
   from distutils.command.build_py import build_py     # for Python2

from distutils.core import setup
#from distutils.extension import Extension

rev="1.12a20"
# macros managedd by mercurial keyword extension
CVSAuthor="$Author: noboru $"
CVSDate="$Date: 2016/01/19 21:58:52 $"
CVSRev="$Revision: 1eeebd5331aa $"
CVSSource="$Source: /Users/noboru/src/python/VXI11/PyVXI11-Current/setup.py,v $"
CVSFile="$RCSFile: setup.py,v $"
CVSId="$Id: setup.py,v 1eeebd5331aa 2016/01/19 21:58:52 noboru $"

sysname=platform.system()
if re.match("Darwin.*",sysname):
    RPCLIB=["rpcsvc"]
elif re.match("CYGWIN.*",sysname):
    RPCLIB=["rpc"]
else:
    RPCLIB=None

try:
    os.stat("./VXI11.h")
    os.stat("./VXI11_svc.c")
    os.stat("./VXI11_clnt.c")
    os.stat("./VXI11_xdr.c")
except OSError:
    os.system("rpcgen -C -h VXI11.rpcl -o VXI11.h")
    os.system("rpcgen -C -m -L VXI11.rpcl -o VXI11_svc.c")
    os.system("rpcgen -C -l VXI11.rpcl -o VXI11_clnt.c")
    os.system("rpcgen -C -c VXI11.rpcl -o VXI11_xdr.c")
    # use of "-N" option should be considered 2013.11.5 NY

ext_modules=[]

ext_modules.append(Extension("cVXI11", 
                             [ "cVXI11.pyx", 
                               "VXI11_clnt.c", "VXI11_xdr.c",
                               "VXI11_svc.c", "createAbtChannel.c",
                             ]
                             ,libraries=RPCLIB
                             ,depends=["cVXI11.pxd"]
                             ,language="c++"
                             ,cython_cplus=True
                             ,undef_macros=["CFLAGS"]
                             ,extra_compile_args=[]
                         ))

# ext_modules.append(Extension("vxi11scan",
#                              [ "vxi11scan.pyx",
#                                "VXI11_clnt.c", "VXI11_xdr.c",
#                                "VXI11_svc.c", "createAbtChannel.c",
#                                ]
#                              ,libraries=RPCLIB
#                              ,depends=["cVXI11.pxd"]
#                              ,language="c++"
#                              ,cython_cplus=True
#                              ,undef_macros=["CFLAGS"]
#                              ,extra_compile_args=[]
#                          ))

## if you  like to compare cython version with swig-version, uncomment the 
## following lines. You must have swig in your path.
# ext_modules.append(Extension("_VXI11",["VXI11.i","VXI11_clnt.c","VXI11_xdr.c"]
#                     ,swig_opts=["-O","-nortti"]
#                     ,libraries=RPCLIB
#                     ))

ext_modules=cythonize(ext_modules)

setup(name="PyVXI11",
      version=rev,
      author="Noboru Yamamoto, KEK, JAPAN",
      author_email = "Noboru.YAMAMOTO@kek.jp",
      description='A Cython based Python module to control devices over VXI11 protocol.',
      url="http://www-cont.j-parc.jp/",
      classifiers=['Programming Language :: Python',
                   'Programming Language :: Cython',
                   'Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator',
                   ],
      ext_modules=ext_modules,
      cmdclass = {'build_ext': build_ext},
      py_modules=[
          "RebootLanGbib","AgilentDSO",
          "TekOSC","TekDPO","LeCroy",
          "vxi11Exceptions",
          #"vxi11scan","VXI11","vxi11Device",
      ],
      **extra
)
