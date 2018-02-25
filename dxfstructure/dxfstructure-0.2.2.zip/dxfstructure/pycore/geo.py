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

import copy
from math import sqrt, sin, cos, atan, pi

checktolerance = 0.1

class Point():
    def __init__(self, xylist=[1.0, 2.0]):
        self.x = float(xylist[0])
        self.y = float(xylist[1])
        
    def distance(self, obj):
        return sqrt((self.x - obj.x)**2+(self.y - obj.y)**2)
        
    def intersection(self, obj):
        if self.distance(obj) <= checktolerance:
            return [obj]
        else:
            return []
    
    def get_coord_list(self):
        return [[self.x, self.y]]
    
    def move(self, vector=[1.0, 1.0]):
        self.x += vector[0]
        self.y += vector[1]
    
    def rotate(self, angle=pi/2.0):
        new_x = self.x*cos(angle) - self.y*sin(angle)
        new_y = self.x*sin(angle) + self.y*cos(angle)
        self.x = new_x
        self.y = new_y
         
    def __str__(self):
        return 'Point at ' + str(self.get_coord_list()[0])

class Line():
    def __init__(self, p1=Point([1.0, 1.0]), p2=Point([2.0, 3.0])):
        self.p1 = p1
        self.p2 = p2
        #---
        if self.p1.x == self.p2.x:
            self.A=1
            self.B=0
            self.C=-self.p1.x
        else:
            self.A = (self.p1.y - self.p2.y) / (self.p1.x - self.p2.x)
            self.B = -1.0
            self.C = self.p1.y - self.A * self.p1.x

    def move(self, vector=[1.0, 1.0]):
        self.p1.move(vector)
        self.p2.move(vector)

    def rotate(self, angle=pi/2.0):
        self.p1.rotate(angle)
        self.p2.rotate(angle)
    
    def draw(self, scene, color='black', dim = True):
        p1 = self.p1.get_coord_list()[0]
        p2 = self.p2.get_coord_list()[0]  
        scene.addLine(p1, p2, color=color)
        if dim:
            midpoint = self.midpoint
            dimtext = str(int(self.length))
            scene.addText(dimtext, midpoint.get_coord_list()[0], height=180, color='yellow')
            
    def distance(self, obj):
        A = self.A
        B = self.B
        C = self.C
        #---
        dl = abs(A*obj.x + B*obj.y + C)/sqrt((A)**2+(B)**2)
        dp1 = self.p1.distance(obj)
        dp2 = self.p2.distance(obj)
        dist_p1_p2 = self.p1.distance(self.p2)
        dist_o_p1 = self.p1.distance(obj)
        dist_o_p2 = self.p2.distance(obj)
        if (dist_p1_p2**2 + dist_o_p1**2 < dist_o_p2**2) or (dist_p1_p2**2 + dist_o_p2**2 < dist_o_p1**2):
            dist = min (dp1, dp2)
        else:
            dist = dl
        return dist

    @property
    def midpoint(self):
        xmid = (self.p1.x + self.p2.x) / 2.0
        ymid = (self.p1.y + self.p2.y) / 2.0
        return Point([xmid, ymid])
          
    @property
    def angle(self):
        try:
            tangens = (self.p2.y - self.p1.y)/(self.p2.x - self.p1.x)
        except ZeroDivisionError:
              tangens = float('inf')
        return atan(tangens)

    def intersection(self, obj):
        xmin = min(self.p1.x, self.p2.x)
        xmax = max(self.p1.x, self.p2.x)
        ymin = min(self.p1.y, self.p2.y)
        ymax = max(self.p1.y, self.p2.y)
        if isinstance(obj, Point):
            if self.distance(obj) < checktolerance and (xmin<=obj.x<=xmax) and (ymin<=obj.y<=ymax):
                return [obj]
            else:
                return []
        if isinstance(obj, Line):
            W = self.A * obj.B - obj.A * self.B
            if W == 0:
                return []
            else:
                Wx = -self.C * obj.B + obj.C * self.B
                Wy = - self.A * obj.C + obj.A * self.C
                x = Wx / W
                y = Wy / W
                p = Point([x,y])
                if self.intersection(p) and obj.intersection(p):
                    return [p]
                else:
                    return []
    
    @property
    def length(self, round=5.0):
        length = dim_round(self.p1.distance(self.p2), round)
        return length
        
    def get_coord_list(self):
        return self.p1.get_coord_list() + self.p2.get_coord_list()
    
    def __str__(self):
        return 'Line from %s to %s' %(self.p1.get_coord_list()[0], self.p2.get_coord_list()[0])

