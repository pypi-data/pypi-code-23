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
]
import os
import sys
import ast
import inspect
import weakref
import warnings
import collections
from . import DependencyManagement
from . import Dependencies; from .Dependencies import numpy, Image, ImageDraw, ImageFont
matplotlib = DependencyManagement.Import( 'matplotlib' )

# home-made 'six'-esque stuff:
try: apply
except NameError: apply = lambda x: x()
try: FileNotFoundError
except NameError: FileNotFoundError = IOError
if sys.version < '3': bytes = str
else: unicode = str; basestring = ( unicode, bytes )
def IfStringThenRawString( x ):    return x.encode( 'utf-8' ) if isinstance( x, unicode ) else x
def IfStringThenNormalString( x ):
	if str is not bytes and isinstance( x, bytes ): return x.decode( 'utf-8' )
	if str is not unicode and isinstance( x, unicode ): return x.encode( 'utf-8' )
	return x

FONTS = []
STYLES = set()

TEST = """\
1: In Xanadu did Kubla Khan
2: A stately pleasure-dome decree:
3: Where Alph, the sacred river, ran
4: Through caverns measureless to man
5: Down to a sunless sea.\
"""

def Raw2Unicode( t ):  # works around a particularly annoying Python 2 <-> 3 wrinkle
	try: t = t.encode( 'raw_unicode_escape' )
	except: pass
	return t.decode( 'utf-8' )
TEST_UNICODE = Raw2Unicode( "\xE0\xA4\xAE\xE0\xA4\xA8\xE0\xA5\x8B\xE0\xA4\xBD\xE0\xA4\xB9\xE0\xA4\xAE\xE0\xA4\xB8\xE0\xA5\x8D\xE0\xA4\xAE\xE0\xA4\xBF\x20\xE0\xA4\xB5\xE0\xA4\xBE\xE0\xA4\x95\xE0\xA5\x8D\xE0\xA4\xA4\xE0\xA5\x8D\xE0\xA4\xB5\xE0\xA4\xAE\xE0\xA5\x8D\x20\xE0\xA5\xA4\x0A\xE0\xA4\xB8\xE0\xA4\xBE\xE0\xA4\xAE\xE0\xA4\xBE\xE0\xA4\xB9\xE0\xA4\xAE\xE0\xA4\xB8\xE0\xA5\x8D\xE0\xA4\xAE\xE0\xA4\xBF\x20\xE0\xA4\x8B\xE0\xA4\x95\xE0\xA5\x83\xE0\xA4\xA4\xE0\xA5\x8D\xE0\xA4\xB5\xE0\xA4\xAE\xE0\xA5\x8D\x20\xE0\xA5\xA4" )



if matplotlib:
	import matplotlib.font_manager, matplotlib.ft2font
	class Font( object ):
		def __init__( self, filename ):
			filename = IfStringThenNormalString( filename )
			self.filename = filename.replace( '\\', '/' )
			try: ft2obj = matplotlib.ft2font.FT2Font( self.filename )
			except RuntimeError: self.good = False; return
			else: self.good = True
			self.family_name = ft2obj.family_name
			self.style = sorted( word for word in ft2obj.style_name.lower().split() if word != 'regular' )
			try: self.monospace = len( { ft2obj.load_char( ord( char ) ).horiAdvance for char in 'iM' } ) == 1
			except: self.monospace = False
			self.words = self.family_name.lower().split() + self.style
			if self.monospace: self.words += [ 'mono', 'monospace', 'monospaced' ]
			self.italic = 'italic' in self.style
			self.bold = 'bold' in self.style
		description = property( lambda self: '"' + self.family_name + '" ' + ' '.join( self.style ).title() + ( ' (monospace)' if self.monospace else '' ) )
		short_description = property( lambda self: self.family_name + ' '.join( self.style ).title() )
		def __repr__( self ): return '%s(%r)' % ( self.__class__.__name__, self.filename )
		def __str__( self ): return self.description
	fonts = [ Font( filename ) for filename in matplotlib.font_manager.findSystemFonts() ]
	fonts = { ( f.description + ' ' + repr( f.filename ) ).lower() : f for f in fonts if f.good }
	FONTS[ : ] = sorted( fonts.values(), key=lambda f: f.description )
	STYLES = { s for f in FONTS for s in f.style }
else:
	warnings.warn( 'failed to find installed system fonts (%s)' % matplotlib )

