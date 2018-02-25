'''
--------------------------------------------------------------------------
Copyright (C) 2017 Lukasz Laba <lukaszlab@o2.pl>

File version 0.3 date 2017-08-10
This file is part of DxfStructure (structural engineering dxf drawing system).
http://struthon.org/

DxfStructure is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

DxfStructure is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Foobar; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
--------------------------------------------------------------------------
'''

logiclayers =        {   'DS_CBAR' :        [133, 30, 'CONTINUOUS'],
                    'DS_CTEXT' :            ['yellow', 20, 'CONTINUOUS'],
                    'DS_STEXT' :            [4, 20, 'CONTINUOUS'],
                    'DS_DEPLINE' :          [46, 15,'CONTINUOUS'],
                    'DS_ELEMENT' :          [234, 20, 'CONTINUOUS'],
                    'DS_RANGE' :            [92, 18, 'CONTINUOUS'],
                    'DS_SCHEDULECONCRETE' : ['yellow', 20, 'CONTINUOUS'],
                    'DS_SCHEDULESTEEL' :    ['yellow', 20, 'CONTINUOUS'],
                    'DS_COMMAND' :          [62, 15, 'CONTINUOUS'],
                    'DS_TMPCHECK' :         [186, 15, 'CONTINUOUS']
                }

drawlayers =    {   'DS_DRAW_PROFILE' :     ['green', 25, 'CONTINUOUS'],
                    'DS_DRAW_FORMWORK' :    [4, 25, 'CONTINUOUS'],
                    'DS_DRAW_BOLT' :        [52, 18, 'CONTINUOUS'],
                    'DS_DRAW_WELD' :        [233, 18,'CONTINUOUS'],
                    'DS_DRAW_DIM' :         ['red', 20, 'CONTINUOUS'],
                    'DS_DRAW_REMARK' :      ['yellow', 18, 'CONTINUOUS'],
                    'DS_DRAW_AXIS' :        [9, 16, 'CONTINUOUS']
                }

layers = dict(logiclayers.items() + drawlayers.items())

layer_name_list = layers.keys()

def color_for_layer(layer_name):
    return layers[layer_name][0]
    
def width_for_layer(layer_name):
    return layers[layer_name][1]
    
def linetype_for_layer(layer_name):
    return layers[layer_name][2]
    
# Test if main        
if __name__ == "__main__":  
    print layer_name_list
        
# Test if main        
if __name__ == "__main__":
    print layer_name_list
    print color_for_layer('DS_DRAW_DIM')
    print width_for_layer('DS_DRAW_DIM')
    print linetype_for_layer('DS_DRAW_DIM')
    
    
    
    
    
    
    
    
    
    
    