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
	'Window',
	'Screens',
]
try: apply
except NameError: apply = lambda x: x()
	
import os
import sys
import ast
import time

from . import DPI
from . import Timing
from . import Rendering # TODO - work around the necessity for this mutual dependency - maybe by removing the distinction between 'devel' and 'bundled' ShaDyLibs?

# home-made `six`-esque stuff:
if sys.version < '3': bytes = str
else: unicode = str; basestring = ( unicode, bytes )
def IfStringThenRawString( x ):    return x.encode( 'utf-8' ) if isinstance( x, unicode ) else x
def IfStringThenNormalString( x ): return x.decode( 'utf-8' ) if str is not bytes and isinstance( x, bytes ) else x
try: unichr
except NameError: unichr = chr


def PackagePath( relative_path ):
	try: frame = inspect.currentframe(); here = os.path.dirname( inspect.getfile( frame ) )
	finally: del frame # https://docs.python.org/3/library/inspect.html#the-interpreter-stack
	return os.path.realpath( os.path.join( here, relative_path ) )

def Screens( pretty_print=False ):
	ShaDyLib = Rendering.LoadAccelerator() # TODO: for now, we use the ShaDyLib module instance that the Rendering submodule has currently imported, because the path-wrangling and accleration preferences will have been dealt with there
	if pretty_print: print( ShaDyLib.Screens( False ) )
	else: return ast.literal_eval( ShaDyLib.Screens( True ) )

class Window( object ):
	"""
	Contains the ShaDyLib-specific code for providing a window and/or changing the screen mode,
	double-buffering and flipping. This is done by providing a thin compatibility wrapper around
	a binary dynamic library. Unlike the other Windowing options, this performs OpenGL initialization
	and automatic setup of a Renderer (all within the DLL).
	"""
	
	accelerated = True
	
	@staticmethod
	def TabulaRasa():
		pass

	@staticmethod
	def CloseAll():
		raise NotImplementedError( "TODO" )

	def __init__( self, width=None, height=None, left=0, top=0, screen=None, frame=False, fullScreenMode='auto', visible=True, openglContextVersion=0, glslDirectory=None, substitutions='' ):
		
		ShaDyLib = Rendering.LoadAccelerator() # TODO: for now, we use the ShaDyLib module instance that the Rendering submodule has currently imported, because the path-wrangling and accleration preferences will have been dealt with there
		if glslDirectory is None: glslDirectory = PackagePath( 'glsl' )
		if width  is None: width  = -1
		if height is None: height = -1
		# if fullScreenMode in [ None, 'auto' ]: the dll-wrapper will deal with it on the next line:
		self.excepthook = None
		self.event_handler = self.DefaultEventHandler
		self.on_close = None
		self._wrapped_event_receiver = ShaDyLib.EventCallback( self.HandleEvent ) # must assign this wrapped object as an attribute here, otherwise the garbage-collector will get it and the callback will cause a segfault when it happens
		self._accel = ShaDyLib.Window( width=width, height=height, left=left, top=top, screen=screen, frame=frame, fullScreenMode=fullScreenMode, visible=visible, openglContextVersion=openglContextVersion, glslDirectory=glslDirectory, substitutions=substitutions )
		self._accel.SetEventCallback( self._wrapped_event_receiver )
		if DPI.GetDPIAwareness() == 0: print( 'Failed to disable DPI scaling (check python.exe properties -> Compatibility)' )
		
	def DefaultEventHandler( self, event ):
		print( event )
		if event.type == 'keyup' and event.key in [ 'q', 'escape' ]: self.Close()
		
	def HandleEvent( self, params ):
		if not self.event_handler: return
		NULL = 'NULL';
		event = eval( 'Event( self, ' + IfStringThenNormalString( params ) + ')' )
		try: self.event_handler( event )
		except Exception as err:
			if not self.excepthook: raise
			sys.stderr.write( '\nFailed to handle %s\n' % event )
			self.excepthook( *sys.exc_info() )
				
	def Run( self, render_func=None, event_func=None, auto=True ):
		# ``render_func`` is unused, and included for compatibilty with other windowing implementations
		# ``auto`` is unused, and included for compatibilty with other windowing implementations
		if event_func is None: event_func = self.DefaultEventHandler
		self.event_handler = event_func
		self._accel.Run()
		self.event_handler = self.DefaultEventHandler
	
	def GetRenderer( self ): return self._accel.GetRenderer()
	def Close( self ):
		if getattr( self, 'on_close', None ): self.on_close()
		try: self._accel.Close
		except: pass
		else: self._accel.Close()
	@apply
	def visible():
		def fget( self ): return self._accel.visible
		def fset( self, value ): self._accel.visible = value
		return property( fget=fget, fset=fset )
	@property
	def width( self ): return self._accel.width
	@property
	def height( self ): return self._accel.height
	@property
	def size( self ): return self._accel.size
	
class Event( object ):
	def __init__( self, window, **kwargs ):
		for field in 'key button modifiers x y dx dy text'.split(): kwargs.setdefault( field, None )
		self.__dict__.update( kwargs )
		if self.modifiers is None: self.modifiers = ''
		if self.button is None: self.button = ''
			
		# make "up" the positive y direction
		if self.dy is not None: self.dy *= -1
		if self.y is not None: self.y = window.height - self.y - 1
			
		# compute dx, dy for mouse_motion if they're not already there
		if self.type == 'mouse_enter': window.prev_mouse_pos = self.x, self.y
		elif self.type == 'mouse_leave': window.prev_mouse_pos = None, None
		elif self.type == 'mouse_motion':
			prevx, prevy = getattr( window, 'prev_mouse_pos', ( None, None ) )
			if prevx is not None and self.dx is None: self.dx = self.x - prevx
			if prevy is not None and self.dy is None: self.dy = self.y - prevy
			window.prev_mouse_pos = self.x, self.y
		
		if isinstance( self.text, int ): self.text = unichr( self.text )
	def __repr__( self ): return 'Event(' + ', '.join( [ '%s=%r' % ( k, v ) for k, v in sorted( self.__dict__.items() ) ] ) + ')'
