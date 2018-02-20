# -*- coding: utf-8 -*-
"""
Created on Wed Feb  7 20:34:27 2018

@author: danaukes
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Feb  7 17:24:29 2018

@author: danaukes
"""


import cairo

ppi = 72
ppmm = 72/25.4

page_width = 44
page_height = 28

class Page(object):
    def __init__(self,filename='output.pdf',width=page_width,height=page_height):
        surface = cairo.PDFSurface(filename, page_width*ppi, page_height*ppi)

        ctx = cairo.Context(surface)
        ctx.scale (1, -1)
        ctx.translate (0, -page_height*ppi)
        
        self._surface = surface
        self._context = ctx

    def draw_poly(self,poly,line_color = (0,0,0,1),line_width=.01,fill_color=(0,0,0,1)):
        
        pt = poly.pop(0)
        self._context.move_to (*pt)
        
        for pt in poly:
            self._context.line_to (*pt)
        
        self._context.close_path ()
        self._context.set_source_rgba(*line_color)
        self._context.set_line_width(line_width)
        self._context.stroke()
    
    def close(self):
        self._surface.finish()
