'''
Created on Jul 21, 2017
 
@author: Salim
'''
from lessrpc_common import Utils as Utils
from lessrpc_common.Constants import SERIALIZATION_FORMAT_HTTP_FORMAT_FIELD_NAME, \
    SERIALIZATION_FORMAT_HTTP_FORMAT_FIELD_VERSION
import platform;
from lessrpc_common.errors.less import SerializationFormatHTTPNotParsable
from pylods.decorators import type_attr


class NameServerInfo():
    '''
    This class contains minimal information regarding a name server
     
    @author: Salim
    '''
    
    def __init__(self, address=None, port=None):
        self.address = address
        self.port = port
        
        
        
        
        
        
        
        
        
       
class ServiceInfo():
    """
        Service info class that contains minimal information regarding a defined service
        @author: Salim
    """
    
    def __init__(self, name=None, sid=None):
        self.name = name
        self.sid = sid
      
    
    def __eq__(self, o):
        if isinstance(o, ServiceInfo):
            return o.name == self.name and self.sid == o.sid
    
        return False
    
    def __ne__(self, o):
        return not self == o
    
    def __str__(self):
        return "{ServiceInfo   name:'" + str(self.name) + "', id:" + str(self.sid) + "}"        
 
 
 
class ServiceDescription():
    
    def __init__(self, info, argsclspaths, resultclspath):
        if not isinstance(argsclspaths, list):
            raise ValueError("argsclspaths must be a list of classpaths")
        self.__info = info
        self.__argsclspaths = argsclspaths
        self.__resultclspath = resultclspath
        
    
    def __get_info(self):
        return self.__info
    
    info = property(__get_info)
    
    def __get_argsclspaths(self):
        return self.__argsclspaths
    
    argsclasspath = property(__get_argsclspaths)
    
    def __get_resultclspath(self):
        return self.__resultclspath
    
    resultclspath = property(__get_resultclspath)
    
    def __str__(self):
        return "{ServiceDescription   info:'" + str(self.info) + "', args:" + str(self.argsclasspath) + " ,  result: " + str(self.resultclspath) + "}"
        




class ServiceLocator():
    
    def __init__(self):
        self.__map = {}
        
    def lookup(self,sid):
        return self.__map.get(sid,None)
    
    def put(self, sid, desc):
        self.__map[sid] = desc
    
    @classmethod
    def create(cls, services=[]):
        locator = ServiceLocator()
        for service in services:
            locator.put(service.info.sid, service)
            
        return locator





class EnvironmentInfo():
    """
        Environment info contains information that allows to know requirements of a client/server stub
    """
    
    def __init__(self, lang=None, os=None, compiler=None):
        self.lang = lang
        self.os = os
        self.compiler = compiler
        
        
    
    def get_os_name(self):
        return self.os.split("/")[0]
    
    
    def get_os_version(self):
        return self.os.split("/")[1]
            
    
    def get_lang_name(self):
        return self.lang.split("/")[0]
    
    def get_lang_version(self):
        return self.lang.split("/")[1]
    
    
    def get_compiler_name(self):
        return self.compiler.split("/")[0]
    
    def get_compiler_version(self):
        return self.compiler.split("/")[1]
    
    
    @classmethod
    def current_env_info(cls):
        lang = "Python/" + platform.python_version()
        os = platform.system() + "/" + platform.release()
        compiler = platform.python_implementation() + "/" + platform.python_version()
        return EnvironmentInfo(lang, os, compiler)
    
    
    
    def __str__(self):
        return "{ EnviromentInfo lang: " + str(self.lang) + ", os: " + str(self.os) + ", compiler: " + str(self.compiler) + "}";
    
    
    
    def __eq__(self, o):
        if isinstance(o, EnvironmentInfo):
            return self.lang == o.lang and self.os == o.os and self.compiler == o.compiler;
    
        return False
    
    
    def __ne__(self, o):
        return not self == o
      
            
    
    


