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
	'ScreenNonlinearity',
	'Linearize',
	'Tukey',
	'Hann', 
	'Sinusoid',
	
	'EllipticalTukeyWindow',
	'LinearizationTestPattern',
	'CheckPattern',
	
	'RelativeLocation',
	
	'FindGamma',
	'TearingTest',
	'PixelRuler',
	
	'PlotTimings',
	'Histogram',
	
	'VDP', 'PixelsToDegrees', 'DegreesToPixels',
	
	'ThreadedShell', 'CommandLine',
	'WorldConstructorCommandLine', 'AutoFinish',
	
	'VideoRecording',
]
import sys
import math
import atexit
import inspect
import warnings
import textwrap
import threading

from . import Logging
from . import CommandLineParsing; from .CommandLineParsing import CommandLine
from . import DependencyManagement
from . import Dependencies; from .Dependencies import numpy

# 1-D helper functions
def ScreenNonlinearity( value, gamma='sRGB' ):
	"""
	Inverse of Linearize()
	"""
	cls = float if isinstance( value, ( int, float ) ) else None
	value = numpy.array( value, dtype='float64', copy=True )
	if gamma is 'sRGB':  # NB: looks very similar to a gamma of 2.2, even though the exponent it uses is 2.4
		nonlinear = value.flat > 0.04045
		value.flat[ ~nonlinear ] /= 12.92
		value.flat[ nonlinear ]  += 0.055
		value.flat[ nonlinear ]  /= 1.055
		value.flat[ nonlinear ] **= 2.4
	else:
		value **= gamma
	return cls( value ) if cls else value

def Linearize( value, gamma='sRGB' ):
	"""
	Inverse of ScreenNonLinearity()
	"""
	cls = float if isinstance( value, ( int, float ) ) else None
	value = numpy.array( value, dtype='float64', copy=True )
	if gamma is 'sRGB':  # NB: looks very similar to a gamma of 2.2, even though the exponent it uses is 2.4
		nonlinear = value.flat > 0.04045 / 12.92
		value.flat[ nonlinear ] **= 1.0 / 2.4
		value.flat[ nonlinear ]  *= 1.055
		value.flat[ nonlinear ]  -= 0.055
		value.flat[ ~nonlinear ] *= 12.92
	else:
		value **= 1.0 / gamma
	return cls( value ) if cls else value

def Tukey( x, rise=0.5, plateau=0.0, fall='rise', start=0.0 ):
	wasarray = isinstance( x, numpy.ndarray )
	if not wasarray: x = numpy.array( x, dtype=float )
	if fall == 'rise': fall = rise
	start_fall = rise + plateau
	y = numpy.zeros_like( x )
	if start: x = x - start
	if rise:
		mask = ( x > 0.0 ) & ( x <= rise )
		scaled = x[ mask ] * ( numpy.pi / rise )
		y[ mask ] = 0.5 - 0.5 * numpy.cos( scaled )
	if plateau:
		mask = ( x > rise ) & ( x <= start_fall )
		y[ mask ] = 1.0
	if fall:
		mask = ( x > start_fall ) & ( x <= start_fall + fall )
		scaled = ( x[ mask ] - start_fall ) * ( numpy.pi / fall )
		y[ mask ] = 0.5 + 0.5 * numpy.cos( scaled )
	return y

def Hann( x, rise=0.5, start=0.0 ):
	return Tukey( x, rise=rise, start=start )

def Sinusoid( x, phase_deg=0 ):
	try: sin, pi, asarray = numpy.sin, numpy.pi, numpy.asarray
	except: sin, pi, asarray = math.sin, math.pi, ( lambda x, dtype: dtype( x ) )
	return sin( 2.0 * pi * ( asarray( x, float ) + asarray( phase_deg, float ) / 360.0 ) )
	
# image/pattern generation
def AsSize( x ):
	try: x.size[ 1 ]
	except: pass
	else: return x.size[ :2 ]
	if isinstance( x, ( int, float ) ): return [ x, x ]
	try: x.size, x.flat, x.shape
	except: pass
	else:
		if x.size in [ 2, 3 ]: return list( x.flat[ :2 ] )
		#elif len( x.shape ) in [ 2, 3 ]: return list( x.shape[ :2 ] )
	try:
		if len( x ) in [ 2, 3 ]: return [ int( x[ 0 ] ), int( x[ 1 ] ) ]
	except:
		pass
	raise( 'could not interpret %r as a size specification' % x )
	