def IdentifyFont( name, styles=None ):
	if isinstance( name, ( tuple, list ) ):
		for eachName in name:
			result = IdentifyFont( eachName )
			if result is not None: return result
		return None
	name = getattr( name, 'filename', name )
	if os.path.isfile( name ): return name
	try: frame = inspect.currentframe(); whereami = os.path.dirname( inspect.getfile( frame ) )
	finally: del frame # https://docs.python.org/3/library/inspect.html#the-interpreter-stack
	newname = os.path.join( whereami, 'fonts', name )
	if os.path.isfile( name + '.ttf' ): name += '.ttf'
	elif os.path.isfile( newname ): name = newname
	elif os.path.isfile( newname + '.ttf' ): name = newname + '.ttf'
	if os.path.isfile( name ): return name
	words = name.lower().split()
	if words and words[ -1 ] == 'regular': words = words[ :-1 ]
	elif styles: words += list( styles )
	candidates = [ f for f in FONTS if all( word in f.words for word in words ) ]
	candidates.sort( key=lambda f: len( f.short_description ) )
	if candidates: return candidates[ 0 ]
	return None

def LoadFont( name='monaco', emWidthInPixels=None, lineHeightInPixels=None ):
	
	if not ImageFont:
		warnings.warn( 'failed to load font: %s\n' % ImageFont )
		return None
	
	name = IdentifyFont( name )
	name = getattr( name, 'filename', name )	
	if name is None: return None
	
	if emWidthInPixels is None and lineHeightInPixels is None:
		raise ValueError( 'must supply either emWidthInPixels or lineHeightInPixels' )
	if emWidthInPixels is not None and lineHeightInPixels is not None:
		raise ValueError( 'must supply either emWidthInPixels or lineHeightInPixels, but not both' )		
	font_size = 1
	while True:
		font = ImageFont.truetype( name, font_size ) # NB: names for installed ttf fonts are abbreviated and for some reason CASE SENSITIVE even on Windows
		if emWidthInPixels is not None and font.getsize( 'm' )[ 0 ] >= emWidthInPixels: break
		if lineHeightInPixels is not None and font.getsize( 'Th_`' )[ 1 ] >= lineHeightInPixels: break
		font_size += 1
	return font
	
def MakeTextImage( string='Hello World', position=( 0, 0 ), imageNumpy=None, anchor='upper left', align='center', **kwargs ):
	
	kwargs = dict( kwargs )
	for key in 'fill bg blockbg'.split():
		value = kwargs.get( key, None )
		if isinstance( value, ( int, float ) ): value = [ value ] * 3
		if value: kwargs[ key ] = tuple( [ max( 0, min( 255, int( round( 255.0 * x ) ) ) ) for x in value ] )
				
	if string in [ None, '' ]: string = ' '
	try: string = str( string )     # converts non-basestring objects to str
	except UnicodeEncodeError: pass # fails on unicode objects under Python 2, but that's OK - we can use the unicode object directly
	if 'font' not in kwargs: kwargs[ 'font' ] = LoadFont( kwargs.pop( 'font_name', 'monaco' ), kwargs.pop( 'font_size', 30 ) )
	kwargs.update( dict( imageNumpy=imageNumpy, position=position, string=string, anchor=anchor, align=align, defer=True ) )
	primitives = RenderTextOntoImage( **kwargs )
	if imageNumpy is None:
		size = numpy.vstack( [ primitive[ 'bbox' ][ 3:1:-1 ] for primitive in primitives ] ).max( axis=0 )
		kwargs[ 'imageNumpy' ] = imageNumpy = numpy.zeros( list( size ) + [ 4 ], 'uint8' )
	bbox = DeferredDraw( imageNumpy, primitives, blockbg=kwargs.get( 'blockbg', None ) )
	return imageNumpy