class Polyline():
    def __init__(self):
        self.segments = []

    def move(self, vector=[1.0, 1.0]):
        for segment in self.segments:
            segment.move(vector)

    def rotate(self, angle=pi/2.0):
        for segment in self.segments:
            segment.rotate(angle)

    def draw(self, scene, color='black'):
        for segment in self.segments:
            segment.draw(scene, color= color)
    
    def add_segment(self, obj):
        self.segments.append(obj)
    
    @property
    def seg_angles(self):
        return [segment.angle for segment in self.segments]

    @property
    def seg_lengths(self):
        return [segment.length for segment in self.segments]

    @property
    def midpoint(self):
        pcoords = self.get_coord_list()
        pnumber = len(pcoords)
        xsum = sum([p[0] for p in pcoords])
        ysum = sum([p[1] for p in pcoords])
        xmid = xsum / pnumber
        ymid = ysum / pnumber
        return Point([xmid, ymid])
    
    def distance(self, obj):
        return min([i.distance(obj) for i in self.segments])

    def intersection(self, obj):
        points = []
        if isinstance(obj, Line) or isinstance(obj, Point):
            for i in self.segments:
                icheck = i.intersection(obj)
                if icheck:
                    points.append(icheck[0])
            return points
        if isinstance(obj, Polyline):
            for i in self.segments:
                for j in obj.segments:
                    ijcheck = i.intersection(j)
                    if ijcheck:
                        points.append(ijcheck[0])
            return points

    def get_coord_list(self):
        coord_list = [p.get_coord_list()[0] for p in self.segments] + [p.get_coord_list()[1] for p in self.segments]
        for i in range(len(coord_list) -1):
            if coord_list[i] == coord_list[i+1]:
                coord_list[i+1] = None
        while None in coord_list:
            coord_list.remove(None)
        return coord_list
    
    @property
    def length(self):
        return sum([seg.length for seg in self.segments])
        
    def __str__(self):
        return 'Polyline with ' + str(len(self.segments)) + ' segments - ' + str([str(i) for i in self.segments])

class Rectangle():
    def __init__(self, p1=Point([1.0, 1.0]), p2=Point([2.0, 3.0])):
        self.p1 = p1
        self.p2 = p2
        self.xmin = min(self.p1.x, self.p2.x)
        self.xmax = max(self.p1.x, self.p2.x)
        self.ymin = min(self.p1.y, self.p2.y)
        self.ymax = max(self.p1.y, self.p2.y)

    def has_inside(self, obj):
        coords = []
        if isinstance(obj, Point):
            coords += obj.get_coord_list()
        if isinstance(obj, Line):
            coords += obj.get_coord_list()
        if isinstance(obj, Polyline):
            coords += obj.get_coord_list()
        if isinstance(obj, Rectangle):
            coords += obj.get_coord_list()
        for p in coords:
            if not self.xmin <= p[0] <= self.xmax:
                return False
            if not self.ymin <= p[1] <= self.ymax:
                return False
        return True
            
    def get_coord_list(self):
        return self.p1.get_coord_list() + self.p2.get_coord_list()

    def __str__(self):
        return 'Rectangle with corners at %s and %s' %(self.p1.get_coord_list()[0], self.p2.get_coord_list()[0])

class Bar_shape():
    def __init__(self, pline):
        self.pline = copy.deepcopy(pline)
        self.reduce_pline()
    
    def reduce_pline(self):
        #-- rotating to longest seg
        seg_legs = self.pline.seg_lengths
        longest = max(seg_legs)
        longest_index = seg_legs.index(longest)
        self.pline.rotate(-self.pline.seg_angles[longest_index])
        #---
        min_x = min([p[0] for p in self.pline.get_coord_list()])
        max_y = max([p[1] for p in self.pline.get_coord_list()])
        move_vector = [-min_x, -max_y]
        self.pline.move(move_vector)

    def draw(self, scene, color='black'):
        self.pline.draw(scene, color=color)
    
    @property
    def sizexy(self):
        sizex = abs(max([p[0] for p in self.pline.get_coord_list()]))
        sizey = abs(min([p[1] for p in self.pline.get_coord_list()]))
        return [sizex, sizey] 

    @property
    def shape_parameter(self):
        dim_round()
        midpoint = self.pline.midpoint
        parameter = [midpoint.distance(Point(xy)) for xy in self.pline.get_coord_list()]
        return parameter

    def __str__(self):
        return 'Bar_shape with ' + str(self.pline)
        