def EllipticalTukeyWindow( size, plateauProportion=0.0 ):
	"""
	Same formula as is used in FragmentShader.c
	"""
	if isinstance( size, numpy.ndarray ) and size.ndim > 1 and size.size > 2: size = [ size.shape[ 1 ], size.shape[ 0 ] ]
	size = numpy.array( size, dtype=float ).flatten()
	if size.size == 1: size = numpy.concatenate( [ size ] * 2, axis=0 )
	if size.size != 2: raise ValueError( 'size must have 1 or 2 elements' )
	width, height = size
	
	plateauProportion = numpy.array( plateauProportion, dtype=float ).flatten()
	if plateauProportion.size == 1: plateauProportion = numpy.concatenate( [ plateauProportion ] * 2, axis=0 )
	if plateauProportion.size != 2: raise ValueError( 'plateauProportion must have 1 or 2 elements' )
	ppx, ppy = plateauProportion
	
	vy, vx = numpy.ix_( numpy.arange( height, dtype=float ), numpy.arange( width, dtype=float ) )
	if numpy.isnan( ppx ) or ppx < 0.0 or ppx > 1.0: vx.flat = 0.0; ppx = 1.0
	if numpy.isnan( ppy ) or ppy < 0.0 or ppy > 1.0: vy.flat = 0.0; ppy = 1.0
	vx -= vx.mean(); vx *= 2.0
	vy -= vy.mean(); vy *= 2.0
	v = vx + 1j * vy
	vlen = numpy.abs( v ) 
	vn = v + 0.0
	mask = vlen != 0.0
	vn[ mask ] /= vlen[ mask ]
	ellipseAxes = width * ppx,  height * ppy
	def InverseLength( c, xweight=1.0, yweight=1.0 ):
		if xweight != 1.0 or yweight != 1.0: c = xweight * c.real + 1j * yweight * c.imag
		length = numpy.abs( c )
		length[ length == 0.0 ] = 1.0
		return 1.0 / length
	r_inner = ellipseAxes[ 0 ] * ellipseAxes[ 1 ] * InverseLength( vn, ellipseAxes[ 1 ], ellipseAxes[ 0 ] ) # inner radius, in same units as v along the direction of v
	r_outer = width * height * InverseLength( vn, height, width ) # outer radius, in same units as v along the direction of v
	rlen = vlen - r_inner
	rlen *= InverseLength( numpy.clip( r_outer - r_inner, 0.0, None ) )
	return 0.5 + 0.5 * numpy.cos( numpy.pi * numpy.clip( rlen, 0.0, 1.0 ) )

def LinearizationTestPattern( canvasSize=( 1920, 1080 ), patchSize=( 50, 50 ), amplitudes=( 0.95, 0.75, 0.5, 0.25 ), plateauProportion=0.85, meanZero=True ):
	"""
	Return a 2-dimensional `numpy.array` containing a special linearization pattern.
	Blank patches are interspersed in checkerboard fashion with textured patches.
	Textured patches contain horizontal stripes, vertical stripes, and checkerboard
	patterns, all of single-pixel granularity. Textured patches vary in contrast.
	When the screen (or stimulus) is perfectly linearized, textured patches of all
	contrasts should be indistinguishable from blank patches when viewed from a
	sufficient distance (or with sufficiently bad uncorrected vision).
	
	Args:
	    canvasSize:
	        may be an `int` (resulting in a square stimulus), or a sequence of
	        two numbers (width, height). May also be a `Shady.World` instance,
	        `Shady.Stimulus` instance, a `PIL` image, or an image represented
	        as a 2- or 3-dimensional `numpy.array` - in these cases the
	        dimensions of the output match the dimensions of the instance.
	    
	    patchSize (sequence of 2 ints):
	        dimensions, in pixels, of the individual patches that make up the
	        pattern in checkerboard fashion.
	    
	    amplitudes (tuple of floats):
	        0.0 means blank, 1.0 means full contrast. 
	    
	    plateauProportion (float):
	        governs the one-dimensional raised-cosine fading at the edges of striped
	        patches.  With `plateauProportion=1`, bright and dark edge artifacts
	        tend to be visible.
	    
	    meanZero (bool):
	        if `True`, then the mean of the output array is 0 and its range is
	        `[-1,1]` when `amplitude=1`.   If `False`, then the mean of the output
	        array is 0.5 and the range is `[0,1]` when `amplitude=1`.
	    
	Returns:
	    A two-dimensional `numpy.array` containing the image pixel values.
	    
	Examples::
	
	    world.Stimulus( LinearizationTestPattern( world ) * 0.5 + 0.5 )
	    world.Stimulus( LinearizationTestPattern( world, meanZero=False ) ) # same as above
	"""
	canvasWidth, canvasHeight = [ int( round( x ) ) for x in AsSize( canvasSize ) ]
	patch = numpy.zeros( patchSize, dtype=float )
	blank = patch
	patches = []
	xfade = EllipticalTukeyWindow( patchSize, [ plateauProportion, None ] )
	yfade = EllipticalTukeyWindow( patchSize, [ None, plateauProportion ] )
	for amplitude in amplitudes:
		lo = -amplitude
		hi = +amplitude
		hstripes = patch + lo
		hstripes[ 0::2, : ] = hi 
		vstripes = patch + lo
		vstripes[ :, 0::2 ] = hi
		if 0.0 <= plateauProportion < 1.0:
			hstripes *= yfade
			vstripes *= xfade
		checks = patch + lo
		checks[ 0::2, 0::2 ] = hi
		checks[ 1::2, 1::2 ] = hi
		patches += [ hstripes, blank, vstripes, blank, checks, blank ]
	height = 0
	while height < canvasHeight:
		row = numpy.concatenate( patches, axis=1 )
		row = numpy.tile( row, ( 1, int( numpy.ceil( float( canvasWidth ) / row.shape[ 1 ] ) ) ) )[ :, :canvasWidth ]
		if height: pattern = numpy.concatenate( [ pattern, row ], axis=0 )
		else: pattern = row
		height += row.shape[ 0 ]
		patches.append( patches.pop( 0 ) )
	pattern = pattern[ :canvasHeight, :, numpy.newaxis ]
	if not meanZero: pattern += 1.0; pattern /= 2.0
	return pattern

