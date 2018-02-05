'''
Created on Nov 7, 2017

@author: Salim
'''
from abc import ABCMeta, abstractmethod 
from pylods.deserialize import DeserializationContext



class Serializer():
    __metaclass__ = ABCMeta
    
    
    @abstractmethod
    def serialize(self, obj, cls, outstream): 
        '''
            serialize into outstream
        :param obj:
        :param cls:
        :param outstream:
        :return no output
        '''
        
    @abstractmethod
    def deserialize(self, instream, cls, ctxt=DeserializationContext.create_context([])): 
        '''
            deserialize instream
        :param instream: inputstream
        :param cls class of object to be read:
        :return object instance of class cls
        '''
    @abstractmethod
    def prepare(self, module):
        '''
        prepares the serialize using the given module
        :param module:
        :return a Serializer instance
        '''
    
        
    @abstractmethod
    def get_type(self):
        '''
            Returns the SerializationFormat for this serializer's type
        '''
        
    
    def __hash(self):
        sformat = self.get_type()
        return hash(sformat.name+"/"+sformat.version)
    
    @abstractmethod
    def copy(self):
        '''
         return a duplicate copy of the serializer
        '''
        
        
    