def RenderTextOntoImage( imageNumpy, position, string, border=( 0, 0 ), linespacing=1.1, align='left', anchor='lower left', bg=None, blockbg=None, defer=False, **kwargs ):
	
	kwargs.setdefault( 'fill',  ( 255, 255, 255 ) )
	font = kwargs.get( 'font', None )
	anchor = anchor.lower()
	align = align.lower()
	
	base = imageNumpy
	if base is None: base = numpy.zeros( [ 2, 2, 3 ], 'uint8' )
	imagePIL = Image.fromarray( base[:2,:2,:] )
	draw = ImageDraw.Draw( imagePIL )
	# draw.multiline_text and draw.multiline_textsize may not exist, depending on your version of PIL / pillow
	lineHeight = draw.textsize( 'Th_`', font=font )[ 1 ]
	fullLineHeight = draw.textsize( 'Th_`q', font=font )[ 1 ]
	
	if not border: border = 0
	if isinstance( border, ( int, float ) ): border = [ int( round( border * lineHeight * 0.45 ) ) ] # the 0.45 is black magic
	if len( border ) == 1: border *= 2

	lines = [ ( line if line else ' ' ) for line in string.split( '\n' ) ]
	nlines = len( lines )
	if nlines < 2: linespacing = 1
	lineStride = lineHeight * linespacing
	widths, heights = zip( *[ draw.textsize( line, font=font ) for line in lines ] )
	heights = [ max( height, fullLineHeight ) for height in heights ]
	bbwidth = max( widths ) + 2 * border[ 0 ]
	bbheight = lineStride * len( lines ) + 2 * border[ 1 ]
	if 'left' in align: xs = [ 0 for width in widths ]
	elif 'right' in align: xs = [ bbwidth - width - 2 * border[ 0 ] for width in widths ]
	else: xs = [ 0.5 * ( bbwidth - width ) - border[ 0 ] for width in widths ]
	xs = numpy.array( xs, float ) + position[ 0 ] + border[ 0 ]
	ys = numpy.array( [ i * lineStride for i in range( nlines ) ], float ) + position[ 1 ] + border[ 1 ] - ( fullLineHeight - lineHeight ) / 2.0
	if 'left' in anchor: pass
	elif 'right' in anchor: xs -= bbwidth
	else: xs -= 0.5 * bbwidth
	if 'top' in anchor or 'upper' in anchor: pass
	elif 'bottom' in anchor or 'lower' in anchor: ys -= lineStride * nlines
	else: ys -= bbheight / 2.0
	# the xs and ys are now bottom-left coordinates for each line
	xs = numpy.round( xs ).astype( int )
	ys = numpy.round( ys ).astype( int )
	primitives = []
	for x, y, width, height, line in zip( xs, ys, widths, heights, lines ):
		primitives.append( dict(
			command='text',
			kwargs=dict( xy=[ x, y ], text=line, **kwargs ),
			bgfill=bg,
			bbox=[ x - border[ 0 ], y - border[ 1 ], x + width + border[ 0 ], y + height + border[ 1 ] ],
		) )
	if defer: return primitives
	else: return DeferredDraw( imageNumpy, primitives, blockbg=blockbg )
	
def DeferredDraw( imageNumpy, primitives, blockbg=None, shift=None ):
	imagePIL = Image.fromarray( imageNumpy )
	draw = ImageDraw.Draw( imagePIL )
	bbox = [ 0, 0, 0, 0 ]
	coords = [ d[ 'bbox'] for d in primitives if 'bbox' in d ]
	if not shift: shift = ( 0, 0 )
	xshift, yshift = shift
	if coords:
		xstart, ystart, xstop, ystop = zip( *coords )
		bbox = [
			max( 0, min( xstart ) + xshift ),
			max( 0, min( ystart ) + yshift ),
			max( xstop ) + xshift, #min( imageNumpy.shape[ 1 ], max( xstop ) + xshift ),
			max( ystop ) + yshift, #min( imageNumpy.shape[ 0 ], max( ystop ) + yshift ),
		]
	if blockbg == True: blockbg = ( [ d[ 'bgfill' ] for d in primitives if d.get( 'bgfill', None ) ] + [ None ] )[ 0 ] 
	if blockbg: draw.rectangle( xy=bbox, fill=blockbg )
	for d in primitives:
		fill = d.get( 'bgfill', None )
		xy = d.get( 'bbox', None )
		if xy and fill: draw.rectangle( xy=[ coord + delta for coord, delta in zip( xy, [ xshift, yshift, xshift, yshift ] ) ], fill=fill )
	for d in primitives:
		kwargs = d[ 'kwargs' ]
		if 'xy' in kwargs: kwargs[ 'xy' ] = [ coord + delta for coord, delta in zip( kwargs[ 'xy' ], [ xshift, yshift, xshift, yshift ] ) ]
		getattr( draw, d[ 'command' ] )( **d[ 'kwargs' ] )
	imageNumpy.flat = numpy.array( imagePIL ).flat
	return bbox  # if you expand this as (xstart, ystart, xstop, ystop) then the relevant slice of the image is imageNumpy[ xstart:xstop, ystart:ystop, : ]


from . import Rendering

QUERY = object()

