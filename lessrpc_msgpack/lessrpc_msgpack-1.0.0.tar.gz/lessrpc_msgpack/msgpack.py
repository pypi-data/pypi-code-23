'''
Created on Jan 21, 2018

@author: Salim
'''
from lessrpc_common.serialize import Serializer
from pylods.deserialize import DeserializationContext
from lessrpc_common.info.basic import SerializationFormat
from pylodsmsgpack.pylodsmsgpack import MsgPackObjectMapper, MsgPackParser


class MsgPackSerializer(Serializer):
    '''
        MsgPackSerializer is the default serializer for less RPC if a serializer couldn't be recognized
    '''
    
    __slots__ = ['__mapper']
    
    def __init__(self, mapper=MsgPackObjectMapper()):
        self.__mapper = mapper
        
    
    def serialize(self, obj, cls, outstream): 
        '''
            serialize into outstream
        :param obj:
        :param cls:
        :param outstream:
        :return no output
        '''
        self.__mapper.write(obj, outstream) 
        
        
    def deserialize(self, instream, cls, ctxt=DeserializationContext.create_context()): 
        '''
            deserialize instream
        :param instream: inputstream
        :param cls class of object to be read:
        :return object instance of class cls
        '''
        parser = MsgPackParser()
        parser = parser.parse(instream)
        return self.__mapper.read_obj(parser, cls, ctxt=ctxt)
        
    def get_type(self):
        return SerializationFormat("MSGPACK", "2.0")
        

    def prepare(self, module):
        self.__mapper.register_module(module)
    
    
    def copy(self):
        tmp = MsgPackSerializer()
        tmp.__mapper = self.__mapper.copy()
        return tmp


