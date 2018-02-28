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
	'BackEnd',
	'ReportVersions',
	'Screens',
	'PackagePath',
	'World',
	'Stimulus',
	'LookupTable',
	'IsShadyObject',
	'AddCustomSignalFunction',
	'AddCustomModulationFunction',
	'SINEWAVE_SF', 'SINEWAVE_MF',
	'DRAWMODE',
]

# Python standard library modules
import os
import re
import sys
import time
import glob
import math
import ctypes
import inspect
import weakref
import platform
import functools
import threading
import traceback
import subprocess
import collections

# sibling sub-module imports
from . import Timing
from . import Logging
from . import PyEngine
from . import PropertyManagement; from .PropertyManagement import ClassWithManagedProperties, ManagedProperty, ManagedShortcut
from . import DependencyManagement

# global defs
MAX_TEXTURE_EXTENT = 8192 # TODO: found this empirically to be 16284 on Surface Pro and 8192 on MacBook; how to query it properly?   GL.glGetIntegerv( MAX_TEXTURE_SIZE )?
MAX_POINTS = 20000

SINEWAVE_SF = 1  # index of the one built-in signal function in the shader (SinewaveSignal)
SINEWAVE_MF = 1  # index of the one built-in modulation function in the shader (SinewaveModulation)

class DRAWMODE( object ):
	POINTS     = -2
	LINES      = -3
	LINE_STRIP = -4
	POLYGON    = -5

# home-made 'six'-esque stuff:
try: apply
except NameError: apply = lambda x: x()
try: FileNotFoundError
except NameError: FileNotFoundError = IOError
if sys.version < '3': bytes = str
else: unicode = str; basestring = ( unicode, bytes )
def IfStringThenRawString( x ):    return x.encode( 'utf-8' ) if isinstance( x, unicode ) else x
def IfStringThenNormalString( x ): return x.decode( 'utf-8' ) if str is not bytes and isinstance( x, bytes ) else x
def reraise( cls, instance, tb=None ): raise ( cls() if instance is None else instance ).with_traceback( tb )
try: Exception().with_traceback
except: exec( 'def reraise( cls, instance, tb=None ): raise cls, instance, tb' ) # has to be wrapped in exec because this would be a syntax error in Python 3.0
class DeferredException( object ):
	def __init__( self, cls, instance, tb=None ): self.cls, self.instance, self.tb = cls, instance, tb
	def __call__( self ): reraise( self.cls, self.instance, self.tb )

def PackagePath( relative_path ):
	"""
	Return an absolute path to a file whose location is specified relative to the
	package root directory (which is assumed to be the parent directory of this file).
	"""
	try: frame = inspect.currentframe(); here = os.path.dirname( inspect.getfile( frame ) )
	finally: del frame # https://docs.python.org/3/library/inspect.html#the-interpreter-stack
	return os.path.realpath( os.path.join( here, relative_path ) )

