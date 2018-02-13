# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>asu.edu.
Please see LICENSE for full license.
"""
class ClassAlgebra(object):
    '''
    This class is used to map standard Python operators to specific function names, making it easy for any child to implement CSG-like functionality
    '''
    def __or__(self,other):
        '''Union one object with another'''
        return self.union(other)
        
    def __sub__(self,other):
        '''Subtract one object from another'''
        return self.difference(other)
        
    def __and__(self,other):
        '''And one object with another'''
        return self.intersection(other)        

    def __xor__(self,other):
        '''Exclusive-Or (or take the symmetric difference of) one object with another'''
        return self.symmetric_difference(other)

    def __lshift__(self,value):
        '''dilate an object'''
        return self.dilate(value)

    def __rshift__(self,value):
        '''erode an object'''
        return self.erode(value)
        