class TextGenerator( Rendering.Scheduled ):
	
	DEFAULTS = dict(
		align = 'left',
		border = ( 0, 0 ),
		linespacing = 1.1,
		fill = ( 1.0, 1.0, 1.0 ),
		bg = None,
		blockbg = None,
	)
	
	stimulus = Rendering.Scheduled.parent  # property
	
	def __init__( self, string='hello', stimulus=None, **kwargs ):
		self.__font_size = ( 'lineheightinpixels', 35 )
		self.__font_family = 'monaco'
		self.__font_styles = set()
		self.__font_found = False
		self.__font_changed = True
		self.__formatting_options = d = dict(
			string = string,
			font = None,
		)
		d.update( self.DEFAULTS )
		self.__formatting_changed = True
		self.__image_changed = False
		self.Set( **kwargs )
		self.stimulus = stimulus
		
	
	def _Property( self, optionName, newValue=QUERY ):
		opt = optionName.lower().replace( '_', '' )
		if opt in STYLES:
			oldValue = ( opt in self.__font_styles )
			if newValue is QUERY or newValue == oldValue: return oldValue
			if newValue: self.__font_styles.add( opt )
			else: self.__font_styles.remove( opt )
			self.__font_changed = True
		elif opt in [ 'style' ]:
			oldValue = ' '.join( sorted( self.__font_styles ) ).title()
			if not oldValue: oldValue = 'Regular'
			if newValue is QUERY: return oldValue
			if not newValue: newValue = 'Regular'
			newValue = { x for x in newValue.lower().split() if x != 'regular' }
			if self.__font_styles == newValue: return oldValue
			self.__font_styles = newValue
			self.__font_changed = True
		elif opt in [ 'family', 'familyname', 'fontfamily', 'fontname', 'font' ]:
			if hasattr( newValue, 'family_name' ):
				if self.__font_styles != newValue.style:
					self.__font_changed = True
					self.__font_styles = set( newValue.style )
				newValue = newValue.family_name
			oldValue = self.__font_family
			if newValue is QUERY or newValue == oldValue: return oldValue
			if newValue is None: newValue = 'default'
			self.__font_family = newValue
			self.__font_changed = True
		elif opt in [ 'emwidthinpixels', 'lineheightinpixels' ]:
			oldType, oldValue = self.__font_size
			if newValue is QUERY: return oldValue if opt == oldType else None
			if newValue is None: return
			if ( opt, newValue ) == ( oldType, oldValue ): return oldValue
			self.__font_size = ( opt, newValue )
			self.__font_changed = True
		elif opt in self.__formatting_options:
			if opt == 'string' and newValue not in [ None, QUERY ]:
				try: newValue = str( newValue ) # converts non-basestring objects to str
				except UnicodeEncodeError: pass # fails on unicode objects under Python 2, but that's OK - we can use the unicode object directly
				if not newValue: newValue = ' '
			oldValue = self.__formatting_options[ opt ]
			if newValue is QUERY or newValue == oldValue: return oldValue
			self.__formatting_options[ opt ] = newValue
			self.__formatting_changed = True
	
	def _Update( self ):
		if self.__font_changed:
			self.__font_changed = False
			sizeMode, sizeValue = self.__font_size
			if   sizeMode.startswith( ( 'e', 'w' ) ): sizeMode = 'emWidthInPixels'
			elif sizeMode.startswith( ( 'l', 'h' ) ): sizeMode = 'lineHeightInPixels'
			font = IdentifyFont( self.__font_family, styles=self.__font_styles )
			fname = getattr( font, 'family_name', None )
			if fname is not None: self.__font_family = fname
			style = getattr( font, 'style', None )
			if style is not None: self.__font_styles = set( style )
			self.__font_found = font is not None
			if not self.__font_found: font = 'monaco'
			self.__formatting_options[ 'font' ] = LoadFont( font, **{ sizeMode : sizeValue } )
			self.__formatting_changed = True
		if self.__formatting_changed:
			self.__formatting_changed = False
			self.__image = MakeTextImage( **self.__formatting_options )
			self.__image_changed = True
		if not self.__image_changed: return
		stimulus, world = self.stimulus, self.world
		if stimulus is None or world is None: return
		stimulus.LoadTexture( self.__image, True )
		self.__image_changed = False
	
	@property
	def font_found( self ): return self.__font_found

for name in STYLES:
	TextGenerator._MakeProperty( name )	
TextGenerator._MakeProperty( 'family', 'family_name', 'font', 'font_family', 'font_name' )
TextGenerator._MakeProperty( 'emWidthInPixels', 'em' )
TextGenerator._MakeProperty( 'lineHeightInPixels', 'size' )
TextGenerator._MakeProperty( 'string' )
TextGenerator._MakeProperty( 'style' )
for name in TextGenerator.DEFAULTS:
	TextGenerator._MakeProperty( name )

def MakeTextProperty():
	def fget( self ): return getattr( self, '_text', None )
	def fset( self, value ):
		obj = getattr( self, '_text', None )
		if value is None or isinstance( value, TextGenerator ):
			if obj:
				obj.CancelUpdate()
				self.world()._Defer( self.LoadTexture, [ [] ] )
			self.SetDynamic( 'text', None, order=2 )
			self._text = value
			if value: value.stimulus = self
		else:
			if obj is None: obj = self._text = TextGenerator( string=' ', stimulus=self )
			if callable( value ): return self.SetDynamic( 'text', value, order=2 )
			self.SetDynamic( 'text', None, order=2 )
			obj.string = value
	return property( fget=fget, fset=fset )
	
Rendering.Stimulus.text = MakeTextProperty()

# TODO:
# - test gracefulness of dependency disintegration
