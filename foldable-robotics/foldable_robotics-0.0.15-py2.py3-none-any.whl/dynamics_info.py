# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>asu.edu.
Please see LICENSE for full license.
"""

class MaterialProperty(object):
    '''
    The MaterialProperty class holds all the information about each layer's material information.  The geometry and material prop information can be passed seaprately, permitting more complex representations.
    '''
    def __init__(self,name,color,thickness,E1,E2,density,poisson,is_adhesive,is_rigid,is_conductive,is_flexible):
        '''
        Initializes the class
        
        :param name: The name of the material
        :type name: string
        :param color: The color of the material, in a tuple of four floats
        :type color: tuple of four floats
        :param thickness: the thickness of the layer
        :type thickness: float
        :param E1: Young's modulus along the primary direction
        :type E1: float
        :param E2: Young's modulus along the secondary direction
        :type E2: float
        :param density: density of the material
        :type density: float
        :param poisson: poisson's ratio of the material
        :type poisson: float
        :param is_adhesive: indicates whether the material is an adhesive
        :type is_adhesive: bool
        :param is_rigid:  indicates whether the material is rigid
        :type is_rigid: bool
        :param is_conductive:  indicates whether the material is conductive
        :type is_conductive: bool
        :param is_flexible:  indicates whether the material is flexible
        :type is_flexible: bool
        :rtype: MaterialProperty
        '''
        self.name = name
        self.color = color
        self.thickness = thickness
        self.E1 = E1
        self.E2 = E2
        self.density = density
        self.poisson = poisson
        self.is_adhesive = is_adhesive
        self.is_rigid = is_rigid
        self.is_conductive = is_conductive
        self.is_flexible = is_flexible
    def copy(self):
        '''
        Copies the class

        :rtype: MaterialProperty
        '''        
        return MaterialProperty(self.name,self.color,self.thickness,self.E1,self.E2,self.density,self.poisson,self.is_adhesive,self.is_rigid,self.is_conductive,self.is_flexible)

    @classmethod
    def make_n_blank(cls,n,thickness = 1,E1 = 1,E2 = 1,density = 1, poisson = 1,is_adhesive = False, is_rigid = False, is_conductive = False, is_flexible = False ):
        '''
        Creates several instances with slightly different colors for differentiation
        
        :param n: number of instances
        :type n: int
        :param thickness: the thickness of the layer
        :type thickness: float
        :param E1: Young's modulus along the primary direction
        :type E1: float
        :param E2: Young's modulus along the secondary direction
        :type E2: float
        :param density: density of the material
        :type density: float
        :param poisson: poisson's ratio of the material
        :type poisson: float
        :param is_adhesive: indicates whether the material is an adhesive
        :type is_adhesive: bool
        :param is_rigid:  indicates whether the material is rigid
        :type is_rigid: bool
        :param is_conductive:  indicates whether the material is conductive
        :type is_conductive: bool
        :param is_flexible:  indicates whether the material is flexible
        :type is_flexible: bool
        :rtype: MaterialProperty
        '''
        import numpy
        import matplotlib.cm
        cm = matplotlib.cm.plasma
        colors = numpy.array([cm(ii/(n-1)) for ii in range(n)])
        colors[:,3] = .25
        colors = [tuple(item) for item in colors]   
        materials = []
        for ii,color in enumerate(colors):
            materials.append(cls('layer'+str(ii),color,thickness,E1,E2,density,poisson,is_adhesive,is_rigid,is_conductive,is_flexible))
        return materials
    
class JointProps(object):
    '''
    The JointProps class holds all the information about each joint's dynamic properties.
    '''
    def __init__(self,stiffness,damping,preload,limit_neg,limit_pos,z_pos):
        '''
        Creates several instances with slightly different colors for differentiation
        
        :param stiffness: stiffness of the joint
        :type stiffness: float
        :param damping: the damping coefficient of the joint
        :type damping: float
        :param preload: moment of preload
        :type preload: float
        :param limit_neg: the negative joint limit in radians
        :type limit_neg: float
        :param limit_pos: the positive joint limit in radians
        :type limit_pos: float
        :param z_pos: the height of the joint
        :type z_pos: float
        :rtype: JointProps
        '''
        self.stiffness = stiffness
        self.damping = damping
        self.preload = preload
        self.limit_neg = limit_neg
        self.limit_pos = limit_pos
        self.z_pos = z_pos

class DynamicsInfo(object):
    '''catchall container for holding information about rigid bodies and their connections'''
    def __init__(self,connected_items,connections,newtonian_ids,material_properties):
        '''
        Initialization function

        :rtype: DynamicsInfo
        '''
#        
#        :param connected_items: 
#        :type connected_items: ?
#        :param connections: the damping coefficient of the joint
#        :type connections: ?
#        :param newtonian_ids: 
#        :type newtonian_ids: ?
#        :param material_properties: 
#        :type material_properties: ?
#        :rtype: DynamicsInfo
#        '''

        self.connected_items = connected_items
        self.connections = connections
        self.newtonian_ids = newtonian_ids
        self.material_properties = material_properties
        

if __name__=='__main__':
    import yaml
    d = DynamicsInfo(1,2,3,4)
    with open('asdf.yaml','w') as f:
        yaml.dump(d,f)
    
            