# -*- coding: utf-8 -*-
"""
A collection of tools used to compute manufacturing geometry useful for laminates and layers.

Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>asu.edu.
Please see LICENSE for full license.
"""

import foldable_robotics
from foldable_robotics.laminate import Laminate
from foldable_robotics.layer import Layer
import shapely.geometry as sg
import shapely.ops as so
import matplotlib.pyplot as plt
plt.ion()


def cleanup(input1,value,resolution=None):
    '''
    Cleans up the layer or laminate by using successive dilate and erode functions to remove small objects.  Results in rounded edges
    
   :param input1: input shape
   :type input1: Layer or Laminate
   :param value: dilate / erode radius
   :type value: float
   :param resolution: resolution
   :type resolution: float
   :rtype: Layer or Laminate
    '''   
    resolution = resolution or foldable_robotics.resolution

    return input1.buffer(value,resolution).buffer(-2*value,resolution).buffer(value,resolution)
    
def cleanup2(a,radius,resolution=None):
    '''
    Cleans up the layer or laminate by using successive dilate and erode functions to remove small objects.  Attempts to address rounded corners with additional CSG logic, at the cost of computation and non-intuitive results.
    
   :param a: input shape
   :type a: Layer or Laminate
   :param radius: dilate / erode radius
   :type radius: float
   :param resolution: resolution
   :type resolution: float
   :rtype: Layer or Laminate
    '''   
    resolution = resolution or foldable_robotics.resolution

    c=(a.buffer(-radius,resolution)).buffer(2*radius,resolution)
    e=(a&c)
    bb=(a.buffer(10*radius,resolution))
    b=bb-a
    d=(b.buffer(-radius,resolution)).buffer(2*radius,resolution)
    
    f=(b&d)
    g=bb-f
    
    h = e^g
    
    i = a^h
    return i

def unary_union(laminate):
    '''
    Unions all the layers in a laminate together and returns to a new Layer.
    
   :param laminate: input shape
   :type laminate: Laminate
   :rtype: Layer
    '''   

    result = Layer()
    for layer in laminate:
        result|=layer
    return result

def keepout_laser(laminate):
    """This function computes the keepout laminate for a laser cut operation..
    
   :param laminate: input shape
   :type laminate: Laminate
   :rtype: Laminate
    """
    result = unary_union(laminate)
    result = [result]*len(laminate)
    new_lam  = Laminate(*result)
    return new_lam 
#
def keepout_mill_up(laminate):
    """This function computes the keepout laminate for a milling operation with the mill above the top layer.
    
   :param laminate: input shape
   :type laminate: Laminate
   :rtype: Laminate
    """    
    result = Layer()
    results = []
    for layer in laminate[::-1]:
        result|=layer
        results.append(result.copy())
    new_lam = Laminate(*results)
    new_lam = new_lam[::-1]
    return new_lam

def keepout_mill_down(laminate):
    """This function computes the keepout laminate for a milling operation with the mill below the bottom layer.
    
   :param laminate: input shape
   :type laminate: Laminate
   :rtype: Laminate
    """    
    return keepout_mill_up(laminate[::-1])[::-1]
#
def keepout_mill_flip(laminate):
    """This function computes the keepout laminate for a milling operation with the mill cutting from above and below.
    
   :param laminate: input shape
   :type laminate: Laminate
   :rtype: Laminate
    """        
    dummy1 = keepout_mill_up(laminate)
    dummy2 = keepout_mill_down(laminate)
    dummy3 = dummy1 & dummy2
    return dummy3
#    
def bounding_box(laminate):
    """This function computes a bounding box aligned with the x and y axes for the given laminate.
    
   :param laminate: input shape
   :type laminate: Laminate
   :rtype: Laminate
    """  
    
    A = keepout_laser(laminate)
    b = so.unary_union(A[0].geoms)
    c = sg.box(*b.bounds)
    result = Layer(c)
    result = [result]*len(laminate)
    new_lam  = Laminate(*result)
    return new_lam 

def not_removable_up(laminate,is_adhesive):
    """This function computes the non-removable material in the up direction for a given laminate.  
    
   :param laminate: input shape
   :type laminate: Laminate
   :param is_adhesive: list of booleans indicating whether the layer at that index is an adhesive layer.
   :type is_adhesive: list
   :rtype: Laminate
    """      
    result = Layer()
    results = []
    for layer in laminate[::-1]:
        result|=layer
        results.append(result.copy())
    new_lam = Laminate(*results)
    new_lam = modify_up(new_lam,is_adhesive)    
    new_lam = new_lam[::-1]

    return new_lam

