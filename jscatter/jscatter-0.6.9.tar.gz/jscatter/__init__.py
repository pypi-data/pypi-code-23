# -*- coding: utf-8 -*-
# written by Ralf Biehl at the Forschungszentrum Jülich ,
# Jülich Center for Neutron Science 1 and Institute of Complex Systems 1
#    jscatter is a program to read, analyse and plot data
#    Copyright (C) 2015  Ralf Biehl
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
from __future__ import division

import os
import webbrowser

# Package information
_path_=os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(_path_,'version.py')) as f:    exec(f.read())

from .dataarray import dataArray
from .dataarray import dataList
from .dataarray import zeros
from .dataarray import ones
from .dataarray import fromFunction
from .graceplot import GracePlot

from . import formel
from . import structurefactor
from . import formfactor
from . import dls
from . import dynamic
from . import parallel
from . import examples
from . import utilities
from . import sas
from .formel import loglist

# shortcuts
grace = GracePlot
dA = dataArray
dL = dataList
sf = structurefactor
ff = formfactor

# import tests
from . import test
test_all=test.suite()

if 'HOME' in os.environ: home = os.environ['HOME']

def showDoc():
    """
    Open the documentation in a webbrowser and print location of the documentation.


    """
    if os.uname()[0]=='Darwin':
        # open is broken but seem to be fixed in newest MACOS versions
        wb=webbrowser.get('Safari')
    else:
        wb = webbrowser.get()
    dochtml=os.path.join(_path_, 'doc', 'html', 'index.html')
    print('open path ',dochtml)
    wb.open_new(dochtml)
    return



__all__ = ['__version__',
           'dataArray',
           'dataList',
           'formel',
           'formfactor',
           'dynamic',
           'ff',
           'sf',
           'structurefactor',
           'GracePlot',
           'dL',
           'dA',
           'grace',
           'examples',
           'loglist',
           'dls',
           'sas',
           'utilities'
           ]

# this is a workaround until we can use always numpy >1.8.2 in a new MMTK version for numpy>1.8.2
# noinspection PyUnresolvedReferences
from distutils.version import LooseVersion, StrictVersion

if LooseVersion(formel.np.__version__) > LooseVersion("1.9."):
    # noinspection PyBroadException
    try:
        from . import mpl

        __all__.append('mpl')
        mplot = mpl.mplot
    except:
        pass

del LooseVersion
del StrictVersion