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
import os
import sys
import math
import time
import shlex
import logging
import tempfile
import warnings
import threading
import subprocess

from . import Timing
from . import Dependencies; from .Dependencies import numpy

if sys.version < '3': bytes = str
else: unicode = str; basestring = ( unicode, bytes )
def IfStringThenRawString( x ):    return x.encode( 'utf-8' ) if isinstance( x, unicode ) else x
def IfStringThenNormalString( x ): return x.decode( 'utf-8' ) if str is not bytes and isinstance( x, bytes ) else x

class Logger( object ):
	def __init__( self, filename ):
		self.__starttime = time.time()
		self.__filepattern = os.path.realpath( filename ) if filename else None
		self.__filename = self.__filepattern.format( time.strftime( '%Y%m%d-%H%M%S', time.localtime( self.__starttime ) ) ) if self.__filepattern else None
		self.__level = logging.INFO
		if self:
			logging.basicConfig( filename=self.__filename, level=self.__level, format='# %(asctime)s %(levelname)s: %(message)s' )
			self.Log( filename=self.__filename, starttime=self.__starttime )

	__nonzero__ = __bool__ = lambda self: self.__filename is not None
		
	filename  = property( lambda self: self.__filename )
	starttime = property( lambda self: self.__starttime )
	
	@property
	def text( self ):
		if not self: return ''
		with open( self.__filename, 'rt' ) as fh:
			return fh.read()
		
	def Cat( self ):
		print( self.text )		
	
	def Eval( self ):
		return Read( self.__filename )
	
	def Edit( self ):
		Bang( [ 'edit', self.__filename ] )
	
	def Log( self, *pargs, **kwargs ):
		if not self: return None
		msg = ', '.join( str( x ) for x in pargs )
		for k, v in sorted( kwargs.items() ):			
			msg += '\n%s = %s' % ( k, ReadableRepr( v ) )
		if kwargs: msg += '\n'
		logging.info( msg )
	
	__call__ = Log
	
	def LogTimings( self, timings ):
		if not self: return
		timings = getattr( timings, 'timings', timings )
		filtered = {}
		indices = [ index for index, values in enumerate( zip( *timings.values() ) ) if any( not math.isnan( value ) for value in values ) ]
		for k, v in timings.items():
			if numpy: v = v[ indices ]
			else: v = [ v[ index ] for index in indices ]
			filtered[ k ] = v
		self.Log( timings=filtered )
		
	def LogSystemInfo( self, threaded=True, verbose=False ):
		if not self: return
		if threaded: return threading.Thread( target=self.LogSystemInfo, kwargs={ 'threaded' : False, 'verbose' : verbose } ).start()
		if verbose: sys.stderr.write( '\n%s Querying system info...\n' % time.strftime( '%Y-%m-%d %H:%M:%S' ) )
		self.Log( system_info=SystemInfo() )
		if verbose: sys.stderr.write( '\n%s Finished querying system info.\n' % time.strftime( '%Y-%m-%d %H:%M:%S' ) )
		
def ReadableRepr( x ):
	if isinstance( x, dict ): return '{\n' + ''.join( '\t%r : %s,\n' % ( k, ReadableRepr( v ) ) for k, v in x.items() ) + '}'
	if hasattr( x, 'tolist' ): x = x.tolist()
	if isinstance( x, str ):
		x = x.strip( '\n' )
		if   '\n' in x and '"""' not in x: x = 'r"""\n%s\n"""' % x
		elif '\n' in x and "'''" not in x: x = "r'''\n%s\n'''" % x
		elif "'"  in x and '"'   in x: x = repr( x )
		else:
			if "'" in x:  x = '"%s"' % x
			else:         x = "'%s'" % x
			if '\\' in x: x = 'r' + x
		return x
	return repr( x )
	
def Bang( cmd, shell=False ):
	windows = sys.platform.lower().startswith('win')
	# If shell is False, we have to split cmd into a list---otherwise the entirety of the string
	# will be assumed to be the name of the binary. By contrast, if shell is True, we HAVE to pass it
	# as all one string---in a massive violation of the principle of least surprise, subsequent list
	# items would be passed as flags to the shell executable, not to the targeted executable.
	# Note: Windows seems to need shell=True otherwise it doesn't find even basic things like ``dir``
	# On other platforms it might be best to pass shell=False due to security issues, but note that
	# you lose things like ~ and * expansion
	if isinstance( cmd, str ) and not shell:
		if windows: cmd = cmd.replace( '\\', '\\\\' ) # otherwise shlex.split will decode/eat backslashes that might be important as file separators
		cmd = shlex.split( cmd ) # shlex.split copes with quoted substrings that may contain whitespace
	elif isinstance( cmd, ( tuple, list ) ) and shell:
		quote = '"' if windows else "'"
		cmd = ' '.join( ( quote + item + quote if ' ' in item else item ) for item in cmd )
	try: sp = subprocess.Popen( cmd, shell=shell, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
	except OSError as err: return err, '', ''
	output, error = [ IfStringThenNormalString( x ).strip() for x in sp.communicate() ]
	return sp.returncode, output, error
	
def SystemInfo():
	uname = sys.platform.lower()
	if uname.startswith( 'win' ):
		fh = tempfile.NamedTemporaryFile( suffix='.txt', delete=False );
		fh.close()
		filename = fh.name;
		resultCode, output, error = Bang( [ 'dxdiag', '/whql:off', '/t', filename ] )
		with open( filename, 'rt' ) as fh: output = fh.read()
		os.remove( filename )
	elif uname.startswith( 'darwin' ):
		resultCode, output, error = Bang( 'system_profiler SPHardwareDataType SPDisplaysDataType SPCameraDataType SPPowerDataType SPDiagnosticsDataType SPMemoryDataType SPUniversalAccessDataType' )
	else:
		warnings.warn( 'TODO: no %s support in SystemInfo()' % uname )
		output = None
	return output

def Read( filename ):
	d = {}
	g = globals()
	g[ 'inf' ] = float( 'inf' )
	g[ 'nan' ] = float( 'nan' )
	with open( filename, 'rt' ) as fh: exec( fh.read(), g, d )
	return d
