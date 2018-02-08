"""
Functions for writing SVG images to disk.
"""
from enum import Enum

__author__ = "Martin Rusilowicz"


def _get_attributes( **kwargs ):
    r = []
    
    for k, v in kwargs.items():
        if v is not None:
            k = k.replace( "_", "-" )
            
            if isinstance( v, list ) or isinstance( v, tuple ):
                v = ",".join( str( x ) for x in v )
            elif isinstance( v, Enum ):
                v = v.name
                
                if v.startswith( "n_" ):
                    v = v[2:]
                
                v = v.replace( "_", "-" )
            
            r.append( '{}="{}"'.format( k, v ) )
    
    return " ".join( r )


class EFontWeight( Enum ):
    normal = 1
    bold = 2
    bolder = 3
    lighter = 4
    n_100 = 5
    n_200 = 6
    n_300 = 7
    n_400 = 8
    n_500 = 9
    n_600 = 10
    n_700 = 11
    n_800 = 12
    n_900 = 13
    inherit = 14


class EPriority:
    LINES = 1
    RECT = 2
    TEXT = 3


class ETextAnchor( Enum ):
    start = 1
    middle = 2
    end = 3


class EAlignmentBaseline( Enum ):
    auto = 1
    baseline = 2
    before_edge = 3
    text_before_edge = 4
    middle = 5
    central = 6
    after_edge = 7
    text_after_edge = 8
    ideographic = 9
    alphabetic = 10
    hanging = 11
    mathematical = 12
    inherit = 13


TColour = str
TMarker = str
TPos = float
TFraction = float
TDashArray = str
TPriority = int


class SvgWriter:
    """
    :attribute enable_html:     Output with HTML headers. Off by default.
    :attribute enable_autosize: Automatically expand width and height to accommodate new content. On by default.
    :attribute enable_kwargs:   Permit unknown arguments to the `add_` functions. Off by default.
    """
    
    
    def __init__( self ):
        self.__defs = []
        self.__data = []
        
        self.enable_html = False
        self.enable_autosize = True
        self.enable_kwargs = False
        self.width = 128
        self.height = 128
        
        self.__defs.append( '<marker id="markerCircle" markerWidth="8" markerHeight="8" refX="5" refY="5"><circle cx="5" cy="5" r="3" style="stroke: none; fill:#00C000;"/></marker><marker id="markerArrow" markerWidth="13" markerHeight="13" refX="2" refY="6" orient="auto"><path d="M2,2 L2,11 L10,6 L2,2" style="fill: #00C000;" /></marker>' )
    
    
    def _get_header_and_footer( self ):
        if self.enable_html:
            header = '<html><body><svg width="{}" height="{}">'
            footer = '</svg></body></html>'
        else:
            header = '<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="{}" height="{}">'
            footer = '</svg></body></html>'
        
        defs = '<defs>' + "\n".join( self.__defs ) + '</defs>'
        header = header.format( self.width, self.height )
        header += defs
        
        return header, footer
    
    
    def to_string( self ):
        r = []
        header, footer = self._get_header_and_footer()
        r.append( header )
        r.extend( x[0] for x in sorted( self.__data, key = self._get_order ) )
        r.append( footer )
        
        return "\n".join( r )
    
    
    def _get_order( self, line ):
        return line[1] * 10000 + line[2]
    
    
    def _append( self, z, content ):
        self.__data.append( (content, z, len( self.__data )) )
    
    
    def _check_kwargs( self, kwargs ):
        if not self.enable_kwargs and kwargs:
            raise ValueError( "Unknown arguments passed. Did you mean to pass these parameters? If you did set `enable_kwargs` to `True` to enable unknown parameters. kwargs = {}".format( kwargs ) )
    
    
    def add_connector( self,
                       x1: TPos,
                       y1: TPos,
                       w1: TPos,
                       h1: TPos,
                       x2: TPos,
                       y2: TPos,
                       w2: TPos,
                       h2: TPos,
                       **kwargs ):
        return self.add_line( x1 + w1 / 2, y1 + h1 / 2, x2 + w2 / 2, y2 + h2 / 2, **kwargs )
    
    
    def add_line( self,
                  x1: TPos,
                  y1: TPos,
                  x2: TPos,
                  y2: TPos,
                  z: TPriority = EPriority.LINES,
                  *,
                  stroke: TColour = None,
                  stroke_width: TPos = None,
                  marker_end: TMarker = None,
                  **kwargs ):
        self._check_kwargs( kwargs )
        self.ensure_size( x1, y1 )
        self.ensure_size( x2, y2 )
        self._append( z, '<line {} />'.format( _get_attributes( x1 = x1, y1 = y1, x2 = x2, y2 = y2, stroke = stroke, stroke_width = stroke_width, marker_end = marker_end, **kwargs ) ) )
    
    
    def add_rect( self,
                  x: TPos,
                  y: TPos,
                  w: TPos,
                  h: TPos,
                  z: TPriority = EPriority.RECT,
                  *,
                  rx = TPos,
                  ry = TPos,
                  fill = TColour,
                  stroke = TColour,
                  stroke_width = TPos,
                  stroke_dasharray = TDashArray,
                  fill_opacity = TFraction,
                  stroke_opacity = TFraction,
                  **kwargs ):
        self._check_kwargs( kwargs )
        self.ensure_size( x + w, y + w )
        self._append( z, '<rect {} />'.format( _get_attributes( x = x, y = y, width = w, height = h, rx = rx, ry = ry, fill = fill, stroke = stroke, stroke_width = stroke_width, stroke_dasharray = stroke_dasharray, fill_opacity = fill_opacity, stroke_opacity = stroke_opacity, **kwargs ) ) )
    
    
    def centre_text( self,
                     x: TPos,
                     y: TPos,
                     w: TPos,
                     h: TPos,
                     text: str,
                     **kwargs ):
        self.add_text( x + w / 2, y + h / 2, text, alignment_baseline = EAlignmentBaseline.middle, text_anchor = ETextAnchor.middle, **kwargs )
    
    
    def add_text( self,
                  x: TPos,
                  y: TPos,
                  text: str,
                  z: TPriority = EPriority.TEXT,
                  *,
                  font_family: str = None,
                  font_size: TPos = None,
                  font_weight: EFontWeight = None,
                  fill: TColour = None,
                  alignment_baseline: EAlignmentBaseline = None,
                  text_anchor: ETextAnchor = None,
                  **kwargs ):
        self._check_kwargs( kwargs )
        self.ensure_size( x, y )
        self._append( z, '<text {}>{}</text>'.format( _get_attributes( x = x, y = y, font_family = font_family, font_size = font_size, font_weight = font_weight, fill = fill, alignment_baseline = alignment_baseline, text_anchor = text_anchor, **kwargs ), text ) )
    
    
    def ensure_size( self, x, y ):
        if not self.enable_autosize:
            return
        
        if self.width < x:
            self.width = x
        
        if self.height < y:
            self.height = y