def CheckPattern( canvasSize=( 1920, 1080 ), amplitude=1.0, checkSize=1, meanZero=True ):
	"""
	Return a 2-dimensional `numpy.array` containing a checkerboard pattern.
	
	Args:
	    canvasSize:
	        may be an `int` (resulting in a square stimulus), or a sequence of
	        two numbers (width, height). May also be a `Shady.World` instance,
	        `Shady.Stimulus` instance, a `PIL` image, or an image represented
	        as a 2- or 3-dimensional `numpy.array` - in these cases the
	        dimensions of the output match the dimensions of the instance.
	    
	    amplitude (float):
	        0.0 means blank, 1.0 means full contrast. 
	    
	    checkSize (int):
	        size, in pixels, of the individual light and dark squares making up the
	        checkerboard pattern.
	    
	    meanZero (bool):
	        if `True`, then the mean of the output array is 0 and its range is
	        `[-1,1]` when `amplitude=1`.   If `False`, then the mean of the output
	        array is 0.5 and the range is `[0,1]` when `amplitude=1`.
	    
	Returns:
	    A two-dimensional `numpy.array` containing the image pixel values.
	    
	Examples::
	
	    world.Stimulus( CheckPattern( world ) * 0.5 + 0.5 )
	    world.Stimulus( CheckPattern( world, meanZero=False ) )  # same as above
	    
	"""
	canvasWidth, canvasHeight = [ int( round( x ) ) for x in AsSize( canvasSize ) ]
	i, j = numpy.ix_( range( canvasHeight ), range( canvasWidth ) )
	i /= checkSize; j /= checkSize
	pattern = ( ( i % 2 ) == ( j % 2 ) ).astype( float )
	if meanZero: pattern *= 2.0; pattern -= 1.0
	return pattern

# custom World behaviours
def FindGamma( world, **kwargs ):
	"""
	DOC-TODO
	"""
	if 'gammatest' not in world.stimuli:
		world.Stimulus( LinearizationTestPattern( world, **kwargs ) * 0.5 + 0.5, name='gammatest', noiseAmplitude=0.005, anchor=world.anchor )
		
	def adjust_gamma( self, event ):
		if event.type == 'mouse_motion':
			x, y = RelativeLocation( event, self.stimuli.gammatest, anchor=0, normalized=True )
			# x and y range from -1 to +1
			self.stimuli.gammatest.gamma = 1.5 + y
			self.stimuli.gammatest.bluegamma *= 1.0 + 0.5 * x   
		if event.type == 'key_release':
			if event.key in [ 'escape' ]: self.Close()
			elif event.key in list( 'abcdefghijklmnopqrstuvwxyz' ):
				print( '\n%s: %s' % ( event.key.upper(), tuple( self.stimuli.gammatest.gamma ) ) )
	world.SetEventHandler( adjust_gamma )
	return world.stimuli.gammatest

def TearingTest( world, period_sec=4.0, proportional_width=0.15 ):
	"""
	DOC-TODO
	"""
	if 'canvas' not in world.stimuli: world.MakeCanvas()
	world.stimuli.canvas.bg = 0
	width = max( 100, int( math.ceil( world.width * proportional_width ) ) )
	bar = world.Patch( name='tearingtest', width=width, height=world.height, anchor=world.anchor, fg=1, x=lambda t: 0.5 * world.width * Sinusoid( t / period_sec ) )
	return bar

