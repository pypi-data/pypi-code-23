# $BEGIN_SHADY_LICENSE$
# 
# This file is part of the Shady project, a Python framework for
# real-time manipulation of psychophysical stimuli for vision science.
# 
# Copyright (C) 2017-18  Jeremy Hill, Scott Mooney
# 
# Shady is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program. If not, see http://www.gnu.org/licenses/ .
# 
# $END_SHADY_LICENSE$
__all__ = [
	'Import',
	'Unimport',
	'RegisterVersion',
	'GetVersions',
	'ReportVersions',
	
	'LoadPyplot',
]

import sys
import platform
import collections

# Force warnings.warn() to omit the source code line in the message
import warnings
formatwarning_orig = warnings.formatwarning
warnings.formatwarning = lambda message, category, filename, lineno, line=None, **k: formatwarning_orig( message, category, filename, lineno, line='' )

IMPORTED = {}
VERSIONS = collections.OrderedDict()

class ModuleNotAvailable( object ):
	def __init__( self, name, packageName=None, broken=False ): self.__name, self.__packageName, self.__broken = name, packageName, broken
	def __bool__( self ): return False    # works in Python 3 but not 2
	def __nonzero__( self ): return False # works in Python 2 but not 3
	def __getattr__( self, attr ): raise ImportError( str( self ) )
	def __str__( self ):
		packageName = self.__packageName
		if packageName and not isinstance( packageName, ( tuple, list ) ): packageName = [ packageName ]
		packageName = ' or '.join( repr( name ) for name in packageName ) if packageName else repr( self.__name )
		if self.__broken:
			msg = 'module %r did not work as expected for this functionality - your installation of the %r package may be broken' % ( self.__name, packageName )
			if self.__broken != 1: msg += ' (%s)' % self.__broken
		else:
			msg = 'module %r could not be imported - you need to install the third-party %s package for this functionality' % ( self.__name, packageName )
		return msg
		
def Import( name, *alternativeNames, **kwargs ):
	packageName = kwargs.pop( 'packageName', None )
	registerVersion = kwargs.pop( 'registerVersion', False )
	if kwargs: raise ValueError( 'unrecognized keyword argument to Import()' )
	for name in ( name, ) + alternativeNames:
		module = IMPORTED.get( name, None )
		if module is not None: return module
		try: exec( 'import ' + name )
		except ImportError: module = ModuleNotAvailable( name, packageName )
		except: module = ModuleNotAvailable( name, packageName, broken=True )
		else: module = IMPORTED[ module.__name__ ] = sys.modules[ name ]; break
	if registerVersion: RegisterVersion( module )
	return module

def Unimport( *names ):
	names = [ getattr( name, '__name__', name ) for name in names ]
	prefixes = tuple( [ name + '.' for name in names ] )
	for registry in [ sys.modules, IMPORTED, VERSIONS ]:
		names = [ name for name in registry if name in names or name.startswith( prefixes ) ]
		for name in names: registry.pop( name )

def RegisterVersion( module=None, attribute='__version__', name=None, value=None ):
	if module and not name:
		name = module.__name__
		if attribute.strip( '_' ).lower() != 'version': name += '.' + attribute
	if module and not value:
		value = getattr( module, attribute, None )
	if name and value:
		VERSIONS[ name ] = value
	return module
	
def GetVersions():
	versions = VERSIONS.__class__()
	for k, v in VERSIONS.items():
		if callable( v ): versions.update( v() )
		elif v: versions[ k ] = v
	return versions

def ReportVersions():
	for k, v in GetVersions().items():
		print( '%25s : %r' % ( k, v ) )

def LoadPyplot( interactive=None ):
	matplotlib = plt = Import( 'matplotlib', registerVersion=True )
	if matplotlib: import matplotlib.pyplot as plt
	if matplotlib and interactive is not None: matplotlib.interactive( interactive )
	return plt

RegisterVersion( name='sys', value=sys.version )
RegisterVersion( name='sys.platform', value=sys.platform )
RegisterVersion( name='platform.machine', value=platform.machine() )
RegisterVersion( name='platform.architecture', value=platform.architecture() )
for func in 'win32_ver mac_ver linux_distribution libc_ver'.split():
	try: result = getattr( platform, func )()
	except: result = ( '', )
	if result and result[ 0 ]:
		RegisterVersion( name='platform.' + func, value=result )