def not_removable_down(laminate,is_adhesive):
    """This function computes the non-removable material in the down direction for a given laminate.  
    
   :param laminate: input shape
   :type laminate: Laminate
   :param is_adhesive: list of booleans indicating whether the layer at that index is an adhesive layer.
   :type is_adhesive: list
   :rtype: Laminate
    """      
    return not_removable_up(laminate[::-1],is_adhesive[::-1])[::-1]

def not_removable_both(laminate):
    """This function computes the non-removable material in the either direction for a given laminate.  
    
   :param laminate: input shape
   :type laminate: Laminate
   :rtype: Laminate
    """      
    
    result = unary_union(laminate)
    new_lam = result.to_laminate(len(laminate)) 
    return new_lam 
    
def modify_up(laminate,is_adhesive):
    laminate = laminate.copy()
    for ii,(test1,test2) in enumerate(zip(is_adhesive[:-1],is_adhesive[1:])):
        if test1 or test2:
            laminate[ii+1] |= laminate[ii]
    return laminate
    
def zero_test(laminate):
    """This function checks whether a laminate is empty.  
    
   :param laminate: input shape
   :type laminate: Laminate
   :rtype: boolean
    """      
    
    result = keepout_laser(laminate)
    if not result[0].geoms:
        return True
    else:
        return False
        
def support(laminate,keepout_method,width,invalid_width, small_dim = .001):
    """This function computes support for a laminate.  
    
   :param laminate: input shape
   :type laminate: Laminate
   :param keepout_method: the keepout method selected for the computation
   :type keepout_method: python function ref
   :param width: gap away from the original laminate
   :type width: float
   :param invalid_width: value to keep support away from non-cuttable regions.
   :type invalid_width: float
   :param small_dim: relatively small dimension for eliminating numerical precision problems.
   :type small_dim: float   
   :rtype: Laminate
    """       
    keepout = keepout_method(laminate)
    all_support = (keepout<<width)-keepout
    not_cuttable = keepout-laminate
    not_cuttable_clean= cleanup(not_cuttable,small_dim,0)
    valid_support = all_support-(not_cuttable_clean<<invalid_width)
    valid_support <<= small_dim
    return valid_support

def split_laminate_by_geoms(laminate):
    """This function splits a laminate into n respective geometries and returns one laminate for each geom.  
    
   :param laminate: input shape
   :type laminate: Laminate
   :rtype: list of Laminates
    """         
    l = len(laminate)
    all_laminates = []
    for ii,layerfrom in enumerate(laminate):
        for jj,geom in enumerate(layerfrom.geoms):
            split_layers = [Layer()]*ii+[Layer(geom)]+[Layer()]*(l-1-ii)
            split= Laminate(*split_layers)
            all_laminates.append(split)
    return all_laminates

def _expand_adhesive(laminate,adhesive):
    '''
    Sub-function used for computing the effect of an adhesive geometry on its neighbors.
    
    :param laminate: input shape
    :type laminate: Laminate
    :param adhesive: indicates whether each layer sticks to its neighbors.
    :type adhesive: list of booleans
    :rtype: Laminate
    '''   
    l = len(laminate)
    expand_up = Laminate(*([Layer()]*l))
    for ii,(layer,test,test2) in enumerate(zip(laminate[:-1],adhesive[:-1],adhesive[1:])):
        if test or test2:
            expand_up[ii+1] = layer.copy()

    expand_down = Laminate(*([Layer()]*l))
    for ii,(layer,test,test2) in enumerate(zip(laminate[1:],adhesive[1:],adhesive[:-1])):
        if test or test2:
            expand_down[ii+1-1] = layer.copy()
            
    result = laminate|expand_up|expand_down
    return result

def find_connected(laminate,adhesive):
    '''
    Creates a list of laminates which are topologically connected above or below and across multiple layers.
    
    :param laminate: input shape
    :type laminate: Laminate
    :param adhesive: indicates whether each layer sticks to its neighbors.
    :type adhesive: list of booleans
    :rtype: Laminate
    '''   

    all_laminates = split_laminate_by_geoms(laminate)
    results = []
    while not not all_laminates:
        result = all_laminates.pop(0)
        expanded_result = _expand_adhesive(result,adhesive)
        changed=True
        while changed:
            changed=False
            for item in all_laminates:
                if not zero_test(item&expanded_result):
                    result |= item
                    expanded_result = _expand_adhesive(result,adhesive)
                    all_laminates.remove(item)
                    changed = True
        results.append(result)
    return results

