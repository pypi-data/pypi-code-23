'''
--------------------------------------------------------------------------
Copyright (C) 2017 Lukasz Laba <lukaszlab@o2.pl>

File version 0.2 date 2017-06-01
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

import math

steel_density = 7850.0 # [kg/m]

def mass_per_meter(bar_diameter = 12): # bar_diameter [mm]
    bar_diameter = float(bar_diameter)
    area = math.pi * (bar_diameter / 1000.0)**2 / 4.0
    mass = area * steel_density
    mass = round(mass, 3)
    return mass
    
grade_signs = {'#' : 'B500A'} 
    
def decode_grade_sign(sign):
    if sign in grade_signs.keys():
        return grade_signs[sign]
    else:
        return str(sign)

# Test if main        
if __name__ == "__main__":
    pass
    print mass_per_meter(12.0)
    print decode_grade_sign('#')
    print decode_grade_sign('3')