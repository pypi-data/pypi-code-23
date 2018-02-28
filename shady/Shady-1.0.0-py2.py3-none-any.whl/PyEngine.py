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
Alternative implementations, in Python, of things that the ShaDyLib accelerator also does.
"""

import os
import re
import sys

if sys.version < '3': bytes = str
else: unicode = str; basestring = ( unicode, bytes )

from . import Timing

class NotYetImported( object ):
	def __init__( self, name ): self.__name = name
	def __getattr__( self, name ): raise RuntimeError( "thread-sensitive module %s has not yet been imported" % self.__name )
	def Unimport( self ): return False

GL = NotYetImported( 'GL' )

def EnableGL():
	global GL
	from . import GL
	return GL
	
def CleanUpGL():
	global GL
	if GL.Unimport():
		sys.modules.pop( GL.__name__, None )
		GL = NotYetImported( 'GL' )
	
def InitShading( width, height, glslDirectory, substitutions ):
	# accelerated
	EnableGL()
	glslVersion = GL.glGetString( GL.GL_SHADING_LANGUAGE_VERSION )
	vertexShaderSource   = os.path.join( glslDirectory, 'VertexShader.c' )
	randomNumberSource   = os.path.join( glslDirectory, 'RandomGLSL330AndUp.c' if glslVersion >= '3.3' else 'Random.c' )
	fragmentShaderSource = os.path.join( glslDirectory, 'FragmentShader.c' )
	vertexShader   = CompileShader( GL.GL_VERTEX_SHADER,   vertexShaderSource, substitutions )
	fragmentShader = CompileShader( GL.GL_FRAGMENT_SHADER, randomNumberSource, fragmentShaderSource, substitutions )
	# build shader program
	program = GL.glCreateProgram()
	GL.glAttachShader( program, vertexShader   )
	GL.glAttachShader( program, fragmentShader )
	GL.glLinkProgram( program )
	# try to activate/enable shader program, handling errors wisely
	try: GL.glUseProgram( program )
	except: print( GL.glGetProgramInfoLog( program ) ); raise
	# enable alpha blending
	GL.glTexEnvf( GL.GL_TEXTURE_ENV, GL.GL_TEXTURE_ENV_MODE, GL.GL_MODULATE )
	#GL.glEnable( GL.GL_DEPTH_TEST ) # enabling this seems to cause all kinds of confusion with the direction of z that works and the direction that does not
	GL.glEnable( GL.GL_BLEND )
	GL.glBlendEquation( GL.GL_FUNC_ADD )
	GL.glBlendFunc( GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA )
	
	GL.glPixelStorei( GL.GL_PACK_ALIGNMENT, 1 )
	GL.glPixelStorei( GL.GL_UNPACK_ALIGNMENT, 1 )
	GL.glPixelStorei( GL.GL_PACK_SKIP_ROWS, 0 )
	GL.glPixelStorei( GL.GL_UNPACK_SKIP_ROWS, 0 )
	GL.glPixelStorei( GL.GL_PACK_SKIP_PIXELS, 0 )
	GL.glPixelStorei( GL.GL_UNPACK_SKIP_PIXELS, 0 )
	# should perhaps first save (and later restore?) these state with GL.glPushClientAttrib(GL.GL_CLIENT_PIXEL_STORE_BIT) and GL.glPopClientAttrib(GL.GL_CLIENT_PIXEL_STORE_BIT)
	# see https://www.opengl.org/archives/resources/features/KilgardTechniques/oglpitfall/
	
	# set projection
	GL.glViewport( 0, 0, width, height )
	GL.glMatrixMode( GL.GL_PROJECTION )
	GL.glOrtho( 0, width, 0, height, -1.0, +1.0 ) # for reasons I do not understand, (zNear, zFar) clipping plane values other (-1.0, +1.0) do not seem to be respected
	GL.glMatrixMode( GL.GL_MODELVIEW )
	GL.glLoadIdentity()
	
	return program

def CompileShader( type, *sources ):
	# accelerated
	accumulatedSource = ''
	substitutions = {}
	for source in sources:
		if isinstance( source, basestring ):
			if not source.strip():
				continue
			token = '//#'
			if source.startswith( token ):
				for pair in re.split( '\n\s*' + token, '\n' + source.strip() )[ 1: ]:
					search, replace = pair.split( None, 1 )
					substitutions[ token + search ] = replace.strip() + '\n' + token + search
				continue
			if '\n' not in source:
				lastFileName = source
				source = open( source, 'rt' )
		if hasattr( source, 'read' ):
			source = source.read()
		accumulatedSource += '\n' + source
	for search, replace in substitutions.items(): accumulatedSource = accumulatedSource.replace( search, replace )
	#for search, replace in substitutions.items(): print( 'search for %r and replace with %r\n\n' % ( search, replace ) )
	#open( lastFileName + '.accumulated', 'wt' ).write( accumulatedSource )
	shader = GL.glCreateShader( type )
	GL.glShaderSource( shader, accumulatedSource )
	GL.glCompileShader( shader )
	result = GL.glGetShaderiv( shader, GL.GL_COMPILE_STATUS )
	if result != 1: raise Exception( "Shader compilation failed:\n" + GL.glGetShaderInfoLog( shader ) )
	return shader

def SetUpProperties( instance, world=None, proplist=None ):
	# accelerated
	
	if world is None: world = instance
	if proplist is None: proplist = instance.Properties( False )
	
	for prop in proplist: prop.__get__( instance, type( instance ) ) # fills instance-specific value from the current default (important to do this now while the instance is being initialized)
	
	instance._property_transfers = transfers = []
	for prop in proplist:
		transferFunction = prop.transfer
		if transferFunction is not None:
			if callable( transferFunction ):
				transferFunctionName = transferFunction.__name__
			else:
				transferFunctionName = transferFunction
				if transferFunctionName.startswith( 'self.' ): transferFunction = getattr( instance, transferFunctionName[ 5: ] )
				else: transferFunction = getattr( GL, transferFunctionName )
			if transferFunctionName.split( '.' )[ -1 ].strip( '_' ).startswith( 'glUniform' ):
				uniformVariableName = 'u' + prop.name[ 0 ].upper() + prop.name[ 1: ]
				uniformVariableAddress = GL.glGetUniformLocation( world._program, uniformVariableName )
				if uniformVariableAddress < 0 and not prop.custom:
					raise NameError( 'failed to find a uniform shader variable called %r' % uniformVariableName )
			else:
				uniformVariableName = None
				uniformVariableAddress = None
			wrappedTransferFunction = WrapTransferFunction( transferFunction, instance._property_storage, prop.name, uniformVariableAddress, transferFunctionName )
			wrappedTransferFunction.prop = [ prop ]
			wrappedTransferFunction.functionName = transferFunctionName
			wrappedTransferFunction.uniformVariableName = uniformVariableName
			wrappedTransferFunction.uniformVariableAddress = uniformVariableAddress
			wrappedTransferFunction.enabled = True
			transfers.append( wrappedTransferFunction )
			if uniformVariableName == 'uShady': world._masterSwitch = wrappedTransferFunction
				
def WrapTransferFunction( transferFunction, container, key, uniformVariableAddress, transferFunctionName ):
	# accelerated
	# NB: we are baking `container[key]` rather than a fixed reference to an array, so that we can allow sharing/unsharing of properties
	if uniformVariableAddress is None:
		def wrappedTransferFunction( *pargs ):
			array = container[ key ]
			if pargs: array.flat = pargs # NB: .flat is numpy-specific
			transferFunction( *array )
	else:
		def wrappedTransferFunction( *pargs ):
			array = container[ key ]
			if pargs:
				try: array.flat = pargs # NB: .flat is numpy-specific
				except: array[ : ] = pargs
			transferFunction( uniformVariableAddress, *array )
	return wrappedTransferFunction
	
def EnableTransfer( instance, *propertyNames ):
	# not accelerated, but not really used anyway
	propertyNames = [ name for arg in propertyNames for name in arg.split() ]
	for transferFunction in instance._property_transfers:
		if transferFunction.prop[ 0 ].name in propertyNames: transferFunction.enabled = True

def DisableTransfer( instance, *propertyNames ):
	# not accelerated, but not really used anyway
	propertyNames = [ name for arg in propertyNames for name in arg.split() ]
	for transferFunction in instance._property_transfers:
		if transferFunction.prop[ 0 ].name in propertyNames: transferFunction.enabled = False

def ExecuteTransfers( instance ):
	# accelerated
	verbose = instance.verbose
	if verbose:
		print( '\n' + instance._Description() )
		instance.verbose -= 1
	for transferFunction in instance._property_transfers:
		if verbose:
			if transferFunction.enabled: print( '%s: %s(%s)' % ( transferFunction.prop[ 0 ].name, transferFunction.functionName, ', '.join( str( x ) for x in transferFunction.prop[ 0 ].determine_array( instance ) ) ) )
			else: print( transferFunction.prop[ 0 ].name + ': DISABLED' )
		if transferFunction.enabled: transferFunction()

def DrawWorld( world, dt=None, t=None ):
	# dt is passed (as sole argument) by PygletWindowing when auto=True, but we will not use it
	# TODO: in PygletWindowing with auto=True, call time is delayed by the time it took to process mouse events, etc...
	if t is None: t = Timing.Seconds() # call time
	world._drawTime = t
	db = world.debugTiming
	firstFrame = ( world.framesCompleted == 0 )
	world._SortStimuli(); db and world._DebugTiming( 'Separated' )
	if firstFrame:
		GL.glClearColor( 0.0, 0.0, 0.0, 0.0 )
		GL.glClear( GL.GL_COLOR_BUFFER_BIT )
	else:
		GL.glMatrixMode( GL.GL_MODELVIEW )
		GL.glPushMatrix()
		GL.glLoadIdentity()
		world.shady = 1
		ExecuteTransfers( world )
		db and world._DebugTiming( 'Transfer' )
		GL.glClear( GL.GL_COLOR_BUFFER_BIT ) #| GL.GL_DEPTH_BUFFER_BIT
		db and world._DebugTiming( 'glClear' )
		for stimulus in world._shady_stimuli:
			if stimulus._accel: stimulus._accel.Draw(); continue  # now that ShaDyLib accelerates World objects (under the name Renderer) as well as Stimulus objects, this will not happen
			if not stimulus.visible: continue
			if stimulus.textureSlotNumber < 0: stimulus.useTexture = False
			GL.glPushMatrix()
			ExecuteTransfers( stimulus )
			GL.glPopMatrix()
		db and world._DebugTiming( 'DrawStimuli' )
		GL.glPopMatrix()
		GL.glBindTexture( GL.GL_TEXTURE_2D, 0 ) # required to support foreign stimuli
		db and world._DebugTiming( 'UnbindTexture' )
		world._masterSwitch( 0 ) # equivalent to setting world.shady = 0 and immediately transferring it
	world._FrameCallback( t )
	world.framesCompleted += 1
		
def WaitForGPU():
	# not yet accelerated
	GL.glFinish()
	
def CaptureRawRGBA( size, origin=None ):
	# accelerated 
	EnableGL()
	if origin is None: origin = ( 0, 0 )
	return GL.glReadPixels( origin[ 0 ], origin[ 1 ], size[ 0 ], size[ 1 ], GL.GL_RGBA, GL.GL_UNSIGNED_BYTE )
	
def GetNumberOfTextureSlots():
	# accelerated (as Renderer method, for convenience of access, although in principle it could be a global function)
	return GL.glGetIntegerv( GL.GL_MAX_TEXTURE_IMAGE_UNITS ) # this returns the number available for fragment-shader use although additional units may be usable by the vertex shader

def DefineQuad( listNumber, width, height ):
	# accelerated
	if listNumber < 0: listNumber = GL.glGenLists( 1 )
	GL.glNewList( listNumber, GL.GL_COMPILE )
	GL.glBegin( GL.GL_QUADS )
	#GL.glColor3f( 1, 1, 1 )
	#GL.glNormal3f( 0,      0,      -1 )
	GL.glVertex3f( width,  0,       0 )
	GL.glVertex3f( width,  height,  0 )
	GL.glVertex3f( 0,      height,  0 )
	GL.glVertex3f( 0,      0,       0 )
	GL.glEnd()
	GL.glEndList()
	return listNumber

def DrawPoints( drawModes, mode, penThickness, smoothing, nPoints, xy, offsets ):
	if   mode == drawModes.POINTS:     drawType, smoothingType = GL.GL_POINTS,     GL.GL_POINT_SMOOTH; GL.glPointSize( penThickness )
	elif mode == drawModes.LINES:      drawType, smoothingType = GL.GL_LINES,      GL.GL_LINE_SMOOTH;  GL.glLineWidth( penThickness )
	elif mode == drawModes.LINE_STRIP: drawType, smoothingType = GL.GL_LINE_STRIP, GL.GL_LINE_SMOOTH;  GL.glLineWidth( penThickness )
	elif mode == drawModes.POLYGON:    drawType, smoothingType = GL.GL_POLYGON,    GL.GL_POLYGON_SMOOTH
	else: return
	try: xy = xy.flat[ : nPoints * 2 ]
	except: xy = xy[ :nPoints * 2 ]
	if smoothing: GL.glEnable(  smoothingType )
	else:         GL.glDisable( smoothingType )
	GL.glBegin( drawType )
	xoff, yoff = offsets
	for xi, yi in zip( xy[ ::2 ], xy[ 1::2 ] ):
		if xi != xi or yi != yi: GL.glEnd(); GL.glBegin( drawType )
		else: GL.glVertex3f( xi + xoff, yi + yoff, 0.0 )
	GL.glEnd()
	

def LoadTexture( textureSlotNumber, textureID, width, height, nChannels, dataType, data, isLUT=False ):
	# accelerated
	internalFormatGL, formatGL, dtypeGL = DetermineFormats( nChannels, dataType )
	if textureID < 0: textureID = GL.glGenTextures( 1 )
	#previousActiveTextureUnit = GL.glGetIntegerv( GL.GL_ACTIVE_TEXTURE )
	textureUnitCode = GL.GL_TEXTURE0 + textureSlotNumber
	GL.glActiveTexture( textureUnitCode )
	#previousTextureID = GL.glGetIntegerv( GL.GL_TEXTURE_BINDING_2D )
	GL.glBindTexture( GL.GL_TEXTURE_2D, textureID )
	GL.glEnable( GL.GL_TEXTURE_2D )
	GL.glTexImage2D( GL.GL_TEXTURE_2D, 0, internalFormatGL, width, height, 0, formatGL, dtypeGL, data )
	GL.glTexParameterf( GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_NEAREST       if isLUT else GL.GL_LINEAR )
	GL.glTexParameterf( GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_NEAREST       if isLUT else GL.GL_LINEAR )
	GL.glTexParameterf( GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S,     GL.GL_CLAMP_TO_EDGE if isLUT else GL.GL_REPEAT )
	GL.glTexParameterf( GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T,     GL.GL_CLAMP_TO_EDGE if isLUT else GL.GL_REPEAT )
	GL.glBindTexture( GL.GL_TEXTURE_2D, 0 ) # required to support foreign stimuli
	return textureID
	
def LoadSubTexture( textureSlotNumber, textureID, column, row, width, height, nChannels, dataType, data ):
	# accelerated
	internalFormatGL, formatGL, dtypeGL = DetermineFormats( nChannels, dataType )
	#previousActiveTextureUnit = GL.glGetIntegerv( GL.GL_ACTIVE_TEXTURE )
	textureUnitCode = GL.GL_TEXTURE0 + textureSlotNumber
	GL.glActiveTexture( textureUnitCode )
	#previousTextureID = GL.glGetIntegerv( GL.GL_TEXTURE_BINDING_2D )
	GL.glBindTexture( GL.GL_TEXTURE_2D, textureID )
	GL.glEnable( GL.GL_TEXTURE_2D )
	GL.glTexSubImage2D( GL.GL_TEXTURE_2D, 0, column, row, width, height, formatGL, dtypeGL, data )
	GL.glBindTexture( GL.GL_TEXTURE_2D, 0 ) # required to support foreign stimuli

def DetermineFormats( nChannels, dataType ):
	# accelerated
	if    dataType in [ 'uint8'   ]: floating = False; dtypeGL = GL.GL_UNSIGNED_BYTE
	elif  dataType in [ 'float32' ]: floating = True;  dtypeGL = GL.GL_FLOAT
	else: raise ValueError( "dataType must be 'float32' or 'uint8'" )
	if    nChannels == 1: formatGL = GL.GL_LUMINANCE;       internalFormatGL = GL.GL_LUMINANCE       if floating else GL.GL_LUMINANCE8
	elif  nChannels == 2: formatGL = GL.GL_LUMINANCE_ALPHA; internalFormatGL = GL.GL_LUMINANCE_ALPHA if floating else GL.GL_LUMINANCE8_ALPHA8
	elif  nChannels == 3: formatGL = GL.GL_RGB;             internalFormatGL = GL.GL_RGB32F          if floating else GL.GL_RGB8
	elif  nChannels == 4: formatGL = GL.GL_RGBA;            internalFormatGL = GL.GL_RGBA32F         if floating else GL.GL_RGBA8
	else: raise ValueError( "nChannels must be 1, 2, 3, or 4" )
	return internalFormatGL, formatGL, dtypeGL

class PropertyArray( object ):
	def __init__( self, propertyName, stimuli ):
		from . import Dependencies
		self.A = Dependencies.numpy.concatenate( [ getattr( stimulus, propertyName )[ None, : ] for stimulus in stimuli ], axis=0 )
