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
"""
This submodule is not imported by default by the parent package.
Import it for its side-effect: it enables the `.video` property
of the `Shady.Stimulus` class.

If `s` is a `Stimulus` instance and `s.video` is equal to its
default value of `None`, then saying::

    s.video = 'fish.mp4'

implicitly creates a `VideoSource` object with the `source`
property equal to `'fish.mp4'.  (If `s.video` was previously
already a `VideoSource`, object then its `source` property is
simply updated accordingly.)

The third-party package `cv2` (installable with
`pip install opencv-python`) is required for video support.
Any source readable by `cv2.VideoCapture` is acceptable: 
use an integer to open a live camera stream, or a string to
specify a video file name.
"""
__all__ = [
	'VideoSource',
]
import os
import sys
import time
import weakref
import threading

if sys.version < '3': bytes = str
else: unicode = str; basestring = ( unicode, bytes )

from . import Rendering
from . import DependencyManagement

cv2 = DependencyManagement.Import( 'cv2', packageName='opencv-python', registerVersion=True )

# home-made 'six'-esque stuff:
try: apply
except NameError: apply = lambda x: x()
try: FileNotFoundError
except NameError: FileNotFoundError = IOError


class VideoSource( Rendering.Scheduled ):
	
	stimulus = Rendering.Scheduled.parent
	
	def __init__( self, source=None, stimulus=None ):
		self.__handle = None
		self.__live = None
		self.__playing = False
		self.__newFrame = None
		self.__oldFrame = None
		self.__tprev = None
		self.__playhead = 0.0
		self.__jumpToTime = None
		self.__jumpToFrame = None
		self.__frameIndex = None
		self.__fps = None
		self.__frameCount = None
		self.__frameWidth = None
		self.__frameHeight = None
		self.__loop = False
		self.__speed = 1.0
		self.__source = None
		self.__changed = True
		self.__frameQueue = None
		self.__acquisitionThread = None
		self.__aperture = None
		self._blank = [ [ [ 0.0 ] * 4 ] ]
		self.stimulus = stimulus
		self.source = source
	
	def __del__( self ):
		self.Close()
	
	def Close( self ):
		self.CancelUpdate()
		if self.__handle and self.__handle.isOpened():
			self.__handle.release()
			self.__handle = None
		#if self.__acquisitionThread: self.__acquisitionThread.join()
				
	def _Update( self ):
		if not self.world: return
		
		if self.__handle is None:
			self.__newFrame = None
		elif self.__live:
			if self.__playing:
				if self.__frameQueue is None: self.AcquireFrames()
				if self.__frameQueue:
					self.__newFrame = self.__frameQueue.pop( 0 )
					self.__changed = True
			else:
				self.__frameQueue = None
		else:
			t = self.world.t
			if not self.__playing:     dt = 0.0; self.__tprev = None
			elif self.__tprev is None: dt = 0.0; self.__tprev = t
			else: dt = t - self.__tprev
			if dt != 0.0 or self.__jumpToTime is not None or self.__jumpToFrame is not None:
				self.__tprev = t
				if self.__jumpToFrame is not None:
					frame = int( self.__jumpToFrame )
					self.__playhead = float( frame ) / self.__fps
					self.__jumpToFrame = self.__jumpToTime = None
				else:
					if self.__jumpToTime is not None:
						self.__playhead = self.__jumpToTime
						self.__jumpToFrame = self.__jumpToTime = None
					else:
						self.__playhead += dt * self.__speed
					frame = int( self.__playhead * self.__fps )
				if self.__loop:
					frame %= self.__frameCount
				else:
					if frame < 0: frame = 0; self.__playing = False
					if frame > self.__frameCount: frame = self.__frameCount; self.__playing = False
				
				if frame != self.__frameIndex:
					if self.__frameIndex is None: self.__frameIndex = -1
					nAhead = frame - self.__frameIndex
					if nAhead < 0 or nAhead > 10:
						self.__handle.set( getattr( cv2, 'CAP_PROP_POS_FRAMES', 1 ), frame )
						nAhead = 1
					for i in range( nAhead ):
						f, pixels = self.__handle.read()
						self.__newFrame = None if pixels is None else pixels[ :, :, ::-1 ]
					self.__frameIndex = frame
					self.__changed = True
		
		stimulus = self.stimulus
		
		pixels = self.__newFrame
		if pixels is None: pixels = self.__oldFrame
		else: self.__oldFrame = pixels
		if self.Transform:
			if pixels is not None: pixels = self.Transform( pixels, self.__changed )
			if pixels is not None: self.__newFrame = pixels; self.__changed = True
		
		if self.__changed and stimulus is not None:
			pixels = self.__newFrame
			stimulus.LoadTexture( self._blank if pixels is None else pixels, pixels is not None and min( stimulus.size ) <= 1 )
			self.__newFrame = None
			self.__changed = False
			
	def Transform( self, pixelArray, pixelArrayHasChanged ):
		"""
		Overshadowable hook that allows you to transform the image before
		it is transferred as a texture to the graphics card.
		
		Return a new pixelArray if you want to transform the image on this frame
		Return None if you do not want to make a change.
		
		`pixelArrayHasChanged` is a boolean that indicates whether this
		(untransformed) frame is different from the previous (untransformed)
		frame.
		
		Note that if you choose to return non-None when `pixelArrayHasChanged`
		is False, you'll be forcing the stimulus to LoadTexture() more often than
		it otherwise would, introducing further CPU costs (over and above the cost
		of performing the transformation itself).s
		"""
		pass
		
	def Play( self, position=None, speed=None, loop=None, frame=None ):
		if loop     is not None: self.loop     = loop
		if speed    is not None: self.speed    = speed
		if position is not None: self.position = position
		if frame    is not None: self.frame    = frame
		self.__playing = True
		#return self # abandoned this because it tends to leave unwanted references to the VideoSource object hanging around in IPython prompts
	def Pause( self, position=None, speed=None, loop=None, frame=None ):
		if loop     is not None: self.loop     = loop
		if speed    is not None: self.speed    = speed
		if position is not None: self.position = position
		if frame    is not None: self.frame    = frame
		self.__playing = False
		#return self # abandoned this because it tends to leave unwanted references to the VideoSource object hanging around in IPython prompts
	@apply
	def playing():
		def fget( self ): return self.__playing
		def fset( self, value ): self.__playing = True if value else False
		return property( fget=fget, fset=fset )
	@apply
	def loop():
		def fget( self ): return self.__loop
		def fset( self, value ): self.__loop = True if value else False
		return property( fget=fget, fset=fset )
	@apply
	def speed():
		def fget( self ):
			return 1.0 if self.__live else self.__speed 
		def fset( self, value ):
			if not self.__live: self.__speed = float( value )
		return property( fget=fget, fset=fset )
	
	fps      = property( lambda self: self.__fps )
	width    = property( lambda self: self.__frameWidth )
	height   = property( lambda self: self.__frameHeight )
	size     = property( lambda self: ( self.__frameWidth, self.__frameHeight ) )
	live     = property( lambda self: self.__live )
	duration = property( lambda self: None if self.__live or not self.__handle or not self.__fps else self.__frameCount / self.__fps )
	
	@apply
	def aperture():
		def fget( self ):
			if self.__aperture is not None: return self.__aperture
			stimulus = self.stimulus
			if stimulus is None: return None
			return tuple( stimulus.envelopeSize )
		def fset( self, value ):
			stimulus = self.stimulus
			world = self.world
			if stimulus is None or world is None: return
			try: w, h = value
			except: w = h = value
			if w is None and h is None: w = h = -1 
			if w is not None and w < 0: w = self.__frameWidth
			if h is not None and h < 0: h = self.__frameHeight
			self.__aperture = ( w, h )
			def unset_aperature(): self.__aperture = None
			world._Defer( stimulus.DefineEnvelope, width=w, height=h )
			world._Defer( unset_aperature )
			
		return property( fget=fget, fset=fset )
	@apply
	def frame():
		def fget( self ):
			if self.__live or not self.__handle or not self.__fps or not self.__frameCount: return None
			return self.__frameIndex
		def fset( self, value ):
			if self.__live or not self.__handle or not self.__fps or not self.__frameCount: return
			if value in [ 'end', 'END' ]: value = self.__frameCount - 1
			if value < 0: value %= self.__frameCount
			self.__jumpToFrame = value
		return property( fget=fget, fset=fset )
	@apply
	def position():
		def fget( self ):
			if self.__live or not self.__handle or not self.__fps or not self.__frameCount: return None
			if self.__frameIndex is None: return None
			return self.__frameIndex / self.__fps
		def fset( self, value ):
			if self.__live or not self.__handle or not self.__fps or not self.__frameCount: return
			if value in [ 'end', 'END' ]: value = self.duration - 1.0 / self.__fps
			if value < 0: value %= self.duration
			self.__jumpToTime = value
		return property( fget=fget, fset=fset )
		
	@apply
	def source():
		def fget( self ): return self.__source
		def fset( self, value ):
			if self.__source == value: return 
			self.Close()
			self.__source = value
			self.__changed = True
			if value is None:
				self.__live = False
				self.__handle = None
			else:
				self.__live = not isinstance( value, basestring )
				self.__playing = self.__live
				self.__handle = cv2.VideoCapture( value )
				if isinstance( value, basestring ) and not os.path.isfile( value ): raise FileNotFoundError( 'could not open file %r' % value )
				# TODO: cv2 issues a warning if the file fails to load - suppress this, since the next line's exception should cover it
				if not self.__handle.isOpened(): raise IOError( 'failed to open video source %r' % value )
				self.__frameCount  = int(   self.__handle.get( getattr( cv2, 'CAP_PROP_FRAME_COUNT',  7 ) ) )
				self.__frameWidth  = int(   self.__handle.get( getattr( cv2, 'CAP_PROP_FRAME_WIDTH',  3 ) ) )
				self.__frameHeight = int(   self.__handle.get( getattr( cv2, 'CAP_PROP_FRAME_HEIGHT', 4 ) ) )
				self.__fps         = float( self.__handle.get( getattr( cv2, 'CAP_PROP_FPS',          5 ) ) )
				if not self.__fps: self.__fps = None
				self._blank = [ [ [ 0.0 ] * 4 ] * self.__frameWidth ] * self.__frameHeight
				#if self.stimulus: self.stimulus.textureSize = self.size
			self.ScheduleUpdate()
			self.position = 0 # shows initial frame, even if paused
		return property( fget=fget, fset=fset )
			
	def AcquireFrames( self, threaded=True ):
		if threaded:
			if self.__frameQueue is not None: return
			self.__acquisitionThread = threading.Thread( target=self.AcquireFrames, kwargs=dict( threaded=False ) )
			return self.__acquisitionThread.start()
		q = self.__frameQueue = []
		while self.__frameQueue is not None:
			if len( q ) > 5 or not self.__playing: break
			handle = self.__handle
			if not handle or not handle.isOpened(): break
			success, newFrame = handle.read()
			if newFrame is not None: q.append( newFrame[ :, :, ::-1 ] )
		self.__frameQueue = None


def MakeVideoProperty():
	def fget( self ): return getattr( self, '_video', None )
	def fset( self, value ):
		obj = getattr( self, '_video', None )
		if value is None or isinstance( value, VideoSource ):
			if obj:
				obj.CancelUpdate()
				self.world()._Defer( self.LoadTexture, obj._blank, False )
			self.SetDynamic( 'video', None, order=2 )
			self._video = value
			if value: value.stimulus = self
		else:
			if obj is None: obj = self._video = VideoSource( stimulus=self )
			if callable( value ): return self.SetDynamic( 'video', value, order=2 )
			self.SetDynamic( 'video', None, order=2 )
			if value == '': value = None
			obj.source = value
		if obj:
			def VideoCleanup( ref ): obj = ref(); obj and obj.Close()
			self.world().OnClose( VideoCleanup, weakref.ref( obj ) )
			#if value.width is not None: self.textureSize = value.size
	return property( fget=fget, fset=fset )
	
Rendering.Stimulus.video = MakeVideoProperty()
