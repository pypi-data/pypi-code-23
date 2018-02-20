# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>asu.edu.
Please see LICENSE for full license.
"""

#import modules from shapely and matplotlib
import shapely.geometry as sg
import matplotlib.pyplot as plt

#import classes from my local modules
from foldable_robotics.laminate import Laminate
from foldable_robotics.layer import Layer

import foldable_robotics.manufacturing

def generate():

    #create a layer named box
    box = Layer(sg.box(0,0,1,1))
    
    #initialize layer01 as box, and union with the same box translated several times
    layer01 = box
    layer01 = layer01 | box.translate(1,-1)
    layer01 = layer01.translate(.5,0)
    layer01 = layer01 | layer01.scale(-1,1)
    layer34 = layer01.scale(1,-1)
    hinge = Laminate(layer01,layer01,Layer(),layer34,layer34)
    hinge_hole = Layer(sg.box(-.5,-1,.5,1))
    hinge |= Laminate(hinge_hole,hinge_hole,hinge_hole,hinge_hole,hinge_hole)
    hinge = hinge.translate(2.5,0)
    hinge = hinge.scale(1/5,1/2)
    return hinge

if __name__=='__main__':
    hinge = generate()
#    hinge = hinge.scale(1,.1)
    hinge.plot()
    
    from foldable_robotics.dynamics_info import MaterialProperty
    import idealab_tools.plot_tris as pt
    
    m = MaterialProperty.make_n_blank(5,thickness = .1)
    
    mesh_items = hinge.mesh_items(m)
    pt.plot_mi(mesh_items)
