# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>asu.edu.
Please see LICENSE for full license.
"""
#import shapely.geometry as sg
#from .shape import Base
#from . import shape
import shapely.geometry
import shapely.geometry as sg
import shapely.affinity as sa
from .class_algebra import ClassAlgebra
import shapely.ops as so
import shapely.wkt as sw
import matplotlib.pyplot as plt
import numpy
import foldable_robotics
from foldable_robotics.jupyter_support import JupyterSupport

def get_segments(poly):
    '''
    get the line segments of a polygon or linestring
    
    :param poly: the geometry
    :type poly: shapely.geometry.Polygon or shapely.geometry.LineString
    :rtype: list of two-coordinate segments
    '''         
    if isinstance(poly,sg.Polygon):
        exterior = list(poly.exterior.coords)
        interiors = [list(interior.coords) for interior in poly.interiors]
        segments = [exterior]+interiors
        segments = [loop+loop[0:1] for loop in segments]
        
    elif isinstance(poly,sg.LineString):
        segments = list(poly.coords)
        
    return segments

def is_collection(item):
    '''
    determines whether the geometry defined by item contains multiple geometries
    
    :param item: the shapely geometry
    :type item: class from shapely.geometry
    :rtype: boolean
    '''    
    collections = [
        shapely.geometry.MultiPolygon,
        shapely.geometry.GeometryCollection,
        shapely.geometry.MultiLineString,
        shapely.geometry.MultiPoint]
    iscollection = [isinstance(item, cls) for cls in collections]
    return any(iscollection)

def extract_r(item,list_in = None):
    '''
    recursively extracts geometries from collections of geometries
    
    :param item: the shapely geometry
    :type item: class from shapely.geometry
    :param list_in: a list to add to
    :type list_in: list
    :rtype: boolean
    '''    
    
    list_in = list_in or []
    if is_collection(item):
        list_in.extend([item3 for item2 in item.geoms for item3 in extract_r(item2,list_in)])
    else:
        list_in.append(item)
    return list_in
    
def flatten(geoms):
    '''
    eliminate any collections of geometries by flattening all into a single list.
    
    :param geoms: the shapely geometries
    :type geoms: list or iterable
    :rtype: list
    '''  
    geom = so.unary_union(geoms)
    entities = extract_r(geom)
#    entities = [item for item in entities if any([isinstance(item,classitem) for classitem in [shapely.geometry.Polygon,shapely.geometry.LineString,shapely.geometry.Point]])]
#    entities = [item for item in entities if not item.is_empty]
    return entities   
    
def from_shapely_to_layer(new_geoms):
    '''
    convert from shapely geometry to Layer class
    
    :param new_geoms: the shapely geometries
    :type new_geoms: list or iterable
    :rtype: Layer
    '''  
    new_geoms = flatten(new_geoms)        
    new_layer = Layer(*new_geoms)
    return new_layer
    
def from_layer_to_shapely(layer):
    '''
    convert from Layer class to shapely geometry
    
    :param layer: the layer instance
    :type layer: Layer
    :rtype: class from shapely.geometry
    '''  
    geoms = so.unary_union(layer.geoms)
    return geoms

def plot_poly(poly,color = None,edgecolor = None, facecolor =None, linewidth = .25):
    '''
    plot a shapely geometry
    
    :param poly: the layer instance
    :type poly: class from shapely.geometry
    :param edgecolor: tuple of r,g,b,a scalars from 0 to 1
    :type edgecolor: tuple
    :param facecolor: tuple of r,g,b,a scalars from 0 to 1
    :type facecolor: tuple
    :param linewidth: width of the line
    :type linewidth: scalar or None for default
    '''  

    color = color or (1,0,0,.25)
    
    facecolor = facecolor or color
    edgecolor = edgecolor or (0,0,0,.5)
    
    import numpy
    from matplotlib.patches import PathPatch
    from matplotlib.path import Path
    import matplotlib.pyplot as plt
    axes = plt.gca()
    vertices = []
    codes = []
    color = list(color)
    if isinstance(poly,sg.Polygon):
        exterior = list(poly.exterior.coords)
        interiors = [list(interior.coords) for interior in poly.interiors]
        for item in [exterior]+interiors:
            vertices.extend(item+[(0,0)])
            codes.extend([Path.MOVETO]+([Path.LINETO]*(len(item)-1))+[Path.CLOSEPOLY])
        path = Path(vertices,codes)
        patch = PathPatch(path,facecolor=facecolor,edgecolor=edgecolor, linewidth= linewidth)        
        axes.add_patch(patch)

    elif isinstance(poly,sg.LineString):
        exterior = numpy.array(poly.coords)
        axes.plot(exterior[:,0],exterior[:,1],color=color[:3]+[.5])
    plt.axis('equal')
    
def check_loop(loop):
    '''
    remove the last element of loop if it is the same as the first
    
    :param loop: list of coordinates
    :type loop: iterable of tuples
    :rtype: iterable of tuples
    '''      
    if loop[-1]==loop[0]:
        return loop[:-1]
        
def triangulate_geom(geom):
    '''
    triangulate a shapely geometry
    
    :param geom: the geometry to triangulate
    :type geom: shapely.Polygon
    :rtype: array of points, array of triangle indeces
    '''      
    import pypoly2tri
    from pypoly2tri.cdt import CDT
    import numpy
    exterior = list(geom.exterior.coords)
    exterior = check_loop(exterior)
    exterior2 = [pypoly2tri.shapes.Point(*item) for item in exterior]
    cdt = CDT(exterior2)
    interiors = []
    for interior in geom.interiors:
        interior= list(interior.coords)
        interior = check_loop(interior)
        interiors.append(interior)
    for interior in interiors:
        interior2 = [pypoly2tri.shapes.Point(*item) for item in interior]
        cdt.AddHole(interior2)
    cdt.Triangulate()
    tris =cdt.GetTriangles()
    points = cdt.GetPoints()
    points2 = numpy.array([item.toTuple() for item in points])
    tris2 = numpy.array([[points.index(point) for point in tri.points_] for tri in tris],dtype = int)
    return points2,tris2

def points_2d_to_3d(points_2d,z_val):
    '''
    convert a list of 2d points to a list of 3d points
    
    :param points_2d: the geometry to triangulate
    :type points_2d: numpy.array
    :param z_val: the padded z value
    :type z_val: float
    :rtype: numpy.array
    '''      

    z = points_2d[:,0:1]*0+z_val
    points3 = numpy.c_[points_2d,z]
    return points3

def extrude(points,tris,z_lower,z_upper):
    '''
    create 3d tetrahedra from 2d triangles
    
    :param points: array of 3d points
    :type points: numpy.array
    :param tris: the triangle coordinates
    :type tris: numpy.array
    :param z_lower: the lower z value
    :type z_lower: float
    :param z_upper: the upper z value
    :type z_upper: float
    :rtype: list of Tetrahedron
    '''       
    
    from idealab_tools.geometry.triangle import Triangle
    tris3 = [Triangle(*(points[tri])) for tri in tris]
    tets = [tet for tri in tris3 for tet in tri.extrude(z_lower,z_upper)]
    return tets
    
def inertia_tensor(about_point,density,z_lower,z_upper,points,tris):
    '''
    create 3d inertia tensor from a 2d list of triangles
    
    :param about_point: the point about which to compute the inertia
    :type about_point: 3d coordinate
    :param density: the density of the material
    :type density: float
    :param z_lower: the lower z value
    :type z_lower: float
    :param z_upper: the upper z value
    :type z_upper: float
    :param points: array of 3d points
    :type points: numpy.array
    :param tris: the triangle coordinates
    :type tris: numpy.array
    :rtype: list of Tetrahedron
    '''       
    import numpy
    tets = extrude(points,tris,z_lower,z_upper)
    Is = numpy.array([tet.I(density,about_point) for tet in tets])
    I = Is.sum(0)
    return I

class Layer(ClassAlgebra):
    '''
    The Layer class is essentially a list of 2d polygons which all exist on the same plane.
    '''
    def __init__(self, *geoms):
        '''
        create a new class instance
        
        :param geoms: a list of shapely geometries contained by the layer
        :type geoms: list of shapely.geometry classes
        :rtype: Layer
        '''   
        geoms = flatten(geoms)
        self.geoms = geoms
        self.id = id(self)

    @classmethod
    def new(cls,*geoms):
        '''
        create a new class instance
        
        :param geoms: a list of shapely geometries contained by the layer
        :type geoms: list of shapely.geometry classes
        :rtype: Layer
        '''   
        
        geoms = flatten(geoms)
        new = cls(*geoms)
        return new

    def copy(self,identical = True):
        '''
        creates a copy of the instance
        
        :param identical: whether to use the same id or not.
        :type identical: boolean
        :rtype: Layer
        '''            
        new = type(self)(*[sw.loads(geom.to_wkt()) for geom in self.geoms])        
        if identical:        
            new.id = self.id
        return new

    def export_dict(self):
        '''
        converts the layer to a dict.
        
        :rtype: dict
        '''
        d = {}
        d['geoms'] = [item.to_wkt() for item in self.geoms]
        d['id'] = self.id
        return d

    @classmethod
    def import_dict(cls,d):
        '''
        converts a dict to a Layer instance
        
        :param d: the laminate in dict form
        :type d: dict
        :rtype: Laminate
        '''        
        
        new = cls(*[sw.loads(item) for item in d['geoms']])
        new.id = d['id']
        return new

    def plot(self,*args,**kwargs):
        '''
        plots the layer using matplotlib.
        
        :param new: whether to create a new figure
        :type new: boolean
        '''   
        
        if 'new' in kwargs:
            new = kwargs.pop('new')
        else:
            new = False
        if new:
            plt.figure()
        for geom in self.geoms:
            plot_poly(geom,*args,**kwargs)

    def binary_operation(self,other,function_name,*args,**kwargs):
        '''
        performs a binary operation between self and other.
        
        :param function_name: the layer-based function to be performed
        :type function_name: string
        :param other: the layer-based function to be performed
        :type other: Layer
        :param args: tuple of arguments passed to subfunction
        :type args: tuple
        :param kwargs: keyword arguments passed to subfunction
        :type kwargs: dict
        :rtype: Layer
        '''
        
        a = from_layer_to_shapely(self)
        b = from_layer_to_shapely(other)
        function = getattr(a,function_name)
        c = function(b,*args,**kwargs)
        return from_shapely_to_layer(c)

    def union(self,other):
        '''
        returns the union between self and other.
        
        :param other: the other layer
        :type other: Layer
        :rtype: Layer
        '''
        return self.binary_operation(other,'union')

    def difference(self,other):
        '''
        returns the difference between self and other.
        
        :param other: the other layer
        :type other: Layer
        :rtype: Layer
        '''
        return self.binary_operation(other,'difference')

    def symmetric_difference(self,other):
        '''
        returns the symmetric difference between self and other.
        
        :param other: the other layer
        :type other: Layer
        :rtype: Layer
        '''
        return self.binary_operation(other,'symmetric_difference')

    def intersection(self,other):
        '''
        returns the intersection between self and other.
        
        :param other: the other layer
        :type other: Layer
        :rtype: Layer
        '''
        return self.binary_operation(other,'intersection')
    
    def buffer(self,value,resolution = None):
        '''
        dilate (or erode) the geometries in the layer
        
        :param value: the positive (or negative) radius of the dilation (or erosion)
        :type value: float
        :param resolution: the number of interpolanting vertices to use
        :type resolution: int
        :rtype: Layer
        '''
        resolution = resolution or foldable_robotics.resolution
        return self.dilate(value,resolution)

    def dilate(self,value,resolution = None):
        '''
        dilate the geometries in the layer
        
        :param value: the radius of the dilation
        :type value: float
        :param resolution: the number of interpolanting vertices to use
        :type resolution: int
        :rtype: Layer
        '''
        resolution = resolution or foldable_robotics.resolution
        geoms = from_layer_to_shapely(self)
        new_geoms = (geoms.buffer(value,resolution))
        return from_shapely_to_layer(new_geoms)

    def erode(self,value,resolution = None):
        '''
        erode the geometries in the layer
        
        :param value: the radius of the erotion
        :type value: float
        :param resolution: the number of interpolanting vertices to use
        :type resolution: int
        :rtype: Layer
        '''        
        resolution = resolution or foldable_robotics.resolution
        return self.dilate(-value,resolution)
        
    def translate(self,xoff=0.0, yoff=0.0, zoff=0.0):
        '''
        translate the layer
        
        :param xoff: the amount of x translation
        :type xoff: float
        :param yoff: the amount of y translation
        :type yoff: float
        :param zoff: the amount of z translation
        :type zoff: float
        :rtype: Layer
        '''          
        geoms = from_layer_to_shapely(self)
        new_geoms = sa.translate(geoms,xoff,yoff,zoff)
        return from_shapely_to_layer(new_geoms)

    def scale(self, xfact=1.0, yfact=1.0, zfact=1.0, origin=(0,0)):
        '''
        scale the layer
        
        :param xfact: the amount of x scaling
        :type xfact: float
        :param yfact: the amount of y scaling
        :type yfact: float
        :param zfact: the amount of z scaling
        :type zfact: float
        :rtype: Layer
        '''           
        geoms = from_layer_to_shapely(self)
        new_geoms = sa.scale(geoms,xfact,yfact,zfact,origin)
        return from_shapely_to_layer(new_geoms)

    def rotate(self, angle, origin=(0,0), use_radians=False):
        '''
        rotate the layer
        
        :param angle: the amount of rotation
        :type angle: float
        :param origin: the origin to use in calculating the rotation
        :type origin: string or tuple
        :param use_radians: whether to use radians or degrees
        :type use_radians: boolean
        :rtype: Layer
        '''          
        geoms = from_layer_to_shapely(self)
        new_geoms = sa.rotate(geoms,angle,origin,use_radians)
        return from_shapely_to_layer(new_geoms)

    def affine_transform(self,*args,**kwargs):
        geoms = from_layer_to_shapely(self)
        new_geoms = sa.affine_transform(geoms,*args,**kwargs)
        return from_shapely_to_layer(new_geoms)

    def simplify(self,tolerance):
        '''
        simplify the layer by reducing the number of coordinates. uses shapely's simplify function.
        
        :param tolerance: the length scale by which to simplify
        :type tolerance: float
        :rtype: Layer
        '''      
        geoms = foldable_robotics.layer.from_layer_to_shapely(self)
        new_geoms = (geoms.simplify(tolerance))
        return foldable_robotics.layer.from_shapely_to_layer(new_geoms)


    def export_dxf(self,name):
        '''
        export the layer to a dxf
        
        :param name: the filename to write
        :type name: string
        '''  
        
        import ezdxf
        dwg = ezdxf.new('R2010')
        msp = dwg.modelspace()
        for geom in self.geoms:
            segments = get_segments(geom)
            for segment in segments:
                for c0,c1 in zip(segment[:-1],segment[1:]):
                    msp.add_line(c0,c1)
        dwg.saveas(name+'.dxf')
        
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
        :rtype: Layer 
        '''           
        import foldable_robotics.manufacturing
        return foldable_robotics.manufacturing.map_line_stretch(self,p1,p2,p3,p4)
    
    def triangulation(self):
        '''
        triangulate a layer
        
        :rtype: array of points, array of triangle indeces
        '''      
         
        points = []
        tris = []
        ii = 0
        for geom in self.geoms:
            if isinstance(geom,sg.Polygon):
                points2,tris2 = triangulate_geom(geom)
                points.append(points2)
                tris.append(tris2+ii)
                ii+=len(points2)
        points = numpy.vstack(points)
        tris = numpy.vstack(tris)
        return points,tris
    
    def mesh_items_inner(self,z_offset = 0,color = (1,0,0,1)):
        '''inner loop for meshing the layer'''
        verts_outer = []
        colors_outer = []
        
        for geom in self.geoms:
            if isinstance(geom,sg.Polygon):
                
                points2,tris2 = triangulate_geom(geom)
                points3 = points_2d_to_3d(points2,z_offset)
                verts =points3[tris2]
                verts_colors = [[color]*3]*len(tris2)
                verts_outer.append(verts)
                colors_outer.append(verts_colors)
        
        verts_outer = numpy.vstack(verts_outer)
        colors_outer = numpy.vstack(colors_outer)
        return verts_outer,colors_outer
    
    def mesh_items(self,z_offset = 0,color = (1,0,0,1)):
        '''Return a pyqtgraph.opengl.GLMeshItem for the layer'''
        import pyqtgraph.opengl as gl
        verts_outer,colors_outer = self.mesh_items_inner(z_offset,color)
        mi=gl.GLMeshItem(vertexes=verts_outer,vertexColors=colors_outer,smooth=False,shader='balloon',drawEdges=False)
        return mi
    
    def mass_props(self,material_property,bottom,top):
        '''compute the mass properties of the layer'''
        area_i = 0
        mass_i=0
        volume_i=0
        
        centroid_x_i=0
        centroid_y_i=0
        centroid_z_i=0

        for geom in self.geoms:
            area_i = geom.area
            volume_ii = geom.area*material_property.thickness
            mass_ii  = volume_ii*material_property.density

            volume_i+=volume_ii
            mass_i+=mass_ii
            centroid = list(geom.centroid.coords)[0]
            centroid_x_i += centroid[0]*mass_ii
            centroid_y_i += centroid[1]*mass_ii
            centroid_z_i += (bottom+top)/2*mass_ii

        centroid_i = centroid_x_i/mass_i,centroid_y_i/mass_i,centroid_z_i/mass_i
        
        return area_i,volume_i,mass_i,centroid_i 
    
    def inertia(self,about_point,z_lower,material_property):
        '''compute the inertia tensor for the layer'''
        I=numpy.zeros((3,3))
        z_upper = z_lower+material_property.thickness

        for geom in self.geoms:
            points,tris = triangulate_geom(geom)
            I+=inertia_tensor(about_point,material_property.density,z_lower,z_upper,points,tris)
            
        return I
    
    def bounding_box_coords(self):
        '''compute the lower left hand and upper right coordinates for computing a bounding box of the layer'''
        a = numpy.array([vertex for geom in self.geoms for vertex in geom.exterior.coords])
        box = [tuple(a.min(0)),tuple(a.max(0))]
        return box

    def bounding_box(self):
        '''create a bounding box of the layer and return as a layer'''
        a,b = self.bounding_box_coords()
        p = sg.box(*a,*b)
        l = Layer(p)
        return l
        
    def exteriors(self):
        '''return the exterior coordinates of all shapes in the layer'''
        a = [list(geom.exterior.coords) for geom in self.geoms]
        return a

    def interiors(self):
        '''return the interior coordinates of all shapes in the layer'''
        a = [list(interior.coords) for geom in self.geoms for interior in geom.interiors]
        return a

    def extrude(self,z_lower,material_property):
        '''create tetrahedra from the layer and return as a set of points and tetrahedra indeces'''
        z_upper = z_lower+material_property.thickness
        points, tris =self.triangulation()
        m = points.shape[0]
        n = tris.shape[0]
        points2 = numpy.r_[numpy.c_[points,[z_lower]*len(points)],numpy.c_[points,[z_upper]*len(points)]]
        tris2 = numpy.r_[numpy.c_[tris[:,(0)]+m,tris[:,(1,0,2)]+m],numpy.c_[tris[:,(0,)]+m,tris[:,(1,)],tris[:,(2,)]+m,tris[:,(2,)]],numpy.c_[tris[:,(0,)]+m,tris[:,(1,)],tris[:,(1,2)]+m]]
        return points2,tris2
    def _repr_svg_(self):
        j = JupyterSupport(self.exteriors()+self.interiors())
        return j._repr_svg_()
    def to_laminate(self,value):
        from foldable_robotics.laminate import Laminate
        laminate = Laminate(*([self]*value))
        return laminate

    
        
def layer_representer(dumper, v):
    '''function for representing layer as a dictionary for use by yaml'''
    d = v.export_dict()
    output = dumper.represent_mapping(u'!Layer',d)
    return output

def layer_constructor(loader, node):
    '''function for constructing layer from a dictionary for use by yaml'''
    item = loader.construct_mapping(node)
    new = Layer.import_dict(item)
    return new
    
import yaml        
yaml.add_representer(Layer, layer_representer)
yaml.add_constructor(u'!Layer', layer_constructor)
        