def RelativeLocation( loc, obj, anchor=None, normalized=False ):
	"""
	Translate a two-dimensional location `loc`...
	
	From:
	    `World` coordinates (i.e. pixels relative to the `World`'s current
	    `.anchor` position)
	To:
	    coordinates relative to the current `.xy` position of a `Stimulus`
	    instance in the same `World`, or relative to a different `.anchor`
	    position of the `World` instance.
	
	Args:
	    loc:
	        input coordinates, in pixels (single scalar or sequence of two scalars)
	
	    obj:
	        `Shady.Stimulus` or `Shady.World` instance
	
	    anchor:
	        by default, `obj.anchor` is used, but for coordinate computation purposes
	        the assumed anchor location can be overridden here using a sequence of
	        2 numbers each in the range `[-1, +1]`.
	    
	    normalized (bool):
	        If `False`, return 2-D coordinates in pixels. If `True`, return 2-D
	        coordinates in the normalized coordinate system of `obj` - this effectively
	        makes this function the inverse of `obj.Place()`.
	       
	Returns:
	    `[x, y]` coordinates, in pixels or normalized units depending on the
	    `normalized` argument.
	
	See also:
	    - Stimulus.Place()
	    - World.Place()
	
	"""
	try: x, y = loc.x, loc.y
	except: x, y = loc
	w, h = obj.size
	try: x0, y0 = obj.xy
	except: x0 = y0 = 0.0
	x = float( x ) - x0
	y = float( y ) - y0
	if anchor is None: anchor = obj.anchor
	try: xp, yp = anchor
	except: xp = yp = anchor
	x = float( x ) + int( ( 0.5 + 0.5 * obj.anchor[ 0 ] ) * w )
	y = float( y ) + int( ( 0.5 + 0.5 * obj.anchor[ 1 ] ) * h )
	x -= int( ( 0.5 + 0.5 * xp ) * w )
	y -= int( ( 0.5 + 0.5 * yp ) * h )
	if normalized: x, y =  2 * x / w, 2 * y / h
	if numpy: return numpy.array( [ x, y ] )
	return [ x, y ]

def PixelRuler( base ):
	"""
	If `base` is an image size specification, or a `World`,
	create a 90%-contrast gray `CheckPattern()` of the
	appropriate size, to use as a base.  Alternatively, `base`
	may be a ready-made image.
	
	Draw grid lines over the base: the 1st pixel (pixel 0) is not
	colored.  The 10th, 20th, 30th,... pixels (i.e. pixels 9, 19,
	29) are blue.  Similarly every 100th pixel is red and every
	1000th pixel is green.
	
	If `base` is a `World` instance, render the pattern at a
	depth of `z=0.9` and return the corresponding `Stimulus`
	instance. Otherwise just return the texture as a `numpy` array.
	"""
	world = base if hasattr( base, '_isShadyObject' ) else None
	if world: base = world.size
	try: AsSize( base )
	except: img = numpy.array( base, copy=True )
	else: img = CheckPattern( base, 0.9 )
	
	if img.dtype == 'uint8': img = img / 255.0
	else: img = 0.5 + 0.5 * img
	if img.ndim == 2: img = img[ :, :, None ]
	if img.shape[ 2 ] == 1: img = img[ :, :, [ 0, 0, 0 ] ]
	if img.shape[ 2 ] == 2: img = img[ :, :, [ 0, 0, 0, 1 ] ]
	steps = {
		  10 : [ 0.0, 0.0, 1.0 ],
		 100 : [ 1.0, 0.0, 0.0 ],
		1000 : [ 0.0, 1.0, 0.0 ],
	}
	for step, color in sorted( steps.items() ):
		for pos in range( step - 1, img.shape[ 0 ], step ):
			for channel, value in enumerate( color ): img[ pos, :, channel ] = value
			img[ pos, :, 3:4 ] = 1.0
		for pos in range( step - 1, img.shape[ 1 ], step ):
			for channel, value in enumerate( color ): img[ :, pos, channel ] = value
			img[ :, pos, 3:4 ] = 1.0
	if world: return world.Stimulus( img, name='pixelruler', z=0.9 )
	else: return img

# plotting
def PlotTimings( arg, savefig=None, **kwargs ):
	"""
	DOC-TODO
	"""
	if isinstance( arg, str ): output, timings = None, Logging.Read( arg )[ 'timings' ]
	elif isinstance( arg, dict ) and 'timings' in arg: output, timings = None, arg[ 'timings' ]
	elif hasattr( arg, 'timings' ): output, timings = arg, arg.timings
	else: output, timings = None, arg
	plt = DependencyManagement.LoadPyplot()
	plt.plot # trigger exception if not found 
	with warnings.catch_warnings():
		warnings.filterwarnings( 'ignore', message='invalid value encountered in' )
		processed = {}
		cpu = False
		t = numpy.asarray( timings[ 'DrawTimeInMilliseconds' ] ) / 1000.0
		keep = ~numpy.isnan( t )
		t = t[ keep ]
		reorder = numpy.argsort( t )
		t = t[ reorder ]
		t = t - t[ 0 ]
		for key, value in timings.items():
			value = numpy.asarray( value )[ keep ][ reorder ].copy()
			if key == 'DrawTimeInMilliseconds':
				value = numpy.diff( value.tolist() + [ numpy.nan ] )
				key = 'Delta' + key
				value[ value > 1000.0 ] = numpy.inf
				value[ value < 0.0 ] = 0.0
			processed[ key ] = value
			if key.startswith( 'cpu_' ):
				cpu = True
				smoothing = 0.9
				for i in range( 1, value.size ):
					value.flat[ i ] = smoothing * value.flat[ i - 1 ] + ( 1.0 - smoothing ) * value.flat[ i ]
		plt.clf()
		if cpu: ax1 = plt.subplot( 2, 1, 1 ); ax2 = plt.subplot( 2, 1, 2, sharex=ax1 )
		else: ax1 = plt.gca(); ax2 = None
		try: nanmean = numpy.nanmean
		except AttributeError: nanmean = lambda x: x[ ~numpy.isnan( x ) ].mean()
		for i, ( key, value ) in enumerate( sorted( processed.items(), key=lambda item: -nanmean( item[ 1 ] ) ) ):
			if key.startswith( 'cpu' ): style = '-'; plt.axes( ax2 )
			else: style = '-'; plt.axes( ax1 )
			plt.plot( t, value, style, label='%02d %s' % ( i, key ), **kwargs )
		if ax1: plt.axes( ax1 ); plt.grid( True ); plt.xlim( [ t.min(), t.max() ] ); plt.legend( loc=( 1, -1 if cpu else 0 ), labelspacing=0 ).draggable( True )
		if ax2: plt.axes( ax2 ); plt.grid( True ); plt.xlim( [ t.min(), t.max() ] ); plt.legend( loc=( 1, 0 ), labelspacing=0 ).draggable( True )
		plt.gcf().subplots_adjust( right=0.8 )
		FinishFigure( maximize=True, raise_=True, zoom=True, savefig=savefig )
	return output

