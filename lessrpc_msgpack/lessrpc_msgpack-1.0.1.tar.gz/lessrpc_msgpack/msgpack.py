'''
Created on Jan 21, 2018

@author: Salim
'''
from lessrpc_common.serialize import Serializer
from pylods.deserialize import DeserializationContext
from lessrpc_common.info.basic import SerializationFormat
from pylodsmsgpack.pylodsmsgpack import MsgPackObjectMapper, MsgPackParser
import base64



class InBase64Wrapper():
    
    
    def __init__(self, instream):
        self.instream = instream
        self.cache = ''
        
        
     
    def read(self, size=-1):
        data = self.instream.read(size)
        finished = len(data) < size or size == -1
        if finished:
            return base64.b64decode(self.cache + data)
        else:
            idx = data.rfind('\n')
            idx = max(idx, data.rfind('='))
            if idx > -1:
                out = base64.b64decode(self.cache + data[0:idx])
                self.cache = data[idx:]
                return out
            else:
                self.cache = self.cache + data
        
    
    def close(self):
        self.instream.close()
            
    
class OutBase64Wrapper():
    
    
    
    def __init__(self, outstream):
        self.outstream = outstream
        self.cache = ''


    
    def write(self, data):
        size = len(data) + len(self.cache)
        sizetowrite = int(round(size / 3))*3
        fromcache = min(sizetowrite, len(self.cache))
        out = self.cache[0:fromcache] + data[0:(sizetowrite - fromcache)]
        self.cache = self.cache[fromcache:len(self.cache)] + data[(sizetowrite - fromcache):len(data)]
        self.outstream.write(base64.b64encode(out))
        

    
    def flush(self):
        if len(self.cache) > 0:
            self.outstream.write(base64.b64encode(self.cache))
            self.outstream.flush()
    
    def close(self):
        self.flush()
        self.outstream.close()
        
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
        if not isinstance(outstream, OutBase64Wrapper):
            outstream = OutBase64Wrapper(outstream)
        self.__mapper.write(obj, outstream) 
        
        
    def deserialize(self, instream, cls, ctxt=DeserializationContext.create_context()): 
        '''
            deserialize instream
        :param instream: inputstream
        :param cls class of object to be read:
        :return object instance of class cls
        '''
        if not isinstance(instream, InBase64Wrapper):
            instream = InBase64Wrapper(instream)
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



