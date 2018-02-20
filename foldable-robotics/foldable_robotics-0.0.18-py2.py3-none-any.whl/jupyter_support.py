# -*- coding: utf-8 -*-
"""
Created on Fri Dec 29 13:06:11 2017

@author: danaukes
"""
path_template = '''M {path} Z'''

svg_template = '''
<svg width="{width:f}" height="{height:f}">
    <path d="{paths}" style="{style}"/>
</svg>
'''    

class JupyterSupport(object):
    def __init__(self,loops):
        self.loops = loops
        self.linewidth = 3
        
    @property
    def svg_style(self):
        '''create the style string for svg'''
        
        #fill = 'fill:none'
        fill = 'fill:#00FF00'
        fill_opacity = 'fill-opacity:1'
        fill_rule = 'fill-rule:evenodd'
        stroke = 'stroke:#808080'
        stroke_width = 'stroke-width:{0}px'.format(self.linewidth)
        stroke_linecap = 'stroke-linecap:round'
        stroke_linejoin = 'stroke-linejoin:round'
        stroke_opacity = 'stroke-opacity:1'
        style_list = [fill,fill_opacity,fill_rule,stroke,stroke_width,stroke_linecap,stroke_linejoin,stroke_opacity]
        style = ';'.join(style_list)
        return style
    
    def loop_string(self,loop):
        loop = loop.tolist()
        c1 = loop.pop(0)
        loop_string = 'M '+'{0:f} {1:f}'.format(*c1)+ ' L ' +(' L '.join([('{0:f} {1:f}'.format(x,y)) for x,y in loop]))+' z'
        return loop_string 
    
    def _repr_svg_(self):
        '''create a svg representation'''
        import numpy
        loops = [numpy.array(loop) for loop in self.loops]
        
        all_points = numpy.vstack(loops)
        
        #mirror along y
        loops = [item *numpy.array([1,-1]) for item in loops]
        all_points *= numpy.array([1,-1])

        #shift minimum point to 0,0
        shift = all_points.min(0)
        loops = [loop-shift for loop in loops]
        all_points -= shift
        #find the dimensions of the shape
        dim = all_points.max(0)-all_points.min(0)
        
        #calculate the scaling according to drawing 100 pixels tall
        scaling = 100/dim[1]
        
        #scale the dimensions and exterior by the scaling factor
        dim*=scaling
        loops= [loop*scaling for loop in loops]
        
        #shift the exterior and dimensions by the width of the line
        loops = [loop + self.linewidth/2 for loop in loops]
        dim+=self.linewidth
        
        #create the path string
        
        paths = [self.loop_string(loop) for loop in loops]
        w = dim[0]
        h = dim[1]

        paths2 = ' '.join(paths)    
        #create the svg string
        svg_string = svg_template.format(paths = paths2, style=self.svg_style, width=w, height = h, width_i=int(w), height_i = int(h))
        return svg_string
    
    def __repr__(self):
        return 'Shape: '+str(self.loops)
    
shape = JupyterSupport([[(0.,0),(10,0),(10,10)],[(1.5,1),(9.5,1),(9.5,9)]])
shape._repr_svg_()
print(shape)    