def GetRevision():
	hgrev = '@HGREV@'
	if hgrev.startswith( '@' ):
		hgrev = 'unknown revision'
		try: sp = subprocess.Popen( [ 'hg', 'id', '-intb', PackagePath( '..' ) ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False )
		except OSError: pass
		else:
			out, err = sp.communicate()
			if sp.returncode == 0: hgrev = IfStringThenNormalString( out ).strip()
	return hgrev

__version__ = open( PackagePath( 'VERSION' ), 'rt' ).read().strip()
DependencyManagement.RegisterVersion( name='Shady', value=( __version__, GetRevision() ) )

# third-party package imports
from . import Dependencies; from .Dependencies import numpy, Image, ImageGrab

_windowing_backend_requested = None
_windowing_backend_loaded = None
_acceleration_preference = 'auto-silent'
Windowing = None
ShaDyLib = None

def PrintStack( limit=None ):
	try:
		frame = inspect.currentframe()
		outerframes = inspect.getouterframes( frame )
		traceback.print_stack( outerframes[ 2 ][ 0 ], limit=limit )
		print( '' )
	finally:
		del outerframes, frame # https://docs.python.org/3/library/inspect.html#the-interpreter-stack

# C++ acceleration
def LoadAccelerator( preference=None ):
	"""
	See `BackEnd()`.
	"""
	global ShaDyLib
	if preference in [ True ] and ShaDyLib is not None: return ShaDyLib  
	develDir = PackagePath( '../../accel-src/release' )
	develLoaded = ShaDyLib is not None and inspect.getfile( ShaDyLib ).startswith( develDir )
	bundledLoaded = ShaDyLib is not None and not develLoaded
	if preference in [ False ] or ( preference in [ 'bundled' ] and not bundledLoaded ) or ( preference in [ 'devel' ] and not develLoaded ):
		ShaDyLib = None
		sys.modules.pop( 'ShaDyLib', None )
		sys.modules.pop( 'Shady.ShaDyLib', None )
		if develDir in sys.path: sys.path.remove( develDir )
		# Tabula rasa in theory but note that this can cause strange bugs where module members become None when imported a second time (at least on OSX under anaconda 2.7.12 - also reported in a comment by Olivier Verdier at https://stackoverflow.com/a/2918951/ )
	if preference in [ 'devel', 'auto', 'auto-silent', True ]:
		if os.path.isdir( develDir ):
			sys.path.insert( 0, develDir )
			try: import ShaDyLib
			except ImportError: pass
			sys.path.remove( develDir )
		if ShaDyLib:
			if preference in [ 'auto', True ]: print( 'Shady accelerated using development library %r' % ShaDyLib.dll._name )
			return ShaDyLib
		if preference in [ 'devel' ]: raise ImportError( 'failed to import development version of ShaDyLib accelerator' )
	if preference in [ 'bundled', 'auto', 'auto-silent', True ]:
		try: from . import accel; from .accel import ShaDyLib
		except ImportError:
			if preference in [ 'bundled' ]: raise ImportError( 'failed to import bundled version of ShaDyLib accelerator' )
		if ShaDyLib:
			if preference in [ 'auto', True ]: print( 'Shady accelerated using bundled library %r' % ShaDyLib.dll._name )
			return ShaDyLib
	elif preference not in [ None, False ]:
		raise ValueError( 'unrecognized accelerator preference %r' % preference )
	if not ShaDyLib:
		if preference in [ True ]: raise ImportError( 'failed to import ShaDyLib accelerator' )
		if preference in [ 'auto' ]: print( 'Shady is running without acceleration' )
	return ShaDyLib

def BackEnd( windowing=None, acceleration=None ):
	"""
	Globally specify the back-end windowing and rendering systems that future
	`World` instances should use.

	Args:
	    windowing:
	        specifies the windowing system. Possible values are as follows:
	    
	        `'default'`:
	              use the ShaDyLib dynamic library if available, else fall back
	              on pyglet.
	        `'shadylib'`, `'accel'`, or `'glfw'`:
	              use the ShaDyLib dynamic library (windowing is handled via the
	              GLFW library from http://glfw.org ).
	        `'pyglet'`:
	              use pyglet (a third-party package that you will need
	              to install separately if you want to use this option)
	        `'pygame'`:
	              use pygame (a third-party package that you will need
	              to install separately if you want to use this option)
	    
	    acceleration:
	        specifies the rendering implementation, i.e. whether to use the ShaDyLib
	        dynamic library (and if so, whether to use the "development" copy of
	        ShaDyLib in cases where you have the entire Shady repository including
	        the C++ sources for ShaDyLib) or whether to fall back on Python code
	        for rendering (not recommended). Possible values are:

	        `None`:
	              leave things as they were (default).
	        `False`:
	              disable ShaDyLib and fall back on the `pyglet` or `PyOpenGL`
	              code in the `PyEngine` submodule (this option is not
	              recommended for time-critical presentation).
	        `True`:
	              if ShaDyLib is already imported, leave things as they are;
	              if not, import either version of ShaDyLib or die trying.
	              Prefer the development version, if available. Print the
	              outcome.
	        `'bundled'`:
	              silently import the bundled version of ShaDyLib from the
	              Shady.accel sub-package, or die trying.
	        `'devel'`:
	              silently import the development version of ShaDyLib from
	              `../../accel-src/release/`, or die trying.
	        `'auto'`:
	              try to import ShaDyLib. Prefer the development version,
	              if available. Don't die in the attempt. Whatever happens,
	              print the outcome.
	
	Returns:
	    If both input arguments are `None`, the name of the current windowing backend is returned.
	    Otherwise, returns `None`.
	"""
	global _windowing_backend_requested, _acceleration_preference
	if windowing is None and acceleration is None: return _windowing_backend_requested
	if windowing is None: windowing = _windowing_backend_requested
	if windowing is not None:
		windowing = windowing.lower()
		if windowing.endswith( 'windowing' ): windowing = windowing[ :-9 ]
		if windowing == 'default': windowing = 'shadylib'
		if windowing in [ 'accel', 'shadylib', 'glfw' ]:
			if acceleration == False: raise ValueError( 'cannot set acceleration=False if using %r back-end for windowing' % windowing )
			if acceleration is None: acceleration = _acceleration_preference
			if acceleration is None: acceleration = True
			windowing = 'shadylib'
		_windowing_backend_requested  = windowing
	if acceleration is not None:
		_acceleration_preference = acceleration
	
def LoadBackEnd():
	# Load (import) the active windowing backend as configured by `BackEnd()`.
	global Windowing, _windowing_backend_loaded
	if _windowing_backend_requested is None: BackEnd( 'default', _acceleration_preference )
	LoadAccelerator( _acceleration_preference )
	if _windowing_backend_requested == 'shadylib' and not ShaDyLib: raise ImportError( 'failed to import ShaDyLib accelerator, which is required when using the "shadylib" windowing option' )
	if _windowing_backend_requested == _windowing_backend_loaded: return Windowing
	elif _windowing_backend_requested == 'pyglet':   from . import PygletWindowing   as Windowing
	elif _windowing_backend_requested == 'pygame':   from . import PygameWindowing   as Windowing
	elif _windowing_backend_requested == 'shadylib': from . import ShaDyLibWindowing as Windowing; # NB: requires accelerator to be loaded here
	else: raise ValueError( 'unsupported back-end module %r' % _windowing_backend_requested )
	_windowing_backend_loaded = _windowing_backend_requested
	Windowing.Window.TabulaRasa()
	return Windowing

def Screens( pretty_print=False ):
	"""
	Get details of any attached screens using the `Screens()` method
	of whichever windowing backend is enabled.

	Args:
		pretty_print (bool): determines the type of the return value
	
	Returns:
		If `pretty_print` is `True`, returns a human-readable string.
		If `pretty_print` is `False`, returns a `dict`.
	"""
	LoadBackEnd()
	return Windowing.Screens( pretty_print=pretty_print )

def ReportVersions( world=None, outputType='print' ):
	"""
	Report versions of all dependencies, including:
	
		* the windowing backend (pyglet, pygame, or ShaDyLib)
		* the acceleration backend (ShaDyLib)
		* any other dependencies managed by Shady, such as `numpy`.
	
	Args:
	    world (World): optional `Shady.World` instance (if supplied,
	                   more information can be provided).
	    outputType (str): may be `'dict'`, `'string'` or `'print'`
	
	Returns:
	    Depending on `outputType`, may return a `dict` or a string
	    detailing Shady's various subcomponents and dependencies and 
	    their version information.
	"""
	LoadBackEnd()
	versions = DependencyManagement.GetVersions()
	versions[ 'backend' ] = _windowing_backend_loaded
	if world:
		versions[ 'backend' ] = world.backend
		versions.update( getattr( world.window, 'versions', {} ) )
		versions.update( getattr( world._accel, 'versions', {} ) )
	global ShaDyLib
	if ShaDyLib:
		accel = ShaDyLib.dll._name.replace( '\\', '/' )
		root = PackagePath( '..' ).replace( '\\', '/' ).rstrip( '/' ) + '/'
		if accel.startswith( root ): accel = accel[ len( root ): ]
		if world is None or 'ShaDyLib' in versions: # yes, that is what I mean
			versions[ 'ShaDyLib' ] = ( ShaDyLib.GetVersion(), ShaDyLib.GetRevision(), accel )
	if outputType in [ 'dict', dict ]: return versions
	s = '\n'.join( '%30r : %r,' % item for item in versions.items() )
	if outputType in [ 'str', 'string', str ]: return s
	elif outputType == 'print': print( s )
	else: raise ValueError( 'unrecognized output type %r' % outputType )

def DeferredCall( func, context=None ):
	@functools.wraps( func )
	def deferred( self, *pargs, **kwargs ):
		world = getattr( self, 'world', self )
		if callable( world ): world = world() # weakref de-ref
		if world._parentThread in [ None, threading.current_thread() ]:
			return func( self, *pargs, **kwargs )
		container = world._Defer( func, self, *pargs, **kwargs )
		while not container and world.state not in [ 'finished', 'closed' ]: time.sleep( 0.001 )
		result = container[ 0 ] if container else None
		if isinstance( result, DeferredException ): result()
		return result
	return deferred
			
def ExceptionHook( name, exc, tb ):	
	hook = sys.excepthook
	if 'IPython' in sys.modules:
		# Wrestle with the IPython devs, goalpost-movers extraordinaires:
		try: from IPython.core.ultratb import ColorTB
		except ImportError: pass
		else: hook = ColorTB()
		try: from IPython.ultraTB import ColorTB
		except ImportError: pass
		else: hook = ColorTB()
		
	stem = PackagePath( '.' )
	extracted = list( traceback.extract_tb( tb ) )
	first_of_interest = 1 + max( [ i for i, f in enumerate( extracted ) if f[ 0 ].startswith( stem ) ] + [ -1 ] )
	if first_of_interest < len( extracted ):
		for i in range( first_of_interest ): tb = tb.tb_next
	hook( name, exc, tb )

def PartialTranslation( v, p ):
	return math.floor( ( 0.5 + 0.5 * p ) * v )

def StimulusSortKey( stim ):
	return ( -getattr( stim, 'z', 0 ) - getattr( stim, 'oz', 0 ), getattr( stim, 'serialNumber', 0 ) )

class ProfileContextManager( object ):
	def __init__( self, mode=True ):
		self.nFrames = 0
		self.mode = mode
		if self.mode == 'pyinstrument':
			pyinstrument = DependencyManagement.Import( 'pyinstrument' )
			self.profile = pyinstrument.Profiler( use_signal=not sys.platform.lower().startswith( 'win' ) )
		elif self.mode:
			import cProfile
			self.profile = cProfile.Profile()
		else:
			self.profile = None
	def __enter__( self ):
		if not self.profile: return
		if self.mode == 'pyinstrument': self.profile.start()
		else: self.profile.enable()
	def __exit__( self, etype, einst, tb ):
		if not self.profile: return
		if self.mode == 'pyinstrument': self.profile.stop()
		else: self.profile.disable()
		self.nFrames += 1
	def stats( self, nFrames=1 ):
		if not self.profile: return None
		if self.mode == 'pyinstrument':
			def MsecPerFrame( f ):
				if hasattr( f, '_time' ): del f._time
				if not hasattr( f, '_total_self_time' ): f._total_self_time = f.self_time
				f.self_time = f._total_self_time * 1000.0 / self.nFrames
				for child in f.children: MsecPerFrame( child )
			MsecPerFrame( self.profile.starting_frame() )
			return self.profile
		else:
			import pstats
			return pstats.Stats( self.profile ).sort_stats( 'cumtime' ) 
			# TODO: normalize stats to msec per frame somehow....
			
def IsShadyObject( obj ):
	return bool( getattr( obj, '_isShadyObject', False ) )

	
@ClassWithManagedProperties._Organize
class LinkGL( ClassWithManagedProperties ):
	"""
	Superclass for the `World`, `Stimulus` and `LookupTable` classes, whose principal
	function is to allow easy transfer of 1-, 2-, 3- or 4-dimensional OpenGL parameters.	
	"""
	
	_isShadyObject = True
		
	def _Initialize( self, world, debugTiming=False ):
		self.world = weakref.ref( world )
		if debugTiming is None: debugTiming = getattr( world, 'debugTiming', False )
		self.debugTiming = debugTiming
		self.verbose = 0
		self.excepthook = ExceptionHook
		if not self._accel: PyEngine.SetUpProperties( self, world=world ) # copies default values into place, AND sets up transfers
	
	def _Accelerate( self, accel, **preserve ): 
		if not accel: return None
		preserve = { k : v * 1 for k, v in preserve.items() }
		if hasattr( accel, 'MakeCustomUniform' ):
			for prop in getattr( self, '_custom_properties', [] ):
				accel.MakeCustomUniform( prop.name, int( prop.transfer[ -2 ] ), prop.transfer[ -1 ] == 'f' )
				preserve[ prop.name ] = getattr( self, prop.name )
		for prop in self.Properties( False ):
			try: prop_accel = accel.GetProperty( prop.name )
			except: pass; print( 'failed to accelerate %s.%s' % ( self.__class__.__name__, prop.name ) )
			else:
				array = PropertyManagement.WrapPropertyArray( prop_accel.A, prop )
				prop.determine_array( self, array=array )#; print( 'accelerated %s.%s = %s' % ( self.__class__.__name__, prop.name, array ) )
		self.Set( **preserve )
		if hasattr( accel, 'SetUpdateCallback' ): # only Renderer objects will have this method
			self._accel_callback = ShaDyLib.UpdateCallback( self._FrameCallback )  # must assign this wrapped object as an attribute here, otherwise the garbage-collector will get it and the callback will cause a segfault when it happens
			accel.SetUpdateCallback( self._accel_callback, 0 )
		return accel

	def _RedirectProperty( self, propertyName, targetInstance, targetArray=None ):
		# overshadows superclass method ClassWithManagedProperties._RedirectProperty
		if not getattr( self, '_accel', None ): return ClassWithManagedProperties._RedirectProperty( self, propertyName=propertyName, targetInstance=targetInstance, targetArray=targetArray )
		# ...but only if there is a self._accel
		p = self._accel.GetProperty( propertyName )
		descriptor = self.GetPropertyDescriptor( propertyName )
		if targetInstance is None or targetInstance is self: p.MakeIndependent( 0 )
		else: p.LinkWithMaster( targetInstance._accel.GetProperty( propertyName )._ptr )
		descriptor.determine_array( self, name=propertyName, array=p.A )
	
	def _Record( self, key, value=None, origin=0.0, factor=1.0, bufferSize=36000 ):
		if value is None: value = self.world()._Clock()
		if not hasattr( self, 'timings' ): self.timings = Bunch()
		array = self.timings.get( key, None )
		if array is None:
			if numpy: array = numpy.zeros( [ bufferSize ], dtype=float ) + numpy.nan
			else: array = [ float( 'nan' ) ] * bufferSize
			self.timings[ key ] = array
		array[ self.framesCompleted % len( array ) ] = ( value - origin ) * factor
		return value
		
	def _DebugTiming( self, key, timeInSeconds=None, origin=None ):
		world = self.world()
		if origin is None: origin = world._drawTime
		return world._Record( self._Description().replace( ' ', '_' ).replace( "'", '' ).replace( '"', '' ) + '_' + key, value=timeInSeconds, origin=origin, factor=1000.0 )
		
	def _Description( self ):
		desc = self.__class__.__name__
		name = getattr( self, 'name', '' )
		if name: desc += ' %r' % name
		return desc	
	
	def __str__( self ): return self._Description()
	def __repr__( self ): return '<%s @ 0x%08x>' % ( self._Description(), id( self ) )
		
	def _CallAnimate( self, t ):
		try:
			self.Animate( t )
		except:
			einfo = sys.exc_info()
			method = self.Animate
			self.SetAnimateMethod( None )
			if method:
				sys.stderr.write( 'Exception during .Animate() callback of %r:\n' % self )
				ExceptionHook( *einfo )
	
	def _SetCallableAttribute( self, name, func, numberOfArgsAfterSelf ):
		if func is None: func = getattr( type( self ), name )
		if func is None: setattr( self, name, func ); return self
		try: inspect.getfullargspec
		except: args = inspect.getargspec( func ).args
		else:   args = inspect.getfullargspec( func ).args
		if len( args ) == numberOfArgsAfterSelf + 1:
			if not hasattr( func, '__self__' ): func = func.__get__( self, type( self ) )
			if func.__self__ is not self: func = func.__func__.__get__( self, type( self ) )
		elif len( args ) != numberOfArgsAfterSelf:
			raise TypeError( '%r function should have either %d arguments (if the first is `self`) or %d (if omitting `self`)' % ( name, numberOfArgsAfterSelf + 1, numberOfArgsAfterSelf ) )
		setattr( self, name, func )
		return self
	
	Animate = None
		
	def SetAnimateMethod( self, callback ):
		"""
		DOC-TODO
		"""
		return self._SetCallableAttribute( 'Animate', callback, numberOfArgsAfterSelf=1 )
		
	def SetVerbosity( self, n, sleep=0.0, propagate=True ):
		"""
		DOC-TODO
		"""
		self.verbose = n
		if not propagate: return
		if hasattr( self, 'stimuli' ):
			for stim in self.stimuli.values(): stim.SetVerbosity( n, sleep=0.0, propagate=True )
		if sleep: time.sleep( sleep )
	
	def Place( self, xp, yp=None, worldCoordinates=True, polar=False ):
		"""
		Convert 2-D normalized coordinates (relative to the instance, -1 to +1 in each
		dimension), into 2-D pixel coordinates, either relative to the `World`'s current
		`.anchor`, or relative to the `World`'s bottom left corner irrespective of `.anchor`.
		
		Input coordinates may be given as one scalar argument,  two scalar arguments, or
		one argument that is a sequence of two numbers.  Depending on the `polar` argument,
		these will be interpreted as `x, y` Cartesian coordinates (where, if `y` omitted,
		it defaults to `y=x`)  or `theta, r` polar coordinates (where, if `r` is omitted,
		it defaults to `r=1`).
		
		Args:
		    worldCoordinates (bool):
		        If `True`, return pixel coordinates relative to the `World`'s own `.anchor`
		        position.  If `False`, return pixel coordinates relative to the `World`'s
		        bottom left corner irrespective of its `.anchor`.
		        
		    polar (bool):
		        If `True`, input coordinates are interpreted as an angle (in degrees) and
		        an optional radius (0 denoting the center, 1 denoting the edge).
		
		Examples::
			
		    instance.Place( [ -1, 1 ] )      # top left corner
		    instance.Place( -1, 1 )          # likewise, top left corner
		    instance.Place( 90, polar=True )  # middle of top edge (radius 1 assumed)
		    instance.Place( [ 90, 0.5 ], polar=True )  # halfway between center and top
		    instance.Place( 90, 0.5, polar=True )  # likewise, halfway between center and top
		        
		"""
		( x0, y0 ), ( w, h ) = self.BoundingBox( worldCoordinates=worldCoordinates )
		if polar:
			theta, r = xp, yp
			if r is None:
				try: theta, r = theta
				except: r = 1.0
			theta *= math.pi / 180.0
			xp = r * math.cos( theta )
			yp = r * math.sin( theta )
		elif yp is None:
			try: xp, yp = xp
			except: yp = xp
		x = x0 + PartialTranslation( w, xp )
		y = y0 + PartialTranslation( h, yp )
		if numpy: return numpy.array( [ x, y ] )
		else: return [ x, y ]
		
	@classmethod
	def AddCustomUniform( cls, name=None, defaultValue=None, **kwargs ):
		"""
		DOC-TODO
		"""
		props = []
		for name, defaultValue in [ ( name, defaultValue ) ] + list( kwargs.items() ):
			if defaultValue is None or not name: continue
			prop = ManagedProperty( names=name.split(), default=defaultValue )
			floatingPoint = True in [ isinstance( x, float ) for x in prop.default ]
			numberOfElements = len( prop.default )
			if numberOfElements == 1:
				if floatingPoint: uType = 'float'; prop.transfer =  'glUniform1f'
				else:             uType = 'int'  ; prop.transfer =  'glUniform1i'
			else:
				uType = 'vec%d' % numberOfElements
				prop.transfer =  'glUniform%df' % numberOfElements # TODO: in later GLSL versions we could have integer vectors
				if numberOfElements not in [ 2, 3, 4 ]: raise ValueError( 'new property must have 1, 2, 3 or 4 elements' )
			cls._AddCustomProperty( prop, index=-1 )
			fieldname = '_custom_properties'
			registry = getattr( cls, fieldname, [] )
			setattr( cls, fieldname, registry )
			registry.append( prop )
			uName = 'u' + prop.name[ 0 ].upper() + prop.name[ 1: ]
			World._substitutions[ 'CUSTOM_UNIFORMS' ][ prop.name ] = 'uniform %s %s;' % ( uType, uName )
			props.append( prop )
		return props

def AddCustomSignalFunction( code ):
	"""
	DOC-TODO
	"""
	return _AddCustomFunction( code, 'SIGNAL_FUNCTION_CALLS', 'uSignalFunction', [ 'float', 'vec3' ],
		'signal = TintSignal( {functionName}( xy ), uColor );' )
	
def AddCustomModulationFunction( code ):
	"""
	DOC-TODO
	"""
	return _AddCustomFunction( code, 'MODULATION_FUNCTION_CALLS', 'uModulationFunction' )

def AlternativesString( sequence, transformation=repr, conjunction='or' ):
	sequence = [ transformation( x ) for x in sequence ]
	return ', '.join( sequence[ :-1 ] ) + ( ( ' %s ' % conjunction ) if len( sequence ) > 1 else '' ) + sequence[ -1 ]

def _AddCustomFunction( code, switchSection, switchName, returnTypes=( 'float', ), functionCall='f = {functionName}( xy );' ):
	tokens = re.findall( r'\w+|[^\w\s]+', code )
	returnType, functionName, openParenthesis, inputType, inputName, closeParenthesis = ( tokens + [ '' ] * 6 )[ :6 ]
	if openParenthesis != '(': raise ValueError( 'must start with a valid function prototype' );
	if returnType not in returnTypes: raise ValueError( 'function must return type %s' % AlternativesString( returnTypes, lambda x: '`%s`' % x ) );
	if inputType != 'vec2' or closeParenthesis != ')': raise ValueError( 'must be a function of a single `vec2` typed input' );
	bodyRegistry = World._substitutions[ 'CUSTOM_FUNCTIONS' ]
	#if code != bodyRegistry.get( functionName, code ): raise ValueError( 'code does not match previously-registered definition of custom function %s' % functionName )
	bodyRegistry[ functionName ] = code
	switchRegistry = World._substitutions[ switchSection ]
	offset = 2 # 0 is no function, 1 is SinewaveSignal or SinewaveModulation
	if functionName in switchRegistry: return offset + list( switchRegistry.keys() ).index( functionName )
	switchNumber = offset + len( switchRegistry )
	switchCode = '\telse if( {switchName} == {switchNumber} ) {{' + functionCall + '}}'
	switchCode = switchCode.format( switchName=switchName, switchNumber=switchNumber, functionName=functionName )
	switchRegistry[ functionName ] = switchCode
	return switchNumber	

@ClassWithManagedProperties._Organize
class World( LinkGL ):
	
	_substitutions = collections.defaultdict( collections.OrderedDict )
	
	def __init__( self, width=None, height=None, window=None, left=None, top=None, screen=None, threaded=True, canvas=False, frame=False, fullScreenMode=None, visible=True, openglContextVersion=0, backend=None, acceleration=None, debugTiming=False, profile=False, logfile=None, **kwargs ):
		"""
		First 1-2 constructor argument(s)::
		
			r = World( window )
		
		where `window` is a Window instance from one of the windowing submodules, or::
		
			r = World( [ width, height ] )
			r = World( width, height )    
			
		where `width` and `height` are expressed in pixels.
		
		Managed properties can also be specified as optional keyword arguments, e.g.::
		
			r = World( ..., clearColor=[0,0,0.5] )
			
		"""
		
		self.__state = 'starting'
		self.__pending = []
		self.__onClose = []
		self.__fakeFrameRate = 0.0
		self.t0 = None
		
		self.logger = Logging.Logger( logfile )
		
		if backend is not None or acceleration is not None: BackEnd( backend, acceleration )
		kwargs.update( dict( width=width, height=height, window=window, left=left, top=top, screen=screen, canvas=canvas, frame=frame, fullScreenMode=fullScreenMode, visible=visible, openglContextVersion=openglContextVersion, debugTiming=debugTiming, profile=profile ) )
		if threaded and not sys.platform.lower().startswith( ( 'win', ) ):
			threaded = False
			print( 'Cannot run in a background thread on %s. Running in main thread - so remember to call .Run()' % sys.platform )
		self.threaded = threaded
		
		
		if self.logger:
			sys.stderr.write( 'Logging to %s\n' % self.logger.filename )
			self.logger.Log( world_construction=kwargs )
			self.OnClose( self.logger.LogTimings, self )
			self.OnClose( self.logger.LogSystemInfo, threaded=True, verbose=True )
			#self.logger.LogSystemInfo( threaded=True, verbose=True )
			
		if threaded:
			self._fatal = None
			def ConstructorThread():
				try: self._Construct( **kwargs )
				except: self._fatal = sys.exc_info(); return
				try: self.Run()
				except: self._fatal = sys.exc_info(); return
			self.thread = threading.Thread( target=ConstructorThread )
			self.thread.start()
			while self.__state != 'running' and self.thread.is_alive(): time.sleep( 0.1 )
			if self._fatal: reraise( *self._fatal )
		else:
			self.thread = None
			self._Construct( **kwargs )
			
	def _Construct( self, width, height, window, left, top, screen, canvas, frame, fullScreenMode, visible, openglContextVersion, debugTiming, profile, **kwargs ):
		# NB: if `window` is supplied, `width`, `height` and `size` arguments will be ignored
		size = kwargs.pop( 'size', None )
		if not window:
			if size is not None:
				if width is None or width <= 0:
					try: width, blah = size
					except: width = size
				if height is None or height <= 0:
					try: blah, height = size
					except: height = size
			if height is None or height <= 0:
				try: width, height = width
				except: height = width
			window = LoadBackEnd().Window
			
		glslDirectory = PackagePath( 'glsl' )
		substitutions = '\n'.join( '//#%s\n%s' % ( key, '\n'.join( entries.values() ) ) for key, entries in self._substitutions.items() if entries )
		
		if callable( window ):
			window_kwargs = dict( screen=screen, frame=frame, fullScreenMode=fullScreenMode, visible=visible, openglContextVersion=openglContextVersion )
			if width  not in [ -1, None ]: window_kwargs[ 'width'  ] = width
			if height not in [ -1, None ]: window_kwargs[ 'height' ] = height
			if left   not in [ -1, None ]: window_kwargs[ 'left'   ] = left
			if top    not in [ -1, None ]: window_kwargs[ 'top'    ] = top
			if getattr( window, 'accelerated', False ):
				window_kwargs[ 'glslDirectory' ] = glslDirectory
				window_kwargs[ 'substitutions' ] = substitutions
				
			if hasattr( window, 'TabulaRasa' ): window.TabulaRasa()
			window = window( **window_kwargs )
		self.window = window
		self.window.excepthook = ExceptionHook
		self.window.on_close = self.RunOnClose
		self.width, self.height = self.window.width, self.window.height
		
		self._parentThread = threading.current_thread()
		self.profile = ProfileContextManager( profile )
		
		if ShaDyLib:
			if getattr( self.window, 'accelerated', False ):
				# accelerated windowing and accelerated rendering: Never even calls self._Draw - the
				# only Python code that will be called on each frame is self._FrameCallback, after all
				# Shady-mode drawing is done. In this case the Window will have already created a Renderer
				# instance and called InitShading
				self._accel = self._Accelerate( self.window.GetRenderer(), size=self.size )
			else:
				# non-accelerated windowing, accelerated rendering: the Window is implemented by a Python wrapper
				# (pyglet, pygame)... and it calls the Python method self._Draw on each frame, which, instead of
				# doing most of its normal thing in Python, will detect the presence of self._accel and call the DLL
				# function self._accel.Draw(). That will in turn draw the Stimulus objects without
				# leaving the binary.
				self._program = ShaDyLib.InitShading( self.width, self.height, glslDirectory, substitutions )
				self._accel = self._Accelerate( ShaDyLib.Renderer( shaderProgram=self._program ), size=self.size )
				#if getattr( self.window, 'needs_help_with_vbl', False ): self._accel.SetSwapInterval( 1 ) # or -1....
		else:
			# non-accelerated mode: no ShaDyLib, so everything is done from Python via the PyEngine sub-module.
			self._program = PyEngine.InitShading( self.width, self.height, glslDirectory, substitutions )
			self._accel = None
			self._slots = list( range( PyEngine.GetNumberOfTextureSlots() ) )
			#if getattr( self.window, 'needs_help_with_vbl', False ): PyEngine.GL.UseVBL() - fails
				
		self.stimuli = Bunch()
		self._Initialize( world=self, debugTiming=debugTiming ) # includes initialization of transfer list, for non-accelerated objects		
		prep = { k : kwargs.pop( k ) for k in list( kwargs.keys() ) if not hasattr( self, k ) }
			
		self.backend = self.window.__module__.split( '.' )[ -1 ].lower()
		if self.backend.endswith( 'windowing' ): self.backend = self.backend[ :-len( 'windowing' ) ]
		self.versions = ReportVersions( world=self, outputType='dict' )
		if self.logger: self.logger.Log( '\nversions = {\n%s\n}\n' % self.ReportVersions( outputType='string' ) )
		
		self.Set( **kwargs )
		if canvas: self.MakeCanvas()
		self.Prepare( **prep )
		
	def Prepare( self, **kwargs ):
		"""
		DOC-TODO
		"""
		if kwargs: print('.Prepare() arguments:')
		for item in sorted( kwargs.items() ): print( '  %s = %r' % item )
		
	def OnClose( self, func, *pargs, **kwargs ):
		"""
		DOC-TODO
		"""
		container = []
		self.__onClose.append( ( func, pargs, kwargs, container ) )
		return container
		
	def CancelOnClose( self, container ):
		"""
		DOC-TODO
		"""
		self.__onClose = [ item for item in self.__onClose if item[ -1 ] is not container ]
	
	def RunOnClose( self ):
		"""
		DOC-TODO
		"""
		while self.__onClose:
			func, pargs, kwargs, container = self.__onClose.pop( 0 )
			try: container.append( func( *pargs, **kwargs ) )
			except: self.excepthook( *sys.exc_info() )
	
	def CreatePropertyArray( self, propertyName, *stimuli ):
		"""
		DOC-TODO
		"""
		stimuli = [ stimulus for x in stimuli for stimulus in ( x if isinstance( x, ( tuple, list ) ) else x.split() if hasattr( x, 'split' ) else [ x ] ) ]
		stimuli = [ ( self.stimuli[ x ] if isinstance( x, basestring ) else x ) for x in stimuli ]
		stimulusNames = [ stimulus.name for stimulus in stimuli ]
		propertyName = stimuli[ 0 ].GetPropertyDescriptor( propertyName ).name # canonicalize
		if not numpy: raise ImportError( 'to create property arrays, you will need the third-party package "numpy"' )
		if self._accel:  propertyArray = self._accel.CreatePropertyArray( propertyName, ' '.join( stimulusNames ) )
		else: propertyArray = PyEngine.PropertyArray( propertyName, stimuli );
		propertyArray.stimulusNames = stimulusNames
		propertyArray.propertyName = propertyName
		for stimulus, row in zip( stimuli, propertyArray.A ):
			descriptor = stimulus.GetPropertyDescriptor( propertyName )
			descriptor.determine_array( stimulus, name=propertyName, array=row )
			# TODO: this needs to be undone whenever an instance of PropertyArray (the class from ShaDyLib.py and the one from PyEngine.py) is destroyed...
		return propertyArray
		
	def _ProcessEvent( self, event ):
		# this indirect path to self.HandleEvent serves two purposes:
		# (1) it allows the HandleEvent method to be changed on the fly, using SetEventHandler
		# (2) it allows x and y coordinates to be transformed according to the World origin
		if event.x is not None: event.x -= PartialTranslation( self.size[ 0 ], self.anchor[ 0 ] )
		if event.y is not None: event.y -= PartialTranslation( self.size[ 1 ], self.anchor[ 1 ] )
		self.HandleEvent( event )
		
	def HandleEvent( self, event ):
		"""
		This method is called every time an event happens.  Its argument
		`event` is a standardized instance of class `Event`, containing
		details of what happened. The default (superclass) implementation
		responds when `event.type` is `'key_release'` and the released key
		is either the Q key or the escape key - this causes the window to
		close (and hence the drawing thread will terminate, if this `World`
		is threaded).

		Overshadow this method in your `World` subclass, or by using
		`.SetEventHandler()` - for example::
		
			def handler( self, event ):
			    print( event )
			w.SetEventHandler( handler )
			
		"""
		#print( event )
		if event.type == 'key_release' and event.key in [ 'escape', 'q' ]: self.window.Close()
		
	def SetEventHandler( self, handler ):
		"""
		Bind `handler` as the instance's event handler in place of the
		default `HandleEvent` method, (or, if `handler` is `None`, revert
		to the default `HandleEvent` method).
		
		The prototype for an event handler can be `handler(self, event)`
		or just `handler(event)`.
		"""
		return self._SetCallableAttribute( 'HandleEvent', handler, numberOfArgsAfterSelf=1 )
	
	def BoundingBox( self, worldCoordinates=False ):
		"""
		DOC-TODO
		"""
		w, h = self.size
		return [
			PartialTranslation( -w, self.anchor[ 0 ] ) if worldCoordinates else 0,
			PartialTranslation( -h, self.anchor[ 1 ] ) if worldCoordinates else 0,
		], [ w, h ]
		
	def _Draw( self, dt=None, t=None ):
		with self.profile:
			if self._accel: self._accel.Draw()
			else:           PyEngine.DrawWorld( self, dt=dt, t=t )
		
	def Run( self ):
		"""
		DOC-TODO
		"""
		if self.__state == 'running':
			while self.__state == 'running': time.sleep( 0.020 )
			return self
		self.__state = 'running'
		self.window.Run( render_func=self._Draw, event_func=self._ProcessEvent )
		self.pstats = self.profile.stats()
		self.__state = 'finished'
		return self
	
	@property
	def shady_stimuli( self ): return { k : v  for k, v in self.stimuli.items() if IsShadyObject( v ) }
	@property
	def foreign_stimuli( self ): return { k : v  for k, v in self.stimuli.items() if not IsShadyObject( v ) }
	@property
	def state( self ): return self.__state

	# Begin managed properties ############################################################
	
	shady = ManagedProperty( 1, transfer = 'glUniform1i' )
	
	size = ( width, height ) = ManagedProperty(
		default = [ -1, -1 ],
		doc = """
			This is a pair of integers denoting the width and height of the `{cls}` in pixels.
			Do not attempt to change these values - it will not alter the size of the window
			and may have unexpected side effects.
		"""
	)
	clearColor = ( red, green, blue ) = ManagedProperty(
		default = [ 0, 0.5, 0 ],
		transfer = 'glClearColor_RGB',
		doc = """
			This is a triplet of numbers in the range 0 to 1. It specifies the color of the empty screen.
			Note that these values are never linearized. For more precise control over the background,
			construct your `{cls}` with the argument `canvas=True` and then you can manipulate `.backgroundColor`,
			`.gamma` and `.noiseAmplitude`.
		""",
	)
	anchor__ = ( ax_n__, ay_n__ ) = ( anchor_x, anchor_y ) = origin = ( ox_n, oy_n ) = ( origin_x, origin_y ) = ManagedProperty(
		default = [ 0.0, 0.0 ],
		transfer = 'self._OriginShift',
		doc = """
			Specifies where, in normalized coordinates within the rendering area of the window, pixel
			coordinate (0,0) should be considered to be for Stimulus positioning. An origin of [-1,-1]
			means the bottom left corner; [0,0] means the center; [+1,+1] means the top right corner.
			Translations resulting from a change in `.anchor` are automatically rounded down to an
			integer number of pixels, to avoid `.anchor` becoming an unexpected source of interpolation
			artifacts.
		""",
	)
	framesCompleted = ManagedProperty(0, transfer = 'glUniform1i' )
	timeInSeconds__ = t = ManagedProperty(
		default = 0.0,
		doc="DOC-TODO",
	)
	visible__ = on = ManagedProperty(
		default = 1,
		doc = "DOC-TODO",
	)
	
	# properties that are not used directly, but are shared with the canvas Stimulus, if it exists:
	backgroundColor__ = bgcolor = bg = ( bgred, bggreen, bgblue ) = ManagedProperty(
		default = [ 0.5, 0.5, 0.5 ],
		doc = """
			This is a triplet of numbers, each in the range 0 to 1, corresponding to red, green and blue channels.
			It specifies the `.backgroundColor` of the background canvas Stimulus, if present (the `{cls}`
			needs to be constructed with the `canvas=True`, or you otherwise need to call `.MakeCanvas()` ).
			When a canvas is created, this property of the `{cls}` is automatically linked to
			the corresponding property of the canvas `Stimulus` instance; if there is no canvas then this property is unused,
			although you may wish to link it explicitly to other stimuli with `.ShareProperties()` or
			`.LinkPropertiesWithMaster()`.
		""",
	)
	noiseAmplitude__ = noise = ( rednoise, greennoise, bluenoise ) = ManagedProperty(
		default = [ 0.0, 0.0, 0.0 ],
		doc = """
			This is a triplet of floating-point numbers corresponding to red, green and blue channels.
			It specifies the `.noiseAmplitude` for the background canvas
			Stimulus, if present (the `{cls}` needs to be constructed with the `canvas=True`, or you otherwise
			need to call `.MakeCanvas()` ). When a canvas is created, this property of the `{cls}` is automatically linked to
			the corresponding property of the canvas `Stimulus` instance; if there is no canvas then this property is unused,
			although you may wish to link it explicitly to other stimuli with `.ShareProperties()` or
			`.LinkPropertiesWithMaster()`.
		""",
	)
	gamma = ( redgamma, greengamma, bluegamma ) = ManagedProperty(
		default = [ 1.0, 1.0, 1.0 ],
		doc = """
			This is a triplet of numbers, each in the range 0 to 1, corresponding to red, green and blue channels.
			It specifies the `.gamma` of the background canvas Stimulus, if present (the `{cls}` needs to be
			constructed with the `canvas=True`, or you otherwise need to call `.MakeCanvas()` ).
			When a canvas is created, this property of the `{cls}` is automatically linked to
			the corresponding property of the canvas `Stimulus` instance; if there is no canvas then this property is unused,
			although you may wish to link it explicitly to other stimuli with `.ShareProperties()` or
			`.LinkPropertiesWithMaster()`.
			
			`.gamma = 1` is linear; `.gamma = -1` gives you the sRGB gamma profile (a piecewise function
			visually very similar to `.gamma = 2.2`)
		""",
	)
	outOfRangeColor = ManagedProperty(
		default = [ 1.0, 0.0, 1.0 ],
		doc = """
			This is a triplet of numbers, each in the range 0 to 1, corresponding to red, green and blue channels.
			It specifies the `.outOfRangeColor` for the background canvas Stimulus, if present (the `{cls}`
			needs to be constructed with the `canvas=True`, or you otherwise need to call `.MakeCanvas()` ).
			When a canvas is created, this property of the `{cls}` is automatically linked to
			the corresponding property of the canvas `Stimulus` instance; if there is no canvas then this property is unused,
			although you may wish to link it explicitly to other stimuli with `.ShareProperties()` or
			`.LinkPropertiesWithMaster()`.
		""",
	)
	outOfRangeAlpha = ManagedProperty(
		default = 1.0,
		doc = """
			This is a number in the range 0 to 1. It specifies the `.outOfRangeAlpha` for the background
			canvas Stimulus, if present (the `{cls}` needs to be constructed with the `canvas=True`, or you
			otherwise need to call `.MakeCanvas()` ). When a canvas is created, this property of the `{cls}` is automatically linked to
			the corresponding property of the canvas `Stimulus` instance; if there is no canvas then this property is unused,
			although you may wish to link it explicitly to other stimuli with `.ShareProperties()` or
			`.LinkPropertiesWithMaster()`.
		""",
	)
	# End managed properties ############################################################
			
	@apply
	def fakeFrameRate():
		def fget( self ): return self.__fakeFrameRate if self.__fakeFrameRate > 0.0 else None
		def fset( self, value ):
			if not value or value < 0.0: value = 0.0
			self.__fakeFrameRate = float( value )
		return property( fget=fget, fset=fset, doc='DOC-TODO' )
		
	def _Defer( self, func, *pargs, **kwargs ):
		# A method that actually makes GL calls, such as NewPage or LoadTexture,
		# must be called from the same thread/context as the one where all other
		# GL operations happen, otherwise you may fail to see any result or the
		# program may crash.  This is a way round it: by calling (for example)
		# `self._Defer( func, arg1, arg2, ... )` the deferred function will be
		# called at the end of the next frame.
		# The @DeferredCall method decorator uses this under the hood to make
		# methods like World.Stimulus or Stimulus.NewPage safe.
		pending = self.__pending
		if pending is None: pending = self.__pending = []
		container = []
		if isinstance( func, ( tuple, list ) ): priority, func = func
		else: priority = 0
		serialNumber = len( pending )
		pending.append( ( -priority, serialNumber, func, pargs, kwargs, container ) ) # NB: ensure container is last
		return container
		
	def _Undefer( self, target_container ):
		self.__pending[ : ] = [ item for item in self.__pending if item[ -1 ] is not target_container ]
		
	def _RunPending( self ):
		pending = sorted( self.__pending, key=lambda x: x[ :2 ] )
		self.__pending[ : ] = []
		for priority, serialNumber, func, pargs, kwargs, container in pending:
			try: result = func( *pargs, **kwargs )
			except: result = DeferredException( *sys.exc_info() )
			container.append( result )
	
	def _SortStimuli( self ):
		if self._accel:
			stimuli = self.stimuli
			shady_names = self._accel.GetStimulusOrder().split()
			foreign_names = list( set( stimuli.keys() ) - set( shady_names ) )
			ss = self._shady_stimuli = [ stimulus for name in shady_names for stimulus in [ stimuli.get( name, None ) ] if stimulus is not None ]
			fs = self._foreign_stimuli = [ stimuli[ name ] for name in foreign_names ]
			fs[ : ] = [ stimulus for stimulus in fs if hasattr( stimulus, 'draw' ) ]
			fs.sort( key=StimulusSortKey )
		else:
			ss = self._shady_stimuli = []
			fs = self._foreign_stimuli = []
			for name, stimulus in self.stimuli.items():
				if IsShadyObject( stimulus ): ss.append( stimulus )
				elif hasattr( stimulus, 'draw' ): fs.append( stimulus )
			ss.sort( key=StimulusSortKey )
			fs.sort( key=StimulusSortKey )
	
	def _Clock( self ):
		# self.__fakeFrameRate is not used here because we're actually interested in wall time
		if self._accel: return self._accel.Seconds()
		else: return Timing.Seconds()
	
	def _FrameCallback( self, t, userPtr=None ):
		
		# To begin with, t is an absolute wall time in seconds, passed through from the windowing framework:
		# - it should have been measured *before* any GPU commands were issued for this frame, as close as possible to the SwapBuffers call (PygletWindowing with auto=True has a problem there);
		# - it is not guaranteed to be expressed relative to any particular epoch/origin
		#sys.stdout.write('*** entered _FrameCallback ***\n'); sys.stdout.flush()
		wallTimeAtCall = self._drawTime = t # record the absolute time at which the parent Draw() or DrawWorld() function was called - this is used by any subsequent _DebugTiming calls (PyEngine.DrawWorld also performs this assignment, so it's redundant in non-accelerated implementations but it doesn't hurt)
		if self.t0 is None: self.t0 = wallTimeAtCall
		if self.__fakeFrameRate:
			worldTime = self.timeInSeconds = self.framesCompleted / self.__fakeFrameRate
		else:
			worldTime = self.timeInSeconds = wallTimeAtCall - self.t0
		# worldTime means seconds since the World's first rendered frame; it is used as an input to Animate methods and any property dynamics, and may be fake
		
		db = self.debugTiming
		db and self._DebugTiming( 'BeginFrameCallback' )
		if getattr( self, '_shady_stimuli', None ) is None or getattr( self, '_foreign_stimuli', None ) is None:
			self._SortStimuli(); db and self._DebugTiming( 'Separated' )
		
		# Shady stimuli will have already been rendered.
		# Now render foreign stimuli (e.g. pyglet sprites) if any
		for stimulus in self._foreign_stimuli:
			try: stimulus.draw()
			except:
				einfo = sys.exc_info()
				name = [ k for k, v in self.stimuli.items() if v is stimulus ][ 0 ]
				self.stimuli.pop( name, None )
				sys.stderr.write( 'Exception occurred while drawing foreign stimulus %r:\n' % name )
				self.excepthook( *einfo )				
		db and self._DebugTiming( 'DrawForeignStimuli' )
		
		# Update managed properties of World and of Shady Stimulus objects
		self._Record( 'DrawTimeInMilliseconds', wallTimeAtCall, factor=1000.0 )
		self.Animate   and ( self._CallAnimate( worldTime ), db and self._DebugTiming( 'Animate' ) )
		self._dynamics and ( self._RunDynamics( worldTime ), db and self._DebugTiming( 'RunDynamics' ) )
		stimuli = self._shady_stimuli
		for stimulus in stimuli:
			stimulus.Animate   and ( stimulus._CallAnimate( worldTime - stimulus.t0 ), stimulus.debugTiming and stimulus._DebugTiming( 'Animate' ) )
			stimulus._dynamics and ( stimulus._RunDynamics( worldTime - stimulus.t0 ), stimulus.debugTiming and stimulus._DebugTiming( 'RunDynamics' ) )
		db and self._DebugTiming( 'DynamicsFor%dStimuli' % len( stimuli ) )
		
		# Run deferred tasks
		self._RunPending();     db and self._DebugTiming( 'RunPending' )
		
		# Clean up
		self._shady_stimuli = self._foreign_stimuli = None
		
		if hasattr( self.window, 'visible' ) and self.window.visible != self.visible:
			self.window.visible = self.visible = ( self.visible != 0 )
		
		#PyEngine.WaitForGPU(); db and self._DebugTiming( 'WaitForGPU' )
		#sys.stdout.write('*** leaving _FrameCallback ***\n'); sys.stdout.flush()
		return 0
	
	def _UniqueStimulusName( self, pattern=None ):
		if pattern is None: pattern = 'stim%02d'
		if '%' not in pattern:
			if pattern not in self.stimuli: return pattern
			pattern += '%02d'
		i = 1
		while True:
			inflected = pattern % i
			if inflected not in self.stimuli: return inflected
			i += 1
			
	def _NextAvailableSlot( self ):
		lst = self._slots
		if not lst: raise RuntimeError( 'run out of slots' )
		result = lst.pop( 0 )
		# NB: was .pop( -1 ), but this led to an "GLException: invalid operation" on both MacBooks 
		# (where nSlots=16) even though, when first tested on one of the Macs, it worked...
		lst.append( result ) # recycle texture units - comment this out to use each unit strictly once
		return result
	
	def _OriginShift( self, xp, yp ): # NB: never called if there's a DLL
		PyEngine.GL.glTranslatef( PartialTranslation( self.width, xp ), PartialTranslation( self.height, yp ), 0.0 )
	
	def AddForeignStimulus( self, stim, name=None, z=0 ):
		stim.z = z
		stim.name = self._UniqueStimulusName( name )
		self.stimuli[ stim.name ] = stim
		return stim
	
	@DeferredCall
	def Wait( self ): return self.framesCompleted
	Tick = Wait
	
	@DeferredCall
	def Stimulus( self, *pargs, **kwargs ):
		"""Creates a `Stimulus` instance using `Stimulus( world=self, ... )`"""
		return Stimulus( self, *pargs, **kwargs )
	
	@DeferredCall
	def Patch( self, **kwargs ):
		params = dict( name='patch%02d', size=100, anchor=0, color=1, pp=-1, bgalpha=0 )
		params.update( kwargs ); return Stimulus( self, **params )
	
	@DeferredCall
	def Sine( self, **kwargs ):
		params = dict( name='sine%02d', size=100, anchor=0, color=-1, pp=-1, signalFunction=1, siga=min( min( self.bg ), min( 1.0 - x for x in self.bg ) ) )
		params.update( kwargs ); return Stimulus( self, **params )
	
	@DeferredCall
	def MakeCanvas( self, **kwargs ):
		params = dict( name='canvas', source=None, useTexture=False, width=self.width, height=self.height, fg=-1, z=1.0 )
		params.update( kwargs )
		return Stimulus( self, **params ).LinkPropertiesWithMaster( self, 'backgroundColor noiseAmplitude gamma outOfRangeColor outOfRangeAlpha anchor' ).Set( **kwargs )
		
	@DeferredCall
	def Close( self ):
		self.__state = 'closing'
		self.window.Close()
		PyEngine.CleanUpGL()
		self.__state = 'closed'
		
	@DeferredCall
	def SetSwapInterval( self, value ):
		if self._accel: self._accel.SetSwapInterval( value, self.backend.lower().startswith( 'shadylib' ) )
		else: sys.stderr.write( 'SetSwapInterval(%r) ignored - cannot manipulate swap interval without using accelerator\n' % value )
			
	@DeferredCall
	def Capture( self, pil=False, fullscreen=False, saveas='', size=None, origin=None ):
		if fullscreen:
			# NB: this does not appear to capture the foreground window if it is a 
			# pygame (i.e. SDL) window that is full-screen or de-facto-full-screen:
			# you will see the windows and desktop behind it, instead.
			img = ImageGrab.grab()
			if saveas: img.save( saveas )
			if pil: return img
			elif numpy: img = numpy.array( img )
			else: print( 'numpy unavailable - returning PIL image' )
		else:
			if size is None: size = self.size
			size = [ int( round( x ) ) for x in size ]
			if not origin: origin = [ 0, 0 ]
			origin = [ int( round( x ) ) for x in origin ]
			bytesPerPixel = 4
			if self._accel:
				buf = ctypes.create_string_buffer( size[ 0 ] * size[ 1 ] * bytesPerPixel )
				self._accel.CaptureRawRGBA( origin[ 0 ], origin[ 1 ], size[ 0 ], size[ 1 ], buf )
				rawRGBA = buf.raw # but NB: maybe shouldn't let the garbage collector get `buf` until the PIL image or numpy array has been created
			else:
				rawRGBA = PyEngine.CaptureRawRGBA( size, origin=origin )
			if not pil and not numpy:
				if Image: print( 'numpy unavailable - returning PIL image' ); pil = True
				else:     print( 'numpy unavailable - returning raw bytes' )
			if pil or saveas:
				img = Image.frombuffer( 'RGBA', size, rawRGBA, 'raw', 'RGBA', 0, 1 ).transpose( Image.FLIP_TOP_BOTTOM )
				if saveas: img.save( saveas )
			if not pil:
				if numpy: img = numpy.fromstring( rawRGBA, dtype='uint8' ).reshape( [ size[ 1 ], size[ 0 ], 4 ] )[ ::-1, :, : ]
				else: img = rawRGBA
			return img
			
	def ReportVersions( self, outputType='print' ):
		if outputType == 'dict': return self.versions
		s = '\n'.join( '%30r : %r,' % item for item in self.versions.items() )
		if outputType == 'string': return s
		elif outputType == 'print': print( s )
		else: raise ValueError( 'unrecognized output type %r' % outputType )

@ClassWithManagedProperties._Organize
class Stimulus( LinkGL ):
	"""
	In constructing a `Stimulus` instance::
	
		s = Stimulus( world, source, ... )

	the required first argument is a `World` instance. To make this more readable
	you can alternatively call the `Stimulus` constructor as a `World` method::

		w = World( ... )
		s = w.Stimulus( source, ... )

	The second argument is the `source` of the carrier texture. This may be omitted (or
	equivalently set to `None`) if your stimulus is just a blank patch, or its carrier
	signal is defined purely by a function in the shader.  Alternatively `source` may be
	a string, `numpy` array,  or a list of strings and/or `numpy` arrays - see
	`.LoadTexture()` for details.

	The `name` argument is a string that will identify this `Stimulus` in the container
	`w.stimuli` of the `World` to which it belongs. To ensure uniqueness of the
	names in this `dict`, you may include a single numeric printf-style pattern in
	the name (the default `name`, for example, is `'stim%02d'`).

	`width` and `height` specify the dimensions of the envelope in pixels but they
	are optional, since usually they will match the dimensions of the underlying
	`source`. However, they can be specified explicitly to crop or repeat the image.
	Note that `width` and `height` should be in the same units (i.e. unscaled pixels)
	as the underlying texture - if you want to change the physical size of the rendered
	stimulus by magnifying or shrinking the texture, manipulate the `envelopeScaling`
	property (or `xscale` and `yscale` separately).  After construction, the specified
	values are stored in the `envelopeSize` property, or separately in the `width`
	and `height` properties, but these should be considered read-only: you have to
	call the `DefineEnvelope` method explicitly to change the envelope size.
	"""
		
	def __init__( self, world, source=None, name=None, page=None, width=None, height=None, size=None, debugTiming=None, **kwargs ):

		self.name = world._UniqueStimulusName( name )
		if world._accel: self._accel = self._Accelerate( world._accel.CreateStimulus( self.name ) )
		else:            self._accel = None
		self._Initialize( world, debugTiming )
		self.serialNumber = len( world.stimuli )
		world.stimuli[ self.name ] = self
		self.t0 = 0.0  # "world Time"
		self.__lut = None
		self.__page = None
		self.pages = {}
		if source is not None:
			self.NewPage( source, key=page, width=width, height=height, size=size, **kwargs )
		else:
			# store width and height for future reference, if specified here
			if width is None:
				try: width = size[ 0 ]
				except: width = size
			if height is None:
				try: height = size[ 1 ]
				except: height = size
			if width  is not None: self.envelopeSize[ 0 ] = self.textureSize[ 0 ] = width
			if height is not None: self.envelopeSize[ 1 ] = self.textureSize[ 1 ] = height
			if width is not None and height is not None: self.DefineEnvelope( width, height )
			self.Set( **kwargs )
			
	@DeferredCall
	def Enter( self ):
		stimuli = self.world().stimuli
		if stimuli.get( self.name, self ) is not self: raise KeyError( "name %r is already taken in %r" % ( self.name, self.world() ) )
		stimuli[ self.name ] = self
		if self._accel: self._accel.Enter()
		
	@DeferredCall
	def Leave( self ):
		self.world().stimuli.pop( self.name, None )
		if self._accel: self._accel.Leave()
		return self

	def __del__( self ):
		pass # print( 'deleting %s' % self._Description() ) # TODO: this never happens - circular refs?
		# TODO: some way of recycling world slots...

	# Begin managed properties ############################################################
	textureSlotNumber__ = slot = ManagedProperty( -1, transfer='glUniformTextureSlot' )
	textureID                  = ManagedProperty( -1, transfer='glBindTexture_IfNotNegative' )
	# NB: these last two lines can be commented out (and save some render time)
	#     if you never want to use foreign (non-Shady, texture-mapped) stimuli such as those from pyglet
	
	envelopeSize__ = size = ( width, height ) = ManagedProperty(
		default = [ -1, -1 ],
		transfer = 'glUniform2f',
		doc = """
			This is a sequence of two numbers denoting the *unscaled* width and height of the envelope (i.e. width and height
			in texel units).  Unlike most properties, changing these numbers will not have an automatic effect on the stimulus.
			To actually change the unscaled envelope size (for example, to clip or repeat a texture, or to load a new differently-
			shaped texture) you can call the `DefineEnvelope()` method, or the `LoadTexture()` method with argument
			`updateEnvelopeSize=True`. To change the size of the envelope in real time by stretching the image content to fit,
			manipulate `.envelopeScaling` or `.scaledSize` instead.
		""",
	)
	textureSize = ManagedProperty(
		default = [ -1, -1 ],
		transfer = 'glUniform2f',
		doc = """
			DOC-TODO
		""",
	)
	visible__ = on = ManagedProperty(
		default = 1,
		doc = "This is a boolean value that determines whether the `{cls}` is rendered or not.",
	)
			
	z__ = depthPlane = depth = ManagedProperty(
		default = 0.0,
		doc = """
			Determines the depth plane of the `{cls}`.
			The convention is that negative values put you closer to the camera, and positive
			further away; also, you must ensure -1 <= z <= +1. Since the projection is orthographic,
			the value is purely used for depth-sorting of stimuli: therefore,
			setting `.z` to a non-integer value will not cause interpolation artifacts.
		""",
	)
	
	envelopeTranslation__ = envelopePosition = position = pos = xy = ( x, y ) = ManagedProperty(
		default = [ 0.0, 0.0 ],
		transfer = 'glTranslatei_PicturePlane',
		doc = """
			This is a pair of numbers, expressed in pixels. It dictates the two-dimensional coordinates
			of the `{cls}` location within the drawing area.  The values are rounded down to integer values
			when they are applied, to avoid artifacts that might otherwise be introduced inadvertently
			due to linear interpolation during rendering.
						
			See also: `.envelopeOrigin`
		""",
	)
	envelopeOrigin = ( ox, oy, oz ) = ManagedProperty(
		default = [ 0.0, 0.0, 0.0 ],
		transfer = 'glTranslatef',
		doc = """
			This is a triplet of numbers, expressed in pixels, denoting the starting-point, in the coordinate system of the parent `World`,
			of the offsets `.envelopeTranslation` (which is composed of `.x` and `.y`) and depth coordinate `.z`.
			The actual rendered position of the anchor point of `{cls}` `s` will be::
			
				[ s.x + s.ox,   s.y + s.oy,  s.z + s.oz ]
			
			relative to the `World`'s own `.origin`.
			
			You can manipulate `.envelopeOrigin` exclusively and leave `.envelopeTranslation` at 0, as an alternative
			way of specifying `{cls}` position. This is the way to go if you prefer to work in 3D floating-point coordinates
			instead of 2D integers: unlike `.envelopeTranslation`, this property gives you the opportunity to represent non-integer
			coordinate values. With that flexibility comes a caveat: non-whole-number values of `.ox` and `.oy` may result in artifacts in any kind of `{cls}`
			(textured or not) due to linear interpolation during rendering.  You may therefore wish to take care to round
			any values you assign, if you choose to use this property.
			
			Note also that for all stimuli,
			you should ensure that the total depth coordinate, `s.z + s.oz`, is in the range ( -1, +1 ].
		""",
	)
	envelopeRotation__ = rotation = orientation = angle = ManagedProperty(
		default = 0.0,
		transfer = 'glRotatef_PicturePlane',
		doc = """
			This is a scalar number, expressed in degrees. The envelope will be rotated counter-clockwise
			by this number of degrees around its `.anchor`. Note that such transformations of the envelope
			(except at multiples of 90 degrees) will introduce small artifacts into any stimulus, due to linear interpolation.
		""",
	)
	envelopeScaling__ = scale = ( xscale__, yscale__ ) = scaling = ( xscaling__, yscaling__ ) = ManagedProperty(
		default = [ 1.0, 1.0 ],
		transfer = 'glScalef_PicturePlane',
		doc = """
			This is a sequence of two floating-point numbers denoting horizontal and vertical scaling factors.
			The actual rendered size, in pixels, of the scaled `{cls}` `s` will be `s.envelopeScaling * s.envelopeSize`
			Note that such transformations of the envelope will introduce small artifacts into any stimulus, due to linear interpolation.
		""",
	)
	anchor = ( ax_n__, ay_n__ ) = ( anchor_x, anchor_y ) = ManagedProperty(
		default = [ 0.0, 0.0 ],
		transfer = 'self._DoAnchorTranslation',
		doc = """
			This is a sequence of two floating-point numbers expressed in normalized coordinates (from -1 to +1).
			It denotes where, on the surface of the envelope, the anchor point will be.  This anchor point is the point
			whose coordinates are manipulated directly by the other properties, and it also serves as the origin of any scaling
			and rotation of the envelope. The default value is `[-1.0, -1.0]` denoting the bottom left corner, whereas
			`[0.0, 0.0]` would be the center.
			
			The translation caused by changes to `.anchor` is always rounded down to an integer number of pixels,
			to avoid it becoming an unforeseen cause of interpolation artifacts.
		""",
	)
	useTexture = ManagedProperty(
		default = 1,
		transfer = 'glUniform1i',
		doc = """
			A boolean value. Default value is `True`, which means that pixel values
			are drawn from the texture specified by the constructor argument
			`source` (or the `source` argument to a subsequent `NewPage` or
			`LoadTexture` call).  If `.useTexture` is set to `False`, the pixel
			values are determined by `.backgroundColor` and/or `.foregroundColor`
			(as well as `.offset`, `.normalizedContrast`, and any windowing and
			shader-side `.signalFunction` or `.modulationFunction`).
		""",
	)
	carrierRotation__ = cr = ManagedProperty(
		default = 0.0,
		doc = """
			This is a scalar number, expressed in degrees. The carrier will be rotated counter-clockwise
			by this number of degrees around the center of the envelope. 
			Note that if your rotation values is not divisible by 90, this will introduce interpolation artifacts
			into stimuli that use textures. (Unlike `.envelopeRotation`, however, this will not compromise
			pure functionally-generated stimuli.)
		""",
	)
	carrierScaling__ = cscale = ( cxscale__, cyscale__ ) = cscaling = ( cxscaling, cyscaling ) = ManagedProperty(
		default = [ 1.0, 1.0 ],
		doc = """
			This is a sequence of two floating-point numbers denoting horizontal and vertical scaling factors.
			The carrier will be magnified by these factors relative to an origin the center of the envelope.
			Note that scaling values != 1.0 will introduce interpolation artifacts into stimuli that use textures
			(but unlike `.envelopeScaling`, this will not compromise pure functionally-generated stimuli).
		""",
	)
	carrierTranslation = ( cx, cy ) = ManagedProperty(
		default = [ 0.0, 0.0 ],
		transfer = 'self._ComputeCarrierTransformation',
		doc = """
			This is a sequence of two numbers, expressed in pixels, corresponding to x and y dimensions.
			It shifts the carrier (texture stimulus and/or shader function) relative to the envelope.
			Note that non-integer translation values will introduce interpolation artifacts into stimuli that
			use textures (but unlike `.envelopeTranslation`, this should not compromise pure functionally-generated stimuli).
		""",
	)
	carrierTransformation = ManagedProperty( [ 1.0, 0.0, 0.0,     0.0, 1.0, 0.0 ], transfer = 'glUniformCoordinateTransformation' )
	
	offset = ( addr, addg, addb ) = ManagedProperty(
		default = [ 0.0, 0.0, 0.0 ],
		transfer = 'glUniform3f',
		doc = """
			This is a triplet of numbers, each in the range 0.0 to 1.0, corresponding to red, green and blue channels. 
			This is added uniformly to all pixel values before they are scaled by `.normalizedContrast` or by
			windowing (via `.plateauProportion`) and/or custom modulation (via `.modulationFunction`).
		""",
	)
	normalizedContrast__ = contrast = ManagedProperty(
		default = 1.0,
		transfer = 'glUniform1f',
		doc = """
			This is a scalar floating-point value in the range 0.0 to 1.0
			which scales the overall contrast of the `{cls}`. At a contrast of 0,
			the `{cls}` is reduced to its `.backgroundColor`.
		""",
	)
	plateauProportion__ = pp = ( ppx, ppy ) = ManagedProperty(
		default = [ -1.0, -1.0 ],
		transfer = 'glUniform2f',
		doc = """
			This is sequence of two floating-point values corresponding to the x and y dimensions.
			
			A negative value indicates that no windowing is to be performed in the
			corresponding dimension.
			
			A value in the range [0, 1] causes windowing to occur: 0 gives a Hann
			window (raised cosine), 1 gives a boxcar window, and intermediate
			values combine the specified amount of constant plateau with a raised-
			cosine falloff to the edge of the envelope (i.e., a Tukey window).
			
			Note that this means [1, 1] gives a circular or elliptical envelope with
			sharp edges, in contrast to [-1, -1] which gives a square or rectangular envelope.
		""",
	)
	signalFunction__ = sigfunc = ManagedProperty(
		default = 0,
		transfer = 'glUniform1i',
		doc = """
			This integer specifies the index of a shader-side signal function.
			If it is left at 0, no function is used: the carrier content is then dependent
			purely on the texture, if any, or is blank if no texture was specified. 
		
			A value of 1 (which can also be referenced as the constant `SINEWAVE_SF`)
			corresponds to the one and only shader-side signal function that we provide out of
			the box, namely  `SinewaveSignal` which generates a sinusoid.  The parameters of the
			sinusoid are determined by the `.signalParameters` property.
		
			Further values, and hence further functions, may be supported if you add them yourself
			using `AddCustomSignalFunction()`.
		
			Any shader-side signal function should take one input argument (a `vec2` specifying
			location in pixels relative to the center of the stimulus) and return a `vec3` or a `float`.
			This return value gets multiplied by the `.color` of the `{cls}`, and added to its
			`.backgroundColor` (and/or its texture, if any).  If `.color` is negative (i.e. disabled,
			as it is by default) then the function output is multiplied by `[1,1,1]`.  
			
			You may choose to access the uniform variable `uSignalParameters` which is a `vec4`
			corresponding to the built-in property `.signalParameters`, and/or you may choose to
			access your own uniforms that you have added via `World.AddCustomUniform()` or
			`Stimulus.AddCustomUniform()`.
			
			See also: `.signalParameters`,
			          `.modulationFunction`, `.modulationParameters`
		""",
	)
	signalParameters__ = ( siga__, sigf__, sigo__, sigp__ ) = carrierRippleAmpFreqAnglePhase = ( cra, crf, cro, crp ) = ManagedProperty(
		default = [ 1.0, 0.05, 0.0, 0.0 ],
		transfer = 'glUniform4f',
		doc = """
			This is a 4-element vector that can be used to pass parameters to the shader-side
			carrier-signal-generating function chosen by `.signalFunction`.
			If `.signalFunction` is left at its default value of 0, the `.signalParameters`
			are ignored. For the one built-in shader signal function (`.signalFunction=1`
			corresponding to the shader function `SinewaveSignal`), these parameters
			are interpreted as amplitude, frequency, orientation and phase of the
			sinusoidal pattern.  Signal functions are additive to your background and/or texture,
			so if you have no texture and a background color of, for example, 0.3 or 0.7,
			a sinewave amplitude greater than 0.3 will go out of range at full contrast. (Beware also the
			additive effect of noise, if your `.noiseAmplitude` is not 0.)
			
			If you're adding your own custom shader function via `AddCustomSignalFunction()`, your
			implementation of that function may choose to ignore or reinterpret this property
			as you wish. If you choose to use it, your shader code can access it as the
			uniform `vec4` variable  `uSignalParameters.`
			
			See also: `.signalFunction`,
			          `.modulationFunction`, `.modulationParameters`
		""",
		notes = "amplitude from 0 to 1; frequency in cycles/pixel; orientation in degrees; phase in degrees",
	)
	modulationFunction__ = modfunc = ManagedProperty(
		default = 0,
		transfer = 'glUniform1i',
		doc = """
			This integer specifies the index of a shader-side contrast modulation function.
			If it is left at 0, no function is used: the stimulus contrast is then dependent
			only on the overall `.normalizedContrast` and on the window applied according to
			`.plateauProportion`.
		
			A value of 1 (which can also be referenced as the constant `SINEWAVE_MF`)
			corresponds to the one and only shader-side modulation function that we provide out of
			the box, namely  `SinewaveModulation` which performs sinusoidal contrast modulation.
			The parameters of this modulation pattern are determined by the `.modulationParameters` property.
		
			Further values, and hence further functions, may be supported if you add them yourself
			using `AddCustomModulationFunction()`.
		
			Any shader-side modulation function should take one input argument (a `vec2` specifying
			location in pixels relative to the center of the stimulus) and return a `float`. This return
			value is used as a multiplier for stimulus contrast. You may choose to access the uniform
			variable `uModulationParameters` which is a `vec4` corresponding to the built-in property
			`.modulationParameters`, and/or you may choose to access your own uniforms that you
			have added via `World.AddCustomUniform()` or `Stimulus.AddCustomUniform()`.
			
			See also: `.modulationParameters`,
			          `.signalFunction`, `.signalParameters`
		""",
	)
	modulationParameters__ = ( moda__, modf__, modo__, modp__ ) = envelopeRippleAmpFreqAnglePhase = ( era, erf, ero, erp ) = ManagedProperty(
		default = [ 0.0, 0.005, 0.0, 90.0 ],
		transfer = 'glUniform4f',
		doc = """
			This is a 4-element vector that can be used to pass parameters to the shader-side
			contrast-modulation function chosen by `.modulationFunction`.
			
			If `.modulationFunction` is left at its default value of 0, these four values
			are ignored. For the one built-in shader modulation function (`.modulationFunction=1`
			corresponding to the shader function `SinewaveModulation`), the values
			are interpreted as depth, frequency, orientation and phase of the desired sinusoidal
			modulation pattern.
			
			If you're adding your own custom shader function via `AddCustomModulationFunction()`, your
			implementation of that function may choose to ignore or reinterpret this
			property as you wish. If you choose to use it, your shader code can access it as the
			uniform `vec4` variable  `uModulationParameters.`
			
			See also: `.modulationFunction`,
			          `.signalFunction`, `.signalParameters`
		""",
		notes = "amplitude, i.e. modulation depth, from 0 to 1; frequency in cycles/pixel; orientation in degrees; phase in degrees",
	)
	backgroundAlpha__ = bgalpha = ManagedProperty(
		default = 1.0,
		transfer = 'glUniform1f',
		doc = """
			This is a floating-point number from 0 to 1, indicating the opacity at locations where the
			signal has been attenuated away completely (by windowing via `.plateauProportion`, by a custom
			`.modulationFunction`, or by manipulation of overall `.normalizedContrast`).
			
			For psychophysical stimuli, ensure `.backgroundAlpha` is 1.0 and manipulate `.backgroundColor` instead:
			although alpha *can* be used for windowing in this way, alpha-blending is applied post-linearization
			so the result will not be well linearized, except in very fragile special cases.
		""",
	)
	backgroundColor__ = bgcolor = bg = ( bgred, bggreen, bgblue ) = ManagedProperty(
		default = [ 0.5, 0.5, 0.5 ],
		transfer = 'glUniform3f',
		doc = """
			This is a triplet of numbers, each in the range 0 to 1, corresponding to red, green and blue channels. It
			specifies the color at locations in which the carrier signal (texture and/or foreground color and/or
			functionally generated carrier signal) has been attenuated away completely (by contrast scaling, windowing,
			or custom contrast modulation pattern).
		""",
	)
	noiseAmplitude__ = noise = ( rednoise, greennoise, bluenoise ) = ManagedProperty(
		default = [ 0.0, 0.0, 0.0 ],
		transfer = 'glUniform3f',
		doc = """
			This is a triplet of floating-point numbers corresponding to red, green and blue channels.
			Negative values lead to uniform noise in the range `[s.noiseAmplitude[i], -s.noiseAmplitude[i]]`.
			Positive value lead to Gaussian noise with standard deviation equal to the `.noiseAmplitude` value.
		""",
	)
	gamma = ( redgamma, greengamma, bluegamma ) = ManagedProperty(
		default = [ 1.0, 1.0, 1.0 ],
		transfer = 'glUniform3f',
		doc = """
			This is a triplet of values denoting the screen gamma that
			should be corrected-for in each of the red, green and blue channels.
			A gamma value of 1 corresponds to the assumption that your
			screen is already linear.  Setting gamma values other than 1
			is an alternative to using a pre-linearized lookup-table or `.lut`.
			
			(You probably want to avoid using non-linear `.gamma` values at the same
			time as a look-up table, but if you want to combine them for
			some reason, you should know that the inverse-function of the
			gamma specified here is applied *before* the look-up table.)
			
			Any value less than or equal to 0.0 is interpreted to denote
			the sRGB function, which is a standard piecewise function that
			follows the `gamma=2.2` curve quite closely (although the exponent
			it uses is actually slightly higher).
		""",
	)
	color__ = ( red__, green__, blue__ ) = foregroundColor = fgcolor = fg = ( fgred, fggreen, fgblue ) = ManagedProperty(
		default = [ -1.0, -1.0, -1.0 ],
		transfer = 'glUniform3f',
		doc = """
			This is a triplet of numbers, each in the range 0 to 1, corresponding to red, green and blue channels. Values
			may also be negative, in which case no colorization is applied in the corresponding channel.
			
			Where non-negative, foreground color plays slightly different roles depending on other parameters:
			
			If the `{cls}` uses a texture, the pixel values from the texture are tinted via multiplication with the `.color` values.
			
			If the `{cls}` uses a `.signalFunction` then the signal is also multiplied by the `.color` before being added.
			
			If there is no texture and no `.signalFunction`, the carrier image consists of just the specified uniform solid `.color`.
			The `{cls}` color may still be attenuated towards the `.backgroundColor`, both uniformly by
			setting `.normalizedContrast` < 1.0, and as a function of space by setting `.plateauProportion` `>= 0.0` or
			by using a `.modulationFunction`).
		""",
	)
	alpha__ = fgalpha = opacity = ManagedProperty(
		default = 1.0,
		transfer = 'glUniform1f',
		doc = """
			This is a floating-point number from 0 to 1. It specifies the opacity of the `{cls}` as a whole.
			Note that with psychophysical stimuli you should always ensure `.alpha` == 1, and manipulate
			`.backgroundColor` and '.normalizedContrast` instead: this is because alpha-blending is carried
			out by the graphics card AFTER our linearization (via the `.gamma` property or via a look-up table)
			is applied. Therefore the result will no longer be linearized.
		""",
	)
	outOfRangeColor = ManagedProperty(
		default = [ 1.0, 0.0, 1.0 ],
		transfer = 'glUniform3f',
		doc = """
			This is a triplet of numbers, each in the range 0 to 1, corresponding to red, green and blue channels.
			It specifies the color that should be used for pixels whose values go out of range.
		""",
	)
	outOfRangeAlpha = ManagedProperty(
		default = 1.0,
		transfer = 'glUniform1f',
		doc = """
			This is a floating-point number from 0 to 1.
			It specifies the color that should be used for pixels whose values go out of range.
		""",
	)
	debugDigitsStartXY = ManagedProperty( [ -1.0, -1.0 ], transfer='glUniform2f' )
	debugDigitSize     = ManagedProperty( [ -1.0, -1.0 ], transfer='glUniform2f' )
	debugValueIJK = ( dbi, dbj, dbk ) = ManagedProperty( [ 0.0, 0.0, 0.0 ], transfer='glUniform3f' )
	lookupTableTextureSize = ManagedProperty( [ -1, -1, -1 ], transfer='glUniform3f' )
	lookupTableTextureSlotNumber = ManagedProperty( -1, transfer='glUniformTextureSlot' )
	lookupTableTextureID = ManagedProperty( -1, transfer='glBindTexture_IfNotNegative' )
	penThickness = ManagedProperty(
		default = 5.0,
		doc = """
			DOC-TODO
		""",
	)
	smoothing = ManagedProperty(
		default = 1,
		doc = """
			DOC-TODO
		""",
	)
	pointsXY = ManagedProperty(
		default = [ 0.0 ] * MAX_POINTS * 2,
		doc = """
			DOC-TODO
		""",
	)
	nPoints__ = numberOfPoints = npoints = ManagedProperty(
		default = 0,
		transfer='self._DrawPoints',
		doc = """
			DOC-TODO
		""",
	)
	quadNumber__ = drawMode = ManagedProperty(
		default = -1,
		transfer='glCallList_IfNotNegative',
		doc = """
			DOC-TODO
		""",
	)
	# NB: quadNumber should be the last ManagedProperty in this sequence
	# End managed properties ############################################################
	
	@apply
	def points():
		doc = """
		DOC-TODO
		"""
		def fget( self ):
			if numpy: n = self.nPoints; return self.pointsXY[ :n * 2 ].reshape( [ n, 2 ] )
			else: return self.pointsXY
		def fset( self, value ):
			if callable( value ): return self.SetDynamic( 'points', value, order=2 )
			self.SetDynamic( 'points', None, order=2 )
			if numpy:
				if not isinstance( value, numpy.ndarray ): value = numpy.array( value )
				if numpy.iscomplexobj( value ): value = numpy.c_[ value.real.flat, value.imag.flat ]
				self.nPoints = value.size // 2
				self.pointsXY.flat = value.flat
			else:
				try: value[ 0 ][ 0 ]
				except: 
					try: value[ 0 ].imag
					except: pass
					else: value = [ x for z in value for x in ( z.real, z.imag ) ]
				else: value = [ x for pair in value for x in pair ]
				self.nPoints = len( value ) // 2
				if value: self.pointsXY[ :len( value ) ] = value
		return property( fget=fget, fset=fset, doc=doc )	
				
	@apply
	def pointsComplex():
		doc = """
		DOC-TODO
		"""
		def fget( self ): return self.pointsXY[ : self.nPoints * 2 ].view( numpy.complex128 ) # numpy required
		def fset( self, value ): self.points = value
		return property( fget=fget, fset=fset, doc=doc )
			
	def _DrawPoints( self, n ):  # NB: never called if there's a DLL
		if not n: return
		w, h = self.envelopeSize
		xp, yp = self.anchor
		offsets = [ PartialTranslation( w, xp ), PartialTranslation( h, yp ) ]
		PyEngine.DrawPoints( DRAWMODE, self.quadNumber, self.penThickness, self.smoothing, n, self.points, offsets )
	
	
	@apply
	def frame(): # pseudo-ManagedProperty (in that it supports _RunDynamics)
		doc = """
			This non-managed property is an integer denoting the index of the
			current frame of a multi-frame stimulus. Note that frames are
			concatenated horizontally in the underlying carrier texture, so a
			change in `.frame` is actually achieved by manipulating `.cx`,
			otherwise known as `.carrierTranslation[0]`.
		"""
		def fget( self ):
			if not self.textureSize[ 0 ] or not self.envelopeSize[ 0 ]: return 0
			return ( -self.carrierTranslation[ 0 ] % self.textureSize[ 0 ] ) // self.envelopeSize[ 0 ]
		def fset( self, value ):
			if callable( value ): return self.SetDynamic( 'frame', value, order=2 )
			self.SetDynamic( 'frame', None, order=2 )
			self.carrierTranslation[ 0 ] = int( ( -self.envelopeSize[ 0 ] * int( value ) ) % self.textureSize[ 0 ] )
		return property( fget=fget, fset=fset, doc=doc )
	
	@apply
	def page():
		doc = """
			DOC-TODO
		"""
		def fget( self ):
			return self.__page
		def fset( self, value ):
			if callable( value ): return self.SetDynamic( 'page', value, order=2 )
			self.SetDynamic( 'page', None, order=2 )
			if isinstance( value, float ) and value not in self.pages: value = int( value )
			if isinstance( value, int ) and value not in self.pages: value %= len( self.pages )
			self.SwitchTo( value )
		return property( fget=fget, fset=fset, doc=doc )
		
	@apply
	def lut():
		doc = """
		look-up table (DOC-TODO)
		"""
		def fget( self ): return self.__lut
		def fset( self, value ): self.SetLUT( value )
		return property( fget=fget, fset=fset, doc=doc )
		
	@apply
	def scaledSize():
		doc="""Non-managed property that reflects the product of `.envelopeSize` and `.envelopeScaling`."""
		def fget( self ): return ( self.scaledWidth, self.scaledHeight )
		def fset( self, value ):
			if callable( value ): return self.SetDynamic( 'scaledSize', value, order=2 )
			self.SetDynamic( 'scaledSize', None, order=2 )
			try: w, h = value
			except: w = h = value
			self.scaledWidth, self.scaledHeight = w, h
		return property( fget=fget, fset=fset, doc=doc )
	@apply
	def scaledWidth():
		doc="""Non-managed property that reflects the product of `.envelopeSize[0]` and `.envelopeScaling[0]`."""
		def fget( self ): return self.envelopeSize[ 0 ] * self.envelopeScaling[ 0 ]
		def fset( self, value ):
			if callable( value ): return self.SetDynamic( 'scaledWidth', value, order=3 )
			self.SetDynamic( 'scaledWidth', None, order=3 )
			if self.envelopeSize[ 0 ]: self.envelopeScaling[ 0 ] = float( value ) / self.envelopeSize[ 0 ]
		return property( fget=fget, fset=fset, doc=doc )
	@apply
	def scaledHeight():
		doc="""Non-managed property that reflects the product of `.envelopeSize[1]` and `.envelopeScaling[1]`."""
		def fget( self ): return self.envelopeSize[ 1 ] * self.envelopeScaling[ 1 ]
		def fset( self, value ):
			if callable( value ): return self.SetDynamic( 'scaledHeight', value, order=3 )
			self.SetDynamic( 'scaledHeight', None, order=3 )
			if self.envelopeSize[ 1 ]: self.envelopeScaling[ 1 ] = float( value ) / self.envelopeSize[ 1 ]
		return property( fget=fget, fset=fset, doc=doc )
		
	
	def _DoAnchorTranslation( self, xp, yp ):  # NB: never called if there's a DLL
		PyEngine.GL.glTranslatef( PartialTranslation( -self.envelopeSize[ 0 ], xp ), PartialTranslation( -self.envelopeSize[ 1 ], yp ), self.z )
	
	def _ComputeCarrierTransformation( self, cx, cy ):  # NB: never called if there's a DLL
		alpha = -self.carrierRotation * math.pi / 180.0
		cosa, sina = math.cos( alpha ), math.sin( alpha )
		xscale, yscale = self.carrierScaling
		xorigin, yorigin = [ x / 2.0 for x in self.envelopeSize ]
		xshift = -cosa * xorigin / xscale + sina * yorigin / xscale + xorigin - cx
		yshift = -cosa * yorigin / yscale - sina * xorigin / yscale + yorigin - cy
		m = [ [ cosa / xscale, -sina / xscale, xshift ], [ sina / yscale,  cosa / yscale, yshift ] ]
		self.carrierTransformation = m[ 0 ] + m[ 1 ]
	
	def ResetClock( self, other=None ):
		if other: self.t0 = getattr( other, 't0', t0 )
		else: self.t0 = self.world().t	
	
	def Capture( self, pil=False, saveas='' ):
		origin, size = self.BoundingBox()
		return self.world().Capture( pil=pil, saveas=saveas, fullscreen=False, size=size, origin=origin )
	
	def BoundingBox( self, worldCoordinates=False ):
		# TODO: really should recreate *all* envelope transformations including envelopeRotation...
		world = self.world()
		bottomLeft = [
			  self.envelopeOrigin[ i ]
			+ self.envelopeTranslation[ i ]
			+ ( 0 if worldCoordinates else PartialTranslation( world.size[ i ], world.anchor[ i ] ) )
			- PartialTranslation( self.scaledSize[ i ], self.anchor[ i ] )
		for i in range( 2 ) ]
		size = self.scaledSize[ :2 ]
		return list( bottomLeft ), list( size )
		
		
	@DeferredCall
	def NewPage( self, source, key=None, width=None, height=None, size=None, **kwargs ):
		if width is None:
			try: width = size[ 0 ]
			except: width = size
		if height is None:
			try: height = size[ 1 ]
			except: height = size
		self.quadNumber = -1
		self.textureSlotNumber = -1 
		self.textureID = -1
		self.LoadTexture( source, False )
		self.Set( **kwargs )
		if not -1.0 <= self.z <= 1.0: raise ValueError( "z must be in the range [-1, 1]" )
		if width  is None: width  = self.frameWidth
		if height is None: height = self.textureSize[ 1 ]
		self.DefineEnvelope( width, height )
		if key is not None: self.SavePage( key )
	
	def SavePage( self, key ):
		fields = 'quadNumber textureSlotNumber textureID textureSize envelopeSize frameWidth'.split()
		self.pages[ key ] = { k : getattr( self, k ) * 1 for k in fields }
		self.__page = key
	
	def SwitchTo( self, key ):
		for k, v in self.pages[ key ].items(): setattr( self, k, v )
		self.__page = key
		return key

	@DeferredCall
	def DefineEnvelope( self, width=None, height=None ):
		if self._accel:
			self._accel.DefineQuad( -1 if width is None else int( round( width ) ), -1 if height is None else int( round( height ) ) )
		else:
			if width  is not None: self.envelopeSize[ 0 ] = width
			if height is not None: self.envelopeSize[ 1 ] = height
			self.quadNumber = PyEngine.DefineQuad( self.quadNumber, *self.envelopeSize )
			
	@DeferredCall
	def SetLUT( self, lut ):
		if lut is not None and not isinstance( lut, LookupTable ): lut = LookupTable( self.world(), lut )
		if lut is None: self.MakePropertiesIndependent( lookupTableTextureSize=-1, lookupTableTextureSlotNumber=-1, lookupTableTextureID=-1 )
		else:           self.LinkPropertiesWithMaster( lut, 'lookupTableTextureSize', 'lookupTableTextureSlotNumber', 'lookupTableTextureID' )
		self.__lut = lut
		return lut
		
	@DeferredCall
	def AddDebugDigits( self, value=None, x=0, y=0, i=0, j=0, k=0 ):
		nDigits = 10
		imageFileName = PackagePath( 'glsl/digits_small.png' )
		if not Image: raise ImportError( 'cannot load %r: Image module not available (need to install `PIL` or `pillow` package)' % imageFileName )
		if not numpy: raise ImportError( 'cannot manipulate image pixels unless you install the `numpy` package' )
		digits = numpy.array( Image.open( imageFileName ), dtype=float ) / 255.0
		digits[ :, :, 3 ] = 1.0
		img = numpy.array( self.source, copy=True ) # could add digits with LoadSubTexture instead of relying on self.source...
		while img.ndim < 3: img = numpy.expand_dims( img, -1 )
		self.debugValueIJK = [ i, j, k ]
		self.debugDigitsStartXY = [ x, y ]
		digitWidth, digitHeight = self.debugDigitSize = [ digits.shape[ 1 ] // nDigits, digits.shape[ 0 ] ]
		rStart = img.shape[ 0 ] - y - digitHeight
		img[ rStart : rStart + digitHeight, x : x + digitWidth * nDigits, : ] = digits[ :, :, :img.shape[ 2 ] ]
		if value is not None: img[ i, j, k ] = value # ...but then we could not do this, in only one channel, with LoadSubTexture...
		self.LoadTexture( img ) # ...so let's just load the whole texture back in
		return self
			
	@DeferredCall
	def LoadTexture( self, source, updateEnvelopeSize=True, useTexture=True ):
		"""
		Loads texture data from `source` and associates it with this Stimulus.
		
		Args:
			source:  the source of the carrier texture data. This may be:
			
				- omitted or set to `None` if there is no texture (just a constant carrier
				  signal, or one defined by a function in the shader)
		
				- a string (possibly including glob characters `'*'` and/or `'?'`) denoting one
				  or more image files to be used as animation frames

				- a `numpy` array specifying the pixel values of a texture image, in which case:

					- `source.dtype` must be one of:
					   - `numpy.dtype('uint8')`   : 8-bit pixel values in the range 0 to 255
					   - `numpy.dtype('float32')` : pixel value in the range 0.0 to 1.0
					   - `numpy.dtype('float64')` : pixel value in the range 0.0 to 1.0
					     (will be converted to float32 automatically)
					
					- `source.shape` must be one of:
						- `[height, width]`        : LUMINANCE image
						- `[height, width, 1]`     : LUMINANCE image
						- `[height, width, 2]`     : LUMINANCE_ALPHA image
						- `[height, width, 3]`     : RGB image
						- `[height, width, 4]`     : RGBA image

				- a `list` or `tuple` containing filenames and/or `numpy` arrays as above, to be
				  used as multiple frames
			
			updateEnvelopeSize (bool): whether or not to update the envelope size to match the
			                           dimensions of the new texture
			                           
			useTexture (bool): new value for the `.useTexture` property attribute that
			                   enables or disables the use of this texture
		"""
		
		if isinstance( source, Stimulus ):
			for key in 'textureID textureSlotNumber textureSize source frameWidth'.split(): setattr( self, key, getattr( source, key ) )
			if updateEnvelopeSize: self.DefineEnvelope( self.frameWidth, self.textureSize[ 1 ] )
			return self
			
		if isinstance( source, ( tuple, list ) ) and source and not isinstance( source[ 0 ], ( bool, int, float, tuple, list ) ):
			sourceList = source
		else:
			sourceList = [ source ]
		def getfiles( pattern ):
			if pattern.lower().startswith( ( 'http://', 'https://' ) ): return [ pattern ]
			result = glob.glob( pattern )
			if not result: raise FileNotFoundError( 'found no files matching %r' % pattern )
			return result
		sourceList = [ source for element in sourceList for source in ( getfiles( element ) if isinstance( element, basestring ) else [ element ] ) ]
		if not sourceList: raise ValueError( "empty source texture" )
		sourceList = [ source for source in sourceList if source is not None ]
		class framelist( list ): pass
		for sourceIndex, source in enumerate( sourceList ):
			if isinstance( source, basestring ):
				if not Image: raise ImportError( 'cannot load textures from file unless you install the `PIL` or `pillow` package' )
				source = framelist( FramesFromFile( source ) )
			sourceList[ sourceIndex ] = source
		# flatten the list in case it got expanded by multi-frame images:
		sourceList = [ source for item in sourceList for source in ( item if isinstance( item, framelist ) else [ item ] ) ]
		for sourceIndex, source in enumerate( sourceList ):
			if not numpy: raise ImportError( 'cannot manipulate textures unless you install the `numpy` package' )
			if not isinstance( source, numpy.ndarray ):
				source = numpy.array( source )
			while source.ndim < 3:
				source = numpy.expand_dims( source, -1 )
			sourceList[ sourceIndex ] = source
				
		if len( sourceList ) == 0:
			source = None
		elif len( sourceList ) == 1:
			source = sourceList[ 0 ]
			self.frameWidth = source.shape[ 1 ]
		else:
			self.frameWidth = max( source.shape[ 1 ] for source in sourceList )
			frameHeight = max( source.shape[ 0 ] for source in sourceList )
			channels = max( source.shape[ 2 ] for source in sourceList )
			strip = numpy.zeros( [ frameHeight, self.frameWidth * len( sourceList ), channels ], dtype=sourceList[ 0 ].dtype )
			# TODO: we're limited by MAX_TEXTURE_EXTENT (see above) so the texture will fail to transfer
			#       if you have, say, more than 32 frames of a 500-by-N-pixel image on the Surface Pro 3
			#       or more than 16 frames of the same image on the MacBook11,1
			for i, source in enumerate( sourceList ):
				xoffset = i * self.frameWidth + ( self.frameWidth - source.shape[ 1 ] ) // 2
				yoffset = ( frameHeight - source.shape[ 0 ] ) // 2
				strip[ yoffset : yoffset + source.shape[ 0 ], xoffset : xoffset + source.shape[ 1 ], : ] = source
				# TODO: will fail if frames differ in their number of channels
			source = strip
		self.source = source # TODO: might need to omit this to save memory
		if source is None: return self
		# at this point we can assume a 3-D numpy array (height by width by channels)
		
		if useTexture is not None: self.useTexture = useTexture
		self.textureSize = [ source.shape[ 1 ], source.shape[ 0 ] ]
		if updateEnvelopeSize: self.DefineEnvelope( self.frameWidth, self.textureSize[ 1 ] )
		if self._accel:
			self._accel.LoadTexture( *PrepareTextureData( source ) )
		else:
			if self.textureSlotNumber < 0: self.textureSlotNumber = self.world()._NextAvailableSlot()
			self.textureID = PyEngine.LoadTexture( self.textureSlotNumber, self.textureID, *PrepareTextureData( source ) )
		
	@DeferredCall
	def LoadSubTexture( self, source, x=0, y=0 ):
		# note: x<0 and y<0 does not wrap around, array-like;  it just moves the edge of the subtexture out of bounds and hence truncates the subtexture
		if self.textureID < 0: raise TypeError( 'cannot load a subtexture into a Stimulus that has no texture' )
		if isinstance( source, basestring ):
			if not Image: raise ImportError( 'cannot load textures from file unless you install the `PIL` or `pillow` package' )
			source = Image.open( source )
		if not numpy: raise ImportError( 'cannot manipulate textures unless you install the `numpy` package' )
		if not isinstance( source, numpy.ndarray ): source = numpy.array( source )
		if source.ndim == 1: source = source[ :, None ]
		if source.ndim == 2: source = source[ :, :, None ]
		canvasWidth, canvasHeight = self.textureSize 
		brushHeight, brushWidth = source.shape[ :2 ]
		column, row = x, canvasHeight - y - brushHeight
		if row < 0: source = source[ -row:, :, : ]; row = 0
		if row + brushHeight > canvasHeight: source = source[ :canvasHeight - row - brushHeight, :, : ]
		if column < 0: source = source[ :, -column:, : ]; column = 0
		if column + brushWidth > canvasWidth: source = source[ :, :canvasWidth - column - brushWidth, : ]
		if not source.size: return
		if self._accel: self._accel.LoadSubTexture( column, row, *PrepareTextureData( source ) )
		else:           PyEngine.LoadSubTexture( self.textureSlotNumber, self.textureID, column, row, *PrepareTextureData( source ) )

def StubProperty( cls, name, requirement ):
	def fail( self, value=None ): raise AttributeError( 'to use the .%s property of the %s class, you must first %s' % ( name, cls.__name__, requirement ) )
	setattr( cls, name, property( fget=fail, fset=fail ) )
StubProperty( Stimulus, 'text',  'explicitly import Shady.Text' )
StubProperty( Stimulus, 'video', 'explicitly import Shady.Video' )
	
def PrepareTextureData( sourceArray, *pargs ):
	if sourceArray.dtype == 'float64':
		sourceArray = sourceArray.astype( 'float32' )
	elif sourceArray.dtype != 'uint8' and sourceArray.dtype.name.startswith( ( 'int', 'uint' ) ) and sourceArray.min() >= 0 and sourceArray.max() <= 255:
		sourceArray = sourceArray.astype( 'uint8' )
	if sourceArray.dtype not in [ 'float32', 'uint8' ]: raise TypeError( 'unsupported data type %r' % sourceArray.dtype.name )
	width     = sourceArray.shape[ 1 ] if len( sourceArray.shape ) >= 2 else 1
	height    = sourceArray.shape[ 0 ]
	nChannels = sourceArray.shape[ 2 ] if len( sourceArray.shape ) >= 3 else 1
	dataType  = sourceArray.dtype.name
	data      = sourceArray.tostring( order='C' )
	return ( width, height, nChannels, dataType, data ) + pargs

@ClassWithManagedProperties._Organize
class LookupTable( LinkGL ):
	def __init__( self, world, values, debugTiming=None ):
		
		if world._accel: self._accel = self._Accelerate( world._accel.CreateRGBTable() )
		else:            self._accel = None
		self._Initialize( world, debugTiming )
		self.LoadValues( values )
	
	@DeferredCall
	def LoadValues( self, values ):

		if not numpy: raise ImportError( 'cannot manipulate lookup-table values unless you install the `numpy` package' )
		if isinstance( values, basestring ):
			file_name = values
			if file_name.lower().endswith( '.npy' ):
				values = numpy.load( file_name )
			elif file_name.lower().endswith( '.npz' ):
				vars = numpy.load( file_name )
				if len( vars.keys() ) == 1: values = vars[ vars.keys()[ 0 ] ]
				else: values = vars[ 'lut' ]
			else:
				if not Image: raise ImportError( 'cannot load LUT from image file unless you install the `PIL` or `pillow` package' )
				values = Image.open( file_name )
				
		values = numpy.array( values, copy=False )
		if values.ndim == 3: values = values.transpose( [ 1, 0, 2 ] ).reshape( [ values.shape[ 0 ] * values.shape[ 1 ], values.shape[ 2 ] ] )
		if values.ndim == 2: values = values[ :, None, : ]
		if values.ndim != 3: raise ValueError( 'LUT array must be 2- or 3- dimensional' )
		if values.shape[ -1 ] not in [ 3, 4 ]: raise ValueError( 'LUT array must have extent 3 or 4 in its highest dimension (RGB or RGBA)' )
		if values.min() < 0 or not 2 <= values.max() <= 255: raise ValueError( 'LUT values must be in range [0, 255]' )
		values = values.astype( 'uint8', copy=False )
		length = values.shape[ 0 ] * values.shape[ 1 ]
		
		# juggle dimensions to fit within maximum allowed width and/or height of GL texture
		height, width = length, 1
		target_width = 1
		extra = 0
		while height > MAX_TEXTURE_EXTENT:
			target_width *= 2
			height = length // target_width
			width = int( math.ceil( length / float( height ) ) )
			extra = width * height - length
		if extra:
			extra = numpy.zeros_like( values[ :extra, :, : ] )
			values = numpy.concatenate( [ values, extra ], axis=0 )
		values = values.reshape( [ width, height, values.shape[ 2 ] ] ).transpose( [ 1, 0, 2 ] )
		
		self.values = values
		self.lookupTableTextureSize = [ values.shape[ 1 ], values.shape[ 0 ], length ]
		if self._accel:
			self._accel.LoadTexture( *PrepareTextureData( values ) )
		else:
			if self.lookupTableTextureSlotNumber < 0: self.lookupTableTextureSlotNumber = self.world()._NextAvailableSlot()
			self.lookupTableTextureID = PyEngine.LoadTexture( self.lookupTableTextureSlotNumber, self.lookupTableTextureID, *PrepareTextureData( values, True ) )
		
	# Begin managed properties ############################################################
	lookupTableTextureSize = ManagedProperty( [ -1, -1, -1 ] )     # no transfer function - just share
	lookupTableTextureSlotNumber__ = slot = ManagedProperty( -1 )  #  these properties with whichever
	lookupTableTextureID = slot = ManagedProperty( -1 )            #  Stimulus objects want to use the LUT
	# End managed properties ############################################################
	
class Scheduled( object ):
	
	__deferred = []
	__world = None
	__parent = None
	__selfref = None
	__cancel = False
	priority = 0
	
	
	@classmethod
	def _MakeProperty( cls, name, *otherNames ):
		def fget( self ): return self._Property( name )
		def fset( self, value ): self._Property( name, value )
		prop = property( fget=fget, fset=fset )
		for eachName in ( name, ) + otherNames: setattr( cls, eachName, prop )
		return prop
		
	def _Property( self, optionName, newValue=None ):
		pass
		
	def _Update( self ):	
		pass
		
	def _TryUpdate( self ):
		cancel, self.__cancel = self.__cancel, False
		if cancel: return
		self.ScheduleUpdate()
		try:
			self._Update()
		except:
			einfo = sys.exc_info()
			world = self.world
			if not world: reraise( *einfo )
			getattr( world, 'excepthook', sys.excepthook )( *einfo )
			self.CancelUpdate()
			
	@staticmethod
	def _WeakTryUpdate( ref ):
		self = ref()
		if self is not None: return self._TryUpdate()
		
	def ScheduleUpdate( self ):
		world = self.world
		self.__cancel = False
		if self.__selfref is None: self.__selfref = weakref.ref( self )
		if world: self.__deferred = world._Defer( ( self.priority, self._WeakTryUpdate ), self.__selfref )
		
	def CancelUpdate( self ):
		world = self.world
		self.__cancel = True
		if world: world._Undefer( self.__deferred )
		
	@apply
	def world():
		def fget( self ): value = self.__world; return value() if isinstance( value, weakref.ReferenceType ) else value
		def fset( self, value ):
			self.CancelUpdate()
			if value is not None and not isinstance( value, weakref.ReferenceType ): value = weakref.ref( value )
			if value is not None and value() is None: value = None
			self.__world = value
			self.ScheduleUpdate()
		return property( fget=fget, fset=fset )
		
	@apply
	def parent():
		def fget( self ): value = self.__parent; return value() if isinstance( value, weakref.ReferenceType ) else value
		def fset( self, value ):
			if value is not None and not isinstance( value, weakref.ReferenceType ): value = weakref.ref( value )
			if value is not None and value() is None: value = None
			self.__parent = value
			self.world = value().world if value else None
		return property( fget=fget, fset=fset )
		
	def Set( self, **kwargs ):
		for k, v in kwargs.items(): setattr( self, k, v )
		return self
		
	
class Bunch( dict ):
	def __init__( self, *pargs, **kwargs ): dict.__init__( self ); self.__dict__ = self.update( *pargs, **kwargs )
	def update( self, *pargs, **kwargs ): [ dict.update( self, d ) for d in pargs + ( kwargs, ) ]; return self
		
def FramesFromFile( filename ):
	if not Image: raise ImportError( 'cannot load textures from file unless you install the `PIL` or `pillow` package' )
	url = None
	if filename.startswith( ( 'http://', 'https://' ) ):
		try: import urllib.request
		except ImportError: from urllib import urlretrieve
		else:
			from urllib.request import urlretrieve
			opener = urllib.request.build_opener()
			opener.addheaders = [ ( 'User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36' ) ]
			urllib.request.install_opener( opener )
		url = filename
		xtn = os.path.splitext( url )[ -1 ]
		import tempfile; f = tempfile.NamedTemporaryFile( suffix=xtn, delete=False ); filename = f.name; f.close();
		urlretrieve( url, filename )
	img = Image.open( filename )
	nFrames = getattr( img, 'n_frames', 1 )
	if nFrames == 1: return [ img ] # most images will be like this
	# ...but now we're on to multi-frame images. pillow will support these, old PIL will not.
	# Also, we have to work around a bug in pillow whereby the palette is lost on the second
	# and subsequent frames you read. One workaround is to read the palette at the beginning
	# and then put it back into the image repeatedly on each subsequent frame.  That doesn't
	# take account of the possibility that the palette might change from frame to frame. The
	# following does do so. Remove either of the #necessary lines, and palettes will be lost
	frames = [ None ] * nFrames
	canvas = frames[ 0 ] = Image.new( 'RGBA', img.size )
	for i in range( nFrames ):
		if i:
			canvas = frames[ i ] = frames[ i - 1 ].copy() # sequential composition (in some GIFs, some frames will be just difference frames)
			if dispose: canvas.paste( *dispose )
			img.close(); img = Image.open( filename ) #necessary
			img.n_frames  #necessary (magic...)
			img.seek( i )
		try: canvas.alpha_composite
		except: canvas.paste( Image.alpha_composite( canvas.crop( img.dispose_extent ), img.convert( 'RGBA' ).crop( img.dispose_extent ) ), img.dispose_extent )
		else: canvas.alpha_composite( img.convert( 'RGBA' ), img.dispose_extent[ :2 ], img.dispose_extent )
		dispose = [ (0,0,0,0), img.dispose_extent ] if img.dispose else None
	img.close()
	try: url and os.remove( filename )
	except: print( 'failed to delete %s' % filename )
	return frames

# TODO:
# - logging / state-machine wrapper around tests
# - text stimuli: importing; degradation
# - copyright and disclaimer (see e.g. ShaDyLib.py)
# - forum
# - issue tracker
# 
# - test on nvidia, ATI, ...
# - test on Windows 8, 7, XP...
# - binary portability and/or performance testing on Ubuntu?
# 
# - remove foreign stimuli?
# - Bit-stealing colour logic, LUT creation and saving...
# - Shady.Video:
#   - ROI  (save time on LoadTexture calls)
#   - timing synchronization test on VideoSource updates?
#   - threaded frame acquisition when reading from video file?
#   - move VideoRecording class from Shady.Utilities to Shady.Video?
# 
# - simple blittable objects (like foreign stimuli, but _RunDynamics-capable)??
# - translate to modern OpenGL
# - chains of event handlers?
# - improve fallback RNG...
# - fix depth clipping (appears to be a pyglet artifact: something in pyglet.app.run resets the projection matrix and viewport)
# - fix auto-repeat (currently happens for some keys and not others, at least on Mac)
# - .LoadTexture() causes .anchor to change 
# 
# Pyglet-specific bugs:
# - PygletWindowing.Window( fullScreenMode=True ):  does not automatically change screen resolution *back* when Window closes
# - On Python 3.0 (but not 2.0, even though both have pyglet 1.2.4)
#   -- the 'space' key is reported by the Event system as 'windows'....(?!)
#   -- the Surface Pro 'return' key is 'return' on one version and 'enter' on the other (both have same code in pyglet.window.key - may be due to arbitary ordering)
# Pygame-specific bugs:
# - with pygame backend + PyEngine, if GL uses pyglet, first World() fails.  Subsequent Worlds seem fine...
# 
# goals
# =====
# primary development platform = Windows
# python (not matlab)
# cross-version and dependency-light (graceful loss of functionality)
# lightweight programmer's interface
# 	property linking
# 	property dynamics
# interactive prompt

# tests/issues
# ------
# tearing
# noise (distributions)
# DPI scaling
# frameskips - accelerated vs not
# linearization
# slew-rate shadows
# report tested hardware, OS, architecture, Python version, package version
# random dots
# CSF
# timing test on TextGenerator updates?

# known issues
# ------------
# whether .smoothing=1 produces round or square dots is hardware-/driver- dependent
# GLSL 1.2  and hence bad random-noise on macs
# on mac, with retina displays:
#   using the accelerator, the window size/position you ask for is not what you get (what you get is good, in that the high-res size is returned, but it's just impossible to know what size to ask for)
#   under pyglet, the window size/position you ask for is what you get (but what you get is low-res)
# on mac, everything must be in main thread (otherwise glfw backend dies, pyglet backend does not deliver events)
# 	(this also means we're limited to one World at a time)
# on mac, pyglet back-end does not grok retina displays
# on mac, SetSwapInterval(x) has no effect when x>1
# pygame cannot select screens
# pygame cannot seem to avoid tearing
# foreign stimuli cannot be depth-sorted behind Shady stimuli
# to use pyglet stimuli as foreign stimuli, we must use the pyglet back-end
# pyglet text stimuli can only be black


# others in same space
# --------------------
# Python:
# 	pyglet
# 	pyshaders (pyglet extension)
# 	PsychoPy (pyglet-based) - does this in fact do shader tricks over and above pyglet?
# 	VisionEgg (pygame-based)
# 	pyEPL
# Matlab:
# 	PsychToolbox
# 	MGL http://www.indiana.edu/~peso/wordpress/software-life/mgl/
# 