def map_line_stretch(self,p1,p2,p3,p4):
    '''
    Transforms a layer or laminate by using the translation and rotation between two lines to compute the stretch, scale, and rotation. 
    
    :param self: input shape
    :type self: Layer or Laminate
    :param p1: point 1 of line 1 in (x,y) format
    :type p1: tuple
    :param p1: point 2 of line 1 in (x,y) format
    :type p1: tuple
    :param p1: point 1 of line 2 in (x,y) format
    :type p1: tuple
    :param p1: point 2 of line 2 in (x,y) format
    :type p1: tuple
    :param kwargs: unused
    :type kwargs: dict
    :rtype: Layer or Laminate
    '''   

    import math
    import numpy
    import foldable_robotics.geometry as geometry
    
    p1 = numpy.array(p1)
    p2 = numpy.array(p2)
    p3 = numpy.array(p3)
    p4 = numpy.array(p4)

    x_axis = numpy.array([1,0])

    v1 = p2-p1
#    pre_rotate = geometry.angle(x_axis,p2-p1)
    pre_rotate = math.atan2(*v1[::-1])

    v2 = p4-p3
    post_rotate = geometry.total_angle(x_axis,p4-p3)
    post_rotate = math.atan2(*v2[::-1])

    scale = geometry.length(p4-p3)/geometry.length(p2-p1)

    laminate = self.translate(*(-p1))
    laminate = laminate.rotate(-pre_rotate*180/math.pi,origin=(0,0))
    laminate = laminate.affine_transform([scale,0,0,1,0,0])
    laminate = laminate.rotate((post_rotate)*180/math.pi,origin=(0,0))
    laminate = laminate.translate(*p3)
    return laminate    
    
def modify_device(device,custom_support_line,support_width,support_gap,hole_buffer):
    '''
    From a list of two-coordinate tuples, creates shapely lines.
    
   :param device: input shape
   :type device: Laminate
   :param custom_support_line: desired additional support geometry
   :type custom_support_line: Laminate
   :param support_width: width of desired support
   :type support_width: float
   :param support_gap: gap between device and support
   :type support_gap: float
   :param hole_buffer: gap between user-supplied support and computed support hole
   :type hole_buffer: float
   :rtype: Laminate
    '''   

    custom_support = custom_support_line<<(support_width/2)
    custom_support_hole = (custom_support & ((device<<support_gap)-device))
    custom_support_hole2 = keepout_laser(custom_support_hole<<hole_buffer) - (custom_support_hole<<2*hole_buffer)
    modified_device = device-custom_support_hole2
    custom_cut = keepout_laser(custom_support_hole)
    return modified_device,custom_support,custom_cut

def lines_to_shapely(hinge_lines):
    '''
    From a list of two-coordinate tuples, creates shapely lines.
    
   :param hinge_lines: input shape
   :type hinge_lines: list of tuples
   :rtype: Laminate
    '''   
    hinge_line = sg.LineString([(0,0),(1,0)])
    hinge_layer = Layer(hinge_line)
    all_hinges1 = [hinge_layer.map_line_stretch((0,0),(1,0),*toline) for toline in hinge_lines]
    return all_hinges1

def calc_hole(hinge_lines,width,resolution = None):
    '''
    From a list of lines computes the hole needed at a node, based on hinge gaps.
    
   :param hinge_lines: input shape
   :type hinge_lines: list of tuples
   :param width: width of the hinge
   :type width: float
   :rtype: Laminate
    '''   

    m = len(hinge_lines)

    try:
        iter(width)
    except TypeError:
        width = [width]*m

    resolution = resolution or foldable_robotics.hole_resolution
    all_hinges1= lines_to_shapely(hinge_lines)
    all_hinges11 = [item.dilate(w/2,resolution = resolution) for item,w in zip(all_hinges1,width)]
    
    plt.figure()
    all_hinges3 = []
    for ii,hinge in enumerate(all_hinges11):
        all_hinges2 = Layer()
        for item in all_hinges11[:ii]+all_hinges11[ii+1:]:
            all_hinges2|=item
        all_hinges3.append(hinge&all_hinges2)
    
    all_hinges4 = Layer()
    for item in all_hinges3:
        all_hinges4|=item
#    all_hinges4.plot(new=True)
    
#    holes = Layer(all_hinges4)
    
    trimmed_lines = [item-all_hinges4 for item in all_hinges1]
    all_hinges = [tuple(sorted(item.geoms[0].coords)) for item in trimmed_lines]
    return all_hinges4,all_hinges

if __name__=='__main__':
    pass