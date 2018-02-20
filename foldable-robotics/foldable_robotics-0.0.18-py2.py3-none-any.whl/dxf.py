# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>asu.edu.
Please see LICENSE for full license.
"""

import ezdxf
import matplotlib.pyplot as plt
#plt.ion()
import numpy


#def read_lines(filename, color = None ,layer = None):
def read_lines(filename, color = None, layer = None):
    '''
    Reads a dxf file searching for line objects,

    :param filename: the file path of the source dxf
    :type filename: string
    :param color: optional.  if included, this function filters for objects of only this color
    :param layer: optional.  if included, this function filters for objects of only this layer
    :rtype: List of lines consisting of two two-coordinate tuples each.
    '''
    dwg = ezdxf.readfile(filename)
    modelspace = dwg.modelspace()
    lines = []
    for e in modelspace:
        if e.dxftype() == 'LINE':
    #        red is code 1, gets added to hinge lines
            if color is not None:
                if e.get_dxf_attrib('color')==color:
                    lines.append([(e.dxf.start[0],e.dxf.start[1]),(e.dxf.end[0],e.dxf.end[1])])
            elif layer is not None:
                if e.get_dxf_attrib('layer')==layer:
                    lines.append([(e.dxf.start[0],e.dxf.start[1]),(e.dxf.end[0],e.dxf.end[1])])
            else:
                lines.append([(e.dxf.start[0],e.dxf.start[1]),(e.dxf.end[0],e.dxf.end[1])])
    return lines

#def read_lwpolylines(filename,color = None,layer = None):
def read_lwpolylines(filename,color = None,layer = None,arc_approx = 0):
    '''
    Reads a dxf file searching for lwpolyline objects, approximating arc elements in an lwpolyline with an n-segement set of lines

    :param filename: the file path of the source dxf
    :type filename: string
    :param color: optional.  if included, this function filters for objects of only this color
    :param layer: optional.  if included, this function filters for objects of only this layer
    :param arc_approx: number of interior points to approximate an arc with
    :type arc_approx: int
    :rtype: List of lines consisting of two two-coordinate tuples each.
    '''
    dwg = ezdxf.readfile(filename)
    modelspace = dwg.modelspace()
    lines = []
    for e in modelspace:
        if e.dxftype() == 'LWPOLYLINE':
            if color is not None:
                if e.get_dxf_attrib('color')==color:
                    line = numpy.array(list(e.get_points()))
                    line_out = []
                    for ii in range(len(line)):
                        if line[ii,4]!=0:
                            line_out.extend(calc_circle(line[ii,:2],line[ii+1,:2],line[ii,4],arc_approx))
                        else:
                            line_out.append(line[ii,:2].tolist())
                    lines.append(line_out)
            elif layer is not None:
                if e.get_dxf_attrib('layer')==layer:
                    line = numpy.array(list(e.get_points()))
                    line_out = []
                    for ii in range(len(line)):
                        if line[ii,4]!=0:
                            line_out.extend(calc_circle(line[ii,:2],line[ii+1,:2],line[ii,4],arc_approx))
                        else:
                            line_out.append(line[ii,:2].tolist())
                    lines.append(line_out)
            else:
                line = numpy.array(list(e.get_points()))
                line_out = []
                for ii in range(len(line)):
                    if line[ii,4]!=0:
                        line_out.extend(calc_circle(line[ii,:2],line[ii+1,:2],line[ii,4],arc_approx))
                    else:
                        line_out.append(line[ii,:2].tolist())
                lines.append(line_out)

    return lines

            
def calc_circle(p1,p2,bulge,arc_approx=0):
    '''
    Approximates an arc betweem two points using a "bulge value".

    :param p1: the starting point.
    :type p1: tuple of floats
    :param p2: the ending point.
    :type p2: tuple of floats
    :param bulge: the bulge value. Positive bulge is right of the segment, negative is left.
    :type bulge: int
    :param arc_approx: number of interior points to approximate an arc with
    :type arc_approx: int
    :rtype: List of two-coordinate tuples.
    '''

    import math
    from foldable_robotics.layer import Layer
    
    
    v = p2 - p1
    
    l = ((v*v)**.5).sum()
    n =v/l
    R = numpy.array([[0,-1],[1,0]])
    n_p = R.dot(n)
    
    p3 = p1+v/2+n_p*-bulge*l/2
    
    x1_0 = p1[0]
    x1_1 = p1[1]
    x2_0 = p2[0]
    x2_1 = p2[1]
    x3_0 = p3[0]
    x3_1 = p3[1]
    p = numpy.array([ x1_0/2 + x3_0/2 + (x1_1 - x3_1)*((x1_0 - x2_0)*(x2_0 - x3_0) + (x1_1 - x2_1)*(x2_1 - x3_1))/(2*((x1_0 - x3_0)*(x2_1 - x3_1) - (x1_1 - x3_1)*(x2_0 - x3_0))),x1_1/2 + x3_1/2 + (-x1_0 + x3_0)*((x1_0 - x2_0)*(x2_0 - x3_0) + (x1_1 - x2_1)*(x2_1 - x3_1))/(2*((x1_0 - x3_0)*(x2_1 - x3_1) - (x1_1 - x3_1)*(x2_0 - x3_0)))])

    v = p-p1
    r = (v.dot(v))**.5
    
    v1=(p1-p)
    v2=(p2-p)
    t1 = math.atan2(v1[1],v1[0])
    t2 = math.atan2(v2[1],v2[0])
    
    if bulge<0:
        if t2>t1:
            t2 = t2 - math.pi
    
    t = numpy.r_[t1:t2:(arc_approx+2)*1j]
    points = r*numpy.c_[numpy.cos(t),numpy.sin(t)] +p
    
    return [p1]+points[1:-1].tolist()

def list_attrib(filename,attrib):
    '''
    list the attributes of all the items in the dxf.  use a string like 'color' or 'layer'

    :param filename: path to the dxf.
    :type filename: string
    :param attrib: attribute you wish to search.
    :type attrib: string
    '''
    
    dwg = ezdxf.readfile(filename)
    modelspace = dwg.modelspace()
    attrib_list =[]
    for item in modelspace:
        try:
            attrib_list.append(item.get_dxf_attrib(attrib))
        except AttributeError:
            attrib_list.append(None)
    return attrib_list

def get_types(filename,model_type):    
    '''
    return all of the dxf items of type "type"

    :param filename: path to the dxf.
    :type filename: string
    :param model_type: model type you are looking for.  ex: 'LWPOLYLINE'
    :type model_type: string
    '''
    
    dwg = ezdxf.readfile(filename)
    modelspace = dwg.modelspace()
    items = list(modelspace.query(model_type))
    return items


# -*- coding: utf-8 -*-
"""
Created on Mon Jan 29 14:39:05 2018