def Histogram( img ):
	"""
	DOC-TODO
	"""
	plt = DependencyManagement.LoadPyplot()
	plt.plot # trigger exception if not found 
	
	if hasattr( img, 'Capture' ): img = img.Capture()
	if img.dtype == float:
		if img.min() < 0: img = 0.5 + 0.5 * img
		img = numpy.clip( img * 255.0, 0.0, 255.0 ).astype( 'uint8' )
	if img.ndim == 2: img = img[ :, :, None ]
	x = numpy.arange( 256 ) # 0 to 255 inclusive
	bin_edges = numpy.arange( 257.0 ) - 0.5   # -0.5 to 255.5 inclusive (includes rightmost edge)
	hist = lambda a: numpy.histogram( a.flat, bins=bin_edges )[ 0 ]
	plt.cla()
	if img.shape[ 2 ] in [ 1, 2 ]:
		plt.plot( x, hist( img[ :, :, 0 ] ), color='k', marker='s', clip_on=False )
	else:
		plt.plot( x, hist( img[ :, :, 0 ] ), color='r', marker='o', clip_on=False )
		plt.plot( x, hist( img[ :, :, 1 ] ), color='g', marker='x', clip_on=False )
		plt.plot( x, hist( img[ :, :, 2 ] ), color='b', marker='+', clip_on=False )
	plt.xlim( x[ [ 0, -1 ] ] )
	plt.ylim( [ 0, max( plt.ylim() ) ] )
	plt.grid( True )


def FinishFigure( maximize=False, raise_=False, pan=False, zoom=False, wait=None, savefig=None ):
	"""
	DOC-TODO
	"""
	plt = DependencyManagement.LoadPyplot()
	plt.plot # trigger exception if not found 
	
	IPython, iPythonShellInstance, ipythonIsRunning = GetIPython()
	if wait is None: wait = not ipythonIsRunning
	if ipythonIsRunning: plt.ion()
	elif wait: plt.ioff()
	plt.draw()
	try: toolbar = plt.gcf().canvas.toolbar
	except: toolbar = None
	if pan and toolbar is not None:
		try: turn_on_pan = ( toolbar._active is not 'PAN' )
		except: turn_on_pan = True
		if turn_on_pan: toolbar.pan( 'on' )
	if zoom and toolbar is not None:
		try: turn_on_zoom = ( toolbar._active is not 'ZOOM' )
		except: turn_on_zoom = True
		if turn_on_zoom: toolbar.zoom( 'on' )
	try: manager = plt.get_current_fig_manager()
	except: manager = None
	if maximize:
		try: plt.gcf().canvas._tkcanvas.master.wm_state( 'zoomed' )
		except: pass
		try: manager.window.state( 'zoomed' )
		except: pass
		try: manager.window.showMaximized()
		except: pass
		try: manager.frame.Maximize( True )
		except: pass
	if raise_:
		try: manager.window.raise_()
		except: pass
	if savefig: plt.gcf().savefig( savefig )
	if wait: plt.show()

RADIANS_PER_DEGREE = math.pi / 180.0

def ReadFileInto( filename, d ):
	exec( open( arg, 'rt' ).read(), dict( nan=float( 'nan' ), inf=float( 'inf' ) ), d )
	