@type_attr('env', EnvironmentInfo)
class ServiceProviderInfo():
    """
        Contains minimal information regarding a provider
    """
    
    def __init__(self, url=None, port=None, env=None):
        self.url = url
        self.port = port                
        self.env = env
            
    
    def __str__(self):
        return "{ServiceProviderInfo url:" + str(self.url) + ", port: " + str(self.port) + ", env: " + str(self.env) + " }";
    
    def __eq__(self, o):
        if isinstance(o, ServiceProviderInfo):
            return self.env == o.env and self.url == o.url and self.port == o.port
    
        return False
    
    def __ne__(self, o):
        return not self == o








        
class SerializationFormat():
    """
  
    SerializationFormat object contains the following fields:
      
    <strong>format: </strong>Name of serialization format</li>
      <li><strong>version: </strong>Version information</li>
      </ul>
  
      @author Salim
 
     """
 
    def __init__(self, name="", version=""):
        self.name = name.lower();
        self.version = version.lower();
            
    
    def __hash__(self):
        return hash(self.name + "/" + self.version);
    
    def http_format(self):
        return "application/vnd.less ;lessversion=\"" + str(Utils.less_version()) + "\" ; format=\"" + str(self.name) + "\" ; formatversion=\"" + str(self.version) + "\"";
    
    def __eq__(self, o):
        if isinstance(o, SerializationFormat):
            return o.name == self.name and o.version == self.version
    
        return False
    
    def __ne__(self, o):
        return not self == o
    
    def __str__(self):
        return "{SerializationFormat name=\"" + str(self.name) + "\", version=\"" + str(self.version) + "\"}";
    
    @staticmethod
    def default_format():
        return SerializationFormat('JSON', "");
    
    @staticmethod
    def parse_http_format(txt):
        parts = txt.split(";")        
        name = None
        version = None
        
        for i in range(1,len(parts)):
            eqIdx = parts[i].strip().find("=")
            eqQIdx = parts[i].strip().find("=\"")
            fieldname = parts[i].strip()[0:eqIdx]
            value = None;
            
            if (eqQIdx != -1):
                value = parts[i].strip()[eqQIdx + 2: len(parts[i].strip()) - 1]
            else:
                value = parts[i].strip()[eqQIdx + 2: len(parts[i].strip()) ] 
            

            if fieldname == SERIALIZATION_FORMAT_HTTP_FORMAT_FIELD_NAME:
                name = value
            elif fieldname == SERIALIZATION_FORMAT_HTTP_FORMAT_FIELD_VERSION:
                version = value                
                
        
        if name == None or version == None:
            raise SerializationFormatHTTPNotParsable(txt);
            
        return SerializationFormat(name, version);
        
        
        
        
        
        
        
class SerializedObject():
    '''
        SerializedObject class that contains generic classes and includes classpath for serialization/deserialization
    '''


    def __init__(self, content=None, classpath=None):
        '''
        Constructor
        '''
        self._content = None
        self.content = content
        self.classpath = classpath
        if(classpath is None):
            self.classpath = Utils.class_path(content);        
        
    
        
    
    def get_content(self):
        return self.content
    

    def set_content(self, content):
        self._content = content
        self.classpath = Utils.class_path(content)
        
        
    content = property(get_content, set_content)
    
    
    
    
    
    
    
    
    
@type_attr("service", ServiceInfo)
@type_attr("provider", ServiceProviderInfo)
@type_attr("serializers", SerializationFormat)
class ServiceSupportInfo():
    '''
        ServiceSupportInfo contains information for support of a provider for a specific service
    '''
    
    def __init__(self, service=None, provider=None, serializers=None):
        self.service = service
        self.provider = provider
        self.serializers = serializers
        
        
    def __str__(self):
        tmp = "{ServiceSupportInfo   service: " + str(self.service) + ",   provider: " + str(self.provider) + "  serialziers=[";
        if(self.serializers is not None):
            for serializer in self.serializers:
                tmp += ", " + str(serializer);
                
        return tmp
    
    
    def __eq__(self, o):
        if not isinstance(o, ServiceSupportInfo):
            return False
        
        if o.service != self.service:
            return False
        
        if len(o.serializers) != len(self.serializers):
            return False
        
        for i in range(0, len(self.serializers)):
            if  self.serializers[i] != o.serializers[i]:
                return False        
    
        return True
    
    def __ne__(self, o):
        return not self == o
    
    
        
    
        
        
        
        