def pline_from_dxfpline(dxfpline):
    pline = Polyline()
    plinepoints = list(dxfpline.get_rstrip_points())
    pointsnumber = len(plinepoints)
    for i in range(pointsnumber-1):
        iseg = Line(Point(plinepoints[i]), Point(plinepoints[i+1]))
        pline.add_segment(iseg)
    return pline

def dim_round(dim = 50.0, tolerance = 5.0):
    dim = float(dim)
    return round(round(dim/tolerance) * tolerance)

# Test if main        
if __name__ == "__main__":
    print '-------------Point testing------------'
    p = Point([1.0, 1.0])
    p1 = Point([1.0, 1.0])
    print p.distance(p1), 'p.distance'
    print 'distance from %s to %s is %s' %(p, p1, p.distance(p1))
    print 'distance from %s to %s is %s' %(p1, p, p1.distance(p))
    print 'intersection for %s and %s is %s - %s' %(p, p1, p.intersection(p1), [str(i) for i in p.intersection(p1)])
    
    print '-------------Line testing------------'
    l1 = Line(Point([0,0]), Point([1,6]))
    print 'Linia l1 %s %s*x + %s*y + %s = 0 ' %(l1, l1.A, l1.B, l1.C)
    l2 = Line(Point([0,5]), Point([3,1]))
    print 'Linia l2 %s %s*x + %s*y + %s = 0 ' %(l2, l2.A, l2.B, l2.C)
    p = Point([1,2])
    print 'distance %s to %s is %s' %(p, l1, l1.distance(p))
    print '%s intersect %s at %s - %s' %(p, l1, l1.intersection(p), [str(i) for i in l1.intersection(p)])
    print 'distance %s to %s is %s' %(p, l2, l2.distance(p))
    print '%s intersect %s at %s - %s' %(p, l2, l2.intersection(p), [str(i) for i in l2.intersection(p)])
    print '%s intesect %s at %s - %s' %(l1, l2, l1.intersection(l2), [str(i) for i in l1.intersection(l2)])
    print '%s intesect %s at %s - %s' %(l2, l1, l2.intersection(l1), [str(i) for i in l2.intersection(l1)])
    
    print '-------------Polyline testing------------'
    p = Point([1,2])
    pline1 = Polyline()
    pline1.add_segment(Line(Point([-3,1]), Point([6,7])))
    pline1.add_segment(Line(Point([6,7]), Point([2,9])))
    print pline1
    
    pline2 = Polyline()
    pline2.add_segment(Line(Point([3,11]), Point([3,3])))
    pline2.add_segment(Line(Point([3,3]), Point([6,3])))
    print pline2
    
    print 'distance %s to %s is %s' %(p, pline1, pline1.distance(p))
    print 'distance %s to %s is %s' %(p, pline2, pline2.distance(p))
    
    print '%s intersect %s at %s - %s' %(pline1, pline2, pline1.intersection(pline2), [str(i) for i in pline1.intersection(pline2)])
    print '%s intersect %s at %s - %s' %(pline1, l1, pline1.intersection(l1), [str(i) for i in pline1.intersection(l1)])
    print '%s intersect %s at %s - %s' %(pline1, p, pline1.intersection(p), [str(i) for i in pline1.intersection(p)])
    
    print '-------------Rextangle testing------------'
    rect = Rectangle(Point([-4,1]), Point([8, 10]))
    print rect
    print rect.xmin, rect.xmax, rect.ymin, rect.ymax , 'dasdads'
    
    print '%s has inside %s - %s' %(rect, p, rect.has_inside(p))
    print '%s has inside %s - %s' %(rect, l1, rect.has_inside(l1))
    print '%s has inside %s - %s' %(rect, l2, rect.has_inside(l2))
    print '%s has inside %s - %s' %(rect, pline1, rect.has_inside(pline1))
    print '%s has inside %s - %s' %(rect, pline2, rect.has_inside(pline2))
    
    print '-------------------------'
    
    for i in [p, l1, pline1, rect]:
        print i.get_coord_list()
    
    bar_shape = Bar_shape(pline1)