def VDP( *pargs, **kwargs ):
	"""
	Return viewing distance measured in pixels. This allows easy conversion between degrees
	and pixels.
	
	If a single scalar numeric argument is provided, return it unchanged.
	
	If a string is provided, treat it the name of a Python file which defines the necessary
	settings as variables, and execute it.
	
	If a `Shady.World` object is provided, infer `widthInPixels` and `heightInPixels` from
	its size. Otherwise, if a `dict` is provided, take the necessary settings from that.
	
	Use `**kwargs` to augment / override settings.

	The necessary settings are:
	
	* viewingDistanceInMm
	
	* EITHER:   `widthInPixels`   AND  `widthInMm`
		  OR:   `heightInPixels`  AND  `heightInMm`
	
	Flexibility is allowed with these variable names: they are case-invariant and
	underscore-invariant, the `'In'` is optional, and the physical units can be mm, cm or
	m. So for example::
	
		viewing_distance_cm = 75
		
	would give the same result as::
	
		ViewingDistanceInMm = 750
	
	Example::
	
		v = VDP( world, heightInMm=169, viewingDistanceInCm=75 )
		pixelsPerDegree = DegreesToPixels( 1.0, v )
	"""
	info = {}
	
	if pargs and isinstance( pargs[ 0 ], ( float, int ) ):
		if pargs[ 1: ] or kwargs: raise TypeError( "additional arguments cannot be used when the first input argument is numeric" )
		viewingDistanceInPixels = pargs[ 0 ]
		return viewingDistanceInPixels
				
	for arg in pargs + ( kwargs, ):
		if isinstance( arg, dict ): info.update( arg )
		elif isinstance( arg, str ): ReadFileInto( arg, info )
		elif hasattr( arg, 'width' ) and hasattr( arg, 'height' ): info[ 'WidthInPixels' ], info[ 'HeightInPixels' ] = arg.width, arg.height
		else: raise TypeError( 'could not interpret input argument' )
	
	def StandardizeName( k ):
		k = k.lower().replace( '_', '' ).replace( ' ', '' ).replace( '(', '' ).replace( ')', '' )
		return k[ 6: ] if k.startswith( 'screen' ) else k
			
	def GetSetting( src, stem, **suffixes ):
		sstem = StandardizeName( stem )
		factors = { sstem + joiner + k : v for k, v in suffixes.items() for joiner in [ '', 'in' ] }
		matched = {}
		for key, value in src.items():
			factor = factors.get( StandardizeName( key ), None )
			if factor is not None and value is not None: matched[ key ] = value * factor
		if not matched: return float( 'nan' )
		if len( set( matched.values() ) ) > 1: raise ValueError( 'conflicting %s information: %s' % ( stem, ', '.join( '%s=%s' % ( k, src[ k ] ) for k in matched ) ) )
		return float( list( matched.values() )[ 0 ] )
	
	millimeters = dict( mm=1.0, millimeters=1.0, cm=10.0, centimeters=10.0, m=1000.0, meters=1000.0, )
	pixels = dict( pixels=1.0 )
	
	widthInPixels  = GetSetting( info, 'width',  **pixels )
	widthInMm      = GetSetting( info, 'width',  **millimeters )
	heightInPixels = GetSetting( info, 'height', **pixels )
	heightInMm     = GetSetting( info, 'height', **millimeters )
	viewingDistanceInMm  = GetSetting( info, 'viewing distance', **millimeters )
	
	if math.isnan( viewingDistanceInMm ):
		raise ValueError( 'need information about viewing distance, e.g.  ViewingDistanceInCm=75' )
	if math.isnan( widthInMm ) and math.isnan( heightInMm ):
		raise ValueError( 'need information about physical display size, e.g.  widthInMm=254, heightInMm=169' )
	if math.isnan( widthInPixels ) and math.isnan( heightInPixels ):
		raise ValueError( 'need information about pixel dimensions, e.g.  widthInPixels=2160, heightInPixels=1440' )
	mmPerPixelHorizontally = widthInMm  / widthInPixels
	mmPerPixelVertically   = heightInMm / heightInPixels
	if math.isnan( mmPerPixelHorizontally ) and math.isnan( mmPerPixelVertically ):
		raise ValueError( 'need both pixel and millimeter dimensions for at least one dimension, e.g.  heightInPixels=1440, heightInMm=169' )
	elif math.isnan( mmPerPixelHorizontally ):
		viewingDistanceInPixels = viewingDistanceInMm / mmPerPixelVertically
	elif math.isnan( mmPerPixelVertically ):
		viewingDistanceInPixels = viewingDistanceInMm / mmPerPixelHorizontally
	else:
		viewingDistanceInPixels = viewingDistanceInMm / ( 0.5 * mmPerPixelHorizontally + 0.5 * mmPerPixelVertically )
		aspectRatio = mmPerPixelHorizontally / mmPerPixelVertically
		if aspectRatio < 0.95 or aspectRatio > 1.05: raise ValueError( 'conflicting screen dimension settings: the specified horizontal and vertical resolutions imply non-square pixels (aspect ratio %g)' % aspectRatio )
	return viewingDistanceInPixels
	