@author: daukes
"""

mapping = []
mapping.append((0,(0x000000)))
mapping.append((1,(0xFF0000)))
mapping.append((2,(0xFFFF00)))
mapping.append((3,(0x00FF00)))
mapping.append((4,(0x00FFFF)))
mapping.append((5,(0x0000FF)))
mapping.append((6,(0xFF00FF)))
mapping.append((7,(0xFFFFFF)))
mapping.append((8,(0x414141)))
mapping.append((9,(0x808080)))
mapping.append((10,(0xFF0000)))
mapping.append((11,(0xFFAAAA)))
mapping.append((12,(0xBD0000)))
mapping.append((13,(0xBD7E7E)))
mapping.append((14,(0x810000)))
mapping.append((15,(0x815656)))
mapping.append((16,(0x680000)))
mapping.append((17,(0x684545)))
mapping.append((18,(0x4F0000)))
mapping.append((19,(0x4F3535)))
mapping.append((20,(0xFF3F00)))
mapping.append((21,(0xFFBFAA)))
mapping.append((22,(0xBD2E00)))
mapping.append((23,(0xBD8D7E)))
mapping.append((24,(0x811F00)))
mapping.append((25,(0x816056)))
mapping.append((26,(0x681900)))
mapping.append((27,(0x684E45)))
mapping.append((28,(0x4F1300)))
mapping.append((29,(0x4F3B35)))
mapping.append((30,(0xFF7F00)))
mapping.append((31,(0xFFD4AA)))
mapping.append((32,(0xBD5E00)))
mapping.append((33,(0xBD9D7E)))
mapping.append((34,(0x814000)))
mapping.append((35,(0x816B56)))
mapping.append((36,(0x683400)))
mapping.append((37,(0x685645)))
mapping.append((38,(0x4F2700)))
mapping.append((39,(0x4F4235)))
mapping.append((40,(0xFFBF00)))
mapping.append((41,(0xFFEAAA)))
mapping.append((42,(0xBD8D00)))
mapping.append((43,(0xBDAD7E)))
mapping.append((44,(0x816000)))
mapping.append((45,(0x817656)))
mapping.append((46,(0x684E00)))
mapping.append((47,(0x685F45)))
mapping.append((48,(0x4F3B00)))
mapping.append((49,(0x4F4935)))
mapping.append((50,(0xFFFF00)))
mapping.append((51,(0xFFFFAA)))
mapping.append((52,(0xBDBD00)))
mapping.append((53,(0xBDBD7E)))
mapping.append((54,(0x818100)))
mapping.append((55,(0x818156)))
mapping.append((56,(0x686800)))
mapping.append((57,(0x686845)))
mapping.append((58,(0x4F4F00)))
mapping.append((59,(0x4F4F35)))
mapping.append((60,(0xBFFF00)))
mapping.append((61,(0xEAFFAA)))
mapping.append((62,(0x8DBD00)))
mapping.append((63,(0xADBD7E)))
mapping.append((64,(0x608100)))
mapping.append((65,(0x768156)))
mapping.append((66,(0x4E6800)))
mapping.append((67,(0x5F6845)))
mapping.append((68,(0x3B4F00)))
mapping.append((69,(0x494F35)))
mapping.append((70,(0x7FFF00)))
mapping.append((71,(0xD4FFAA)))
mapping.append((72,(0x5EBD00)))
mapping.append((73,(0x9DBD7E)))
mapping.append((74,(0x408100)))
mapping.append((75,(0x6B8156)))
mapping.append((76,(0x346800)))
mapping.append((77,(0x566845)))
mapping.append((78,(0x274F00)))
mapping.append((79,(0x424F35)))
mapping.append((80,(0x3FFF00)))
mapping.append((81,(0xBFFFAA)))
mapping.append((82,(0x2EBD00)))
mapping.append((83,(0x8DBD7E)))
mapping.append((84,(0x1F8100)))
mapping.append((85,(0x608156)))
mapping.append((86,(0x196800)))
mapping.append((87,(0x4E6845)))
mapping.append((88,(0x134F00)))
mapping.append((89,(0x3B4F35)))
mapping.append((90,(0x00FF00)))
mapping.append((91,(0xAAFFAA)))
mapping.append((92,(0x00BD00)))
mapping.append((93,(0x7EBD7E)))
mapping.append((94,(0x008100)))
mapping.append((95,(0x568156)))
mapping.append((96,(0x006800)))
mapping.append((97,(0x456845)))
mapping.append((98,(0x004F00)))
mapping.append((99,(0x354F35)))
mapping.append((100,(0x00FF3F)))
mapping.append((101,(0xAAFFBF)))
mapping.append((102,(0x00BD2E)))
mapping.append((103,(0x7EBD8D)))
mapping.append((104,(0x00811F)))
mapping.append((105,(0x568160)))
mapping.append((106,(0x006819)))
mapping.append((107,(0x45684E)))
mapping.append((108,(0x004F13)))
mapping.append((109,(0x354F3B)))
mapping.append((110,(0x00FF7F)))
mapping.append((111,(0xAAFFD4)))
mapping.append((112,(0x00BD5E)))
mapping.append((113,(0x7EBD9D)))
mapping.append((114,(0x008140)))
mapping.append((115,(0x56816B)))
mapping.append((116,(0x006834)))
mapping.append((117,(0x456856)))
mapping.append((118,(0x004F27)))
mapping.append((119,(0x354F42)))
mapping.append((120,(0x00FFBF)))
mapping.append((121,(0xAAFFEA)))
mapping.append((122,(0x00BD8D)))
mapping.append((123,(0x7EBDAD)))
mapping.append((124,(0x008160)))
mapping.append((125,(0x568176)))
mapping.append((126,(0x00684E)))
mapping.append((127,(0x45685F)))
mapping.append((128,(0x004F3B)))
mapping.append((129,(0x354F49)))
mapping.append((130,(0x00FFFF)))
mapping.append((131,(0xAAFFFF)))
mapping.append((132,(0x00BDBD)))
mapping.append((133,(0x7EBDBD)))
mapping.append((134,(0x008181)))
mapping.append((135,(0x568181)))
mapping.append((136,(0x006868)))
mapping.append((137,(0x456868)))
mapping.append((138,(0x004F4F)))
mapping.append((139,(0x354F4F)))
mapping.append((140,(0x00BFFF)))
mapping.append((141,(0xAAEAFF)))
mapping.append((142,(0x008DBD)))
mapping.append((143,(0x7EADBD)))
mapping.append((144,(0x006081)))
mapping.append((145,(0x567681)))
mapping.append((146,(0x004E68)))
mapping.append((147,(0x455F68)))
mapping.append((148,(0x003B4F)))
mapping.append((149,(0x35494F)))
mapping.append((150,(0x007FFF)))
mapping.append((151,(0xAAD4FF)))
mapping.append((152,(0x005EBD)))
mapping.append((153,(0x7E9DBD)))
mapping.append((154,(0x004081)))
mapping.append((155,(0x566B81)))
mapping.append((156,(0x003468)))
mapping.append((157,(0x455668)))
mapping.append((158,(0x00274F)))
mapping.append((159,(0x35424F)))
mapping.append((160,(0x003FFF)))
mapping.append((161,(0xAABFFF)))
mapping.append((162,(0x002EBD)))
mapping.append((163,(0x7E8DBD)))
mapping.append((164,(0x001F81)))
mapping.append((165,(0x566081)))
mapping.append((166,(0x001968)))
mapping.append((167,(0x454E68)))
mapping.append((168,(0x00134F)))
mapping.append((169,(0x353B4F)))
mapping.append((170,(0x0000FF)))
mapping.append((171,(0xAAAAFF)))
mapping.append((172,(0x0000BD)))
mapping.append((173,(0x7E7EBD)))
mapping.append((174,(0x000081)))
mapping.append((175,(0x565681)))
mapping.append((176,(0x000068)))
mapping.append((177,(0x454568)))
mapping.append((178,(0x00004F)))
mapping.append((179,(0x35354F)))
mapping.append((180,(0x3F00FF)))
mapping.append((181,(0xBFAAFF)))
mapping.append((182,(0x2E00BD)))
mapping.append((183,(0x8D7EBD)))
mapping.append((184,(0x1F0081)))
mapping.append((185,(0x605681)))
mapping.append((186,(0x190068)))
mapping.append((187,(0x4E4568)))
mapping.append((188,(0x13004F)))
mapping.append((189,(0x3B354F)))
mapping.append((190,(0x7F00FF)))
mapping.append((191,(0xD4AAFF)))
mapping.append((192,(0x5E00BD)))
mapping.append((193,(0x9D7EBD)))
mapping.append((194,(0x400081)))
mapping.append((195,(0x6B5681)))
mapping.append((196,(0x340068)))
mapping.append((197,(0x564568)))
mapping.append((198,(0x27004F)))
mapping.append((199,(0x42354F)))
mapping.append((200,(0xBF00FF)))
mapping.append((201,(0xEAAAFF)))
mapping.append((202,(0x8D00BD)))
mapping.append((203,(0xAD7EBD)))
mapping.append((204,(0x600081)))
mapping.append((205,(0x765681)))
mapping.append((206,(0x4E0068)))
mapping.append((207,(0x5F4568)))
mapping.append((208,(0x3B004F)))
mapping.append((209,(0x49354F)))
mapping.append((210,(0xFF00FF)))
mapping.append((211,(0xFFAAFF)))
mapping.append((212,(0xBD00BD)))
mapping.append((213,(0xBD7EBD)))
mapping.append((214,(0x810081)))
mapping.append((215,(0x815681)))
mapping.append((216,(0x680068)))
mapping.append((217,(0x684568)))
mapping.append((218,(0x4F004F)))
mapping.append((219,(0x4F354F)))
mapping.append((220,(0xFF00BF)))
mapping.append((221,(0xFFAAEA)))
mapping.append((222,(0xBD008D)))
mapping.append((223,(0xBD7EAD)))
mapping.append((224,(0x810060)))
mapping.append((225,(0x815676)))
mapping.append((226,(0x68004E)))
mapping.append((227,(0x68455F)))
mapping.append((228,(0x4F003B)))
mapping.append((229,(0x4F3549)))
mapping.append((230,(0xFF007F)))
mapping.append((231,(0xFFAAD4)))
mapping.append((232,(0xBD005E)))
mapping.append((233,(0xBD7E9D)))
mapping.append((234,(0x810040)))
mapping.append((235,(0x81566B)))
mapping.append((236,(0x680034)))
mapping.append((237,(0x684556)))
mapping.append((238,(0x4F0027)))
mapping.append((239,(0x4F3542)))
mapping.append((240,(0xFF003F)))
mapping.append((241,(0xFFAABF)))
mapping.append((242,(0xBD002E)))
mapping.append((243,(0xBD7E8D)))
mapping.append((244,(0x81001F)))
mapping.append((245,(0x815660)))
mapping.append((246,(0x680019)))
mapping.append((247,(0x68454E)))
mapping.append((248,(0x4F0013)))
mapping.append((249,(0x4F353B)))
mapping.append((250,(0x333333)))
mapping.append((251,(0x505050)))
mapping.append((252,(0x696969)))
mapping.append((253,(0x828282)))
mapping.append((254,(0xBEBEBE)))
mapping.append((255,(0xFFFFFF)))


from_index = dict([(ii,rgb) for ii,rgb in mapping])
to_index = dict([(rgb,ii) for ii,rgb in mapping])

if __name__=='__main__':
    #Here goes the file name of the dxf.
    filename ='C:/Users/daukes/code/foldable_robotics/python/foldable_robotics_tests/test2.DXF'
    dwg = ezdxf.readfile(filename)
    modelspace = dwg.modelspace()
    hinge_lines = read_lines(filename)
    exteriors = read_lwpolylines(filename,arc_approx=10)
    
    
    #turn lists into arrays
    hinge_lines = numpy.array(hinge_lines)
    
    for item in hinge_lines:
        plt.plot(item[:,0],item[:,1],'r--')
    
    for item in exteriors:
        item = numpy.array(item)
        plt.plot(item[:,0],item[:,1],'k-', linewidth = 3)
        
    plt.axis('equal')
#    print(list_attrib(filename,'closed'))
    items = get_types(filename,'LWPOLYLINE')
#    c  = approx_lwpoly(exteriors[0])
#    for item in c:
#        item.plot()
    