def DegreesToPixels( extentInDegrees, screenInfo, eccentricityInDegrees=0 ):
	"""
	DOC-TODO
	"""
	if numpy: tan = numpy.tan; extentInDegrees = numpy.asarray( extentInDegrees ); eccentricityInDegrees = numpy.asarray( eccentricityInDegrees )
	else:     tan = math.tan
	viewingDistanceInPixels = VDP( screenInfo )
	startInDegrees = eccentricityInDegrees - extentInDegrees / 2.0
	endInDegrees   = eccentricityInDegrees + extentInDegrees / 2.0
	startInPixels = viewingDistanceInPixels * tan( startInDegrees * RADIANS_PER_DEGREE  )
	endInPixels   = viewingDistanceInPixels * tan( endInDegrees   * RADIANS_PER_DEGREE )
	#eccentricityInPixels   = viewingDistanceInPixels * tan( eccentricityInDegrees * RADIANS_PER_DEGREE  )
	extentInPixels = endInPixels - startInPixels
	if numpy and not extentInPixels.shape: extentInPixels = extentInPixels.flat[ 0 ]
	return extentInPixels

def PixelsToDegrees( extentInPixels, screenInfo, eccentricityInPixels=0 ):
	"""
	DOC-TODO
	"""
	if numpy: atan2 = numpy.arctan2; extentInPixels = numpy.asarray( extentInPixels ); eccentricityInPixels = numpy.asarray( eccentricityInPixels )
	else:     atan2 = math.atan2
	viewingDistanceInPixels = VDP( screenInfo )
	startInPixels = eccentricityInPixels - extentInPixels / 2.0
	endInPixels   = eccentricityInPixels + extentInPixels / 2.0
	startInDegrees = atan2( startInPixels, viewingDistanceInPixels ) / RADIANS_PER_DEGREE
	endInDegrees   = atan2( endInPixels,   viewingDistanceInPixels ) / RADIANS_PER_DEGREE
	#eccentricityInDegrees = atan2( eccentricityInPixels, viewingDistanceInPixels ) / RADIANS_PER_DEGREE
	extentInDegrees = endInDegrees - startInDegrees
	if numpy and not extentInDegrees.shape: extentInDegrees = extentInDegrees.flat[ 0 ]
	return extentInDegrees

def GetIPython():
	IPython = DependencyManagement.Import( 'IPython', packageName='ipython', registerVersion=True )
	instance = None
	isRunning = False
	if not instance:
		try: instance = IPython.get_ipython()
		except: pass
	if not instance:
		try: instance = get_ipython()
		except: pass
	if not instance:
		try: instance = __IPYTHON__  # you goalpost-moving m**********rs
		except: pass
	isRunning = instance is not None and not getattr( instance, 'exit_now', False ) and getattr( instance, 'keep_running', True )
	return IPython, instance, isRunning

def Announce( msg, wrapWidth=79 ):
	msg += '\n'
	if wrapWidth: 
		stripped = msg.lstrip( '\n' ); before = msg[ :len( msg ) - len( stripped ) ]
		stripped = msg.rstrip( '\n' ); after  = msg[ len( stripped ): ]
		msg = before + '\n'.join( textwrap.wrap( msg, wrapWidth ) ) + after
	sys.stderr.write( msg )
	try: sys.stderr.flush()
	except: pass

def ThreadedShell( on_close=None, user_ns='this', threaded=True, prefer_ipython=True ):
	"""
	One nice and highly educational way of debugging, designing or otherwise
	interacting with a `Shady.World` is to do so from an interactive prompt. This is
	easy on Windows - a `Shady.World` can be run in a background thread, so it can
	simply be started from an ongoing IPython session.  In many other OSes, this is
	not possible, because the windowing back-end typically insists on being in the
	main thread, crashing or behaving weirdly if not.
	
	This utility function turns the problem inside-out by starting an interactive
	shell in a background thread. Call this function at the end of your script but
	before `world.Run()`.  Launch your script through the ordinary Python interpreter.
	
	Example::
		
		if not world.threaded:  Shady.ThreadedShell( world.Close ); world.Run()
	
	The third-party package `IPython` is recommended, and is used if installed.
	"""
	IPython, iPythonShellInstance, ipythonIsRunning = GetIPython()
	if ipythonIsRunning: return Announce( 'It looks like IPython is already running - an additional ThreadedShell will not be started.' )
	if user_ns == 'this': user_ns = 0
	if isinstance( user_ns, int ):
		try:
			frame = inspect.currentframe()
			for i in range( abs( user_ns ) + 1 ): frame = frame.f_back
			user_ns = frame.f_locals
		finally: del frame # https://docs.python.org/3/library/inspect.html#the-interpreter-stack
	if threaded:
		thread = threading.Thread( target=ThreadedShell, kwargs=dict( user_ns=user_ns, threaded=False, on_close=on_close, prefer_ipython=prefer_ipython ) )
		thread.start()
		return thread
	if user_ns is not None: user_ns = dict( user_ns )
	if IPython and prefer_ipython and hasattr( IPython, 'start_ipython' ):
		IPython.start_ipython( argv=[], user_ns=user_ns ) # this is the payload!
		if on_close: on_close()
		# The rest is to work around a thread-related ProgrammingError exception from SQLite that happens at system exit:
		IPython, iPythonShellInstance, ipythonIsRunning = GetIPython()
		try:
			all_handlers = atexit._exithandlers # only available in Python 2.x
		except:
			handler = iPythonShellInstance.atexit_operations # unfortunately, this will presumably break sooner or later as IPython evolves (it has a track record of moving goalposts that we rely on in exactly this kind of workaround) 
			atexit.unregister( handler ) # only available in Python 3.x
			handler()
		else:
			ip_handlers = [ item for item in all_handlers if 'IPython' in repr( item ) ]
			for item in ip_handlers: all_handlers.remove( item ); func, pargs, kwargs = item; func( *pargs, **kwargs )
		if not hasattr( iPythonShellInstance, 'keep_running' ): iPythonShellInstance.keep_running = False
	else:
		if prefer_ipython:
			if not IPython: excuse = str( IPython )
			else: excuse = 'IPython version possibly too old?'
			Announce( 'The enhanced interactive shell is not available (%s). Trying fallback shell...' % excuse )
		print( sys.version )
		try: getcmd = raw_input
		except: getcmd = input
		while True:
			try: cmd = getcmd( '>>> ' )
			except ( EOFError, SystemExit ): break
			except KeyboardInterrupt as exc: print( exc )
			try: co = compile( cmd, 'user interactive input', 'single' )
			except: sys.excepthook( *sys.exc_info() )
			else:
				try: exec( co, user_ns, user_ns ) 
				except KeyboardInterrupt as exc: print( exc )
				except SystemExit: break
				except: sys.excepthook( *sys.exc_info() )
		if on_close: on_close()

def WorldConstructorCommandLine( argv=None, **defaults ):
	cmdline = CommandLine( argv=argv )
	if 'IPython' in sys.modules: IPython, iPythonShellInstance, ipythonIsRunning = GetIPython()
	else: ipythonIsRunning = False
	opt = lambda name, default, **spec: cmdline.Option( name, defaults.get( name, default ), **spec )
	opt( 'width',    default=None, position=0, type=( None, int, tuple, list ), min=1, minlength=2, maxlength=2 )
	opt( 'height',   default=None, position=1, type=( None, int ), min=1 )
	opt( 'size',     default=None,  type=( None, int, tuple, list ), min=1, minlength=2, maxlength=2 )
	opt( 'left',     default=None,  type=( None, int ) )
	opt( 'top',      default=None,  type=( None, int ) )
	opt( 'screen',   default=None,  type=( None, int ), min=0 )
	opt( 'threaded', default=sys.platform.lower().startswith( 'win' ) and ipythonIsRunning, type=bool )
	opt( 'canvas',   default=False, type=( bool ) )
	opt( 'frame',    default=False, type=( bool ) )
	opt( 'fullScreenMode',       default=None,  type=( None, bool ) )
	opt( 'visible',              default=True,  type=( bool ) )
	opt( 'openglContextVersion', default=0,     type=( int ) )
	opt( 'backend',              default=None,  type=( None, str ) )
	opt( 'acceleration',         default=None,  type=( None, bool ) )
	opt( 'debugTiming',          default=False, type=( bool ) )
	opt( 'profile',              default=False, type=( bool ) )
	opt( 'logfile',              default=None,  type=( None, str ) )
	return cmdline
	
def AutoFinish( world, shell=False, prefer_ipython=True ):
	if shell: ThreadedShell( on_close=world.Close, user_ns=-1, prefer_ipython=prefer_ipython ) and world.Run()
	if world.debugTiming: world.Run(); PlotTimings( world )
	if not world.threaded: world.Run()

class VideoRecording( object ):
	def __init__( self, filename, fps=60.0, codec='XVID', container='.avi' ):
		self.__file = None
		self.filename = filename
		self.codec = codec
		if hasattr( fps, 'fakeFrameRate' ): fps = fps.fakeFrameRate
		self.fps = fps
		self.container = container
		
	def WriteFrame( self, frame ):
		cv2 = DependencyManagement.Import( 'cv2', packageName='opencv-python', registerVersion=True )
		
		if hasattr( frame, 'Capture' ): frame = frame.Capture()
		if not self.__file:
			filename = self.filename
			container = '.' + self.container.lstrip( '.' )
			if not filename.lower().endswith( container.lower() ): filename += container
			self.__file = cv2.VideoWriter(
				filename,
				fourcc=cv2.VideoWriter_fourcc( *self.codec ),
				fps=self.fps,
				frameSize=frame.shape[ 1::-1 ],
				isColor=True,
			)
			if not self.__file.isOpened(): raise IOError( 'failed to open video file %r' % filename )
		self.__file.write( frame[ :, :, 2::-1 ] )
	
	def Close( self ):
		if self.__file and self.__file.isOpened(): self.__file.release()
		self.__file = None
	
	def __del__( self ):
		self.Close()

