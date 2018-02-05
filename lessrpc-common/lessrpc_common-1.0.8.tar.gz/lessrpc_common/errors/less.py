'''
Created on Nov 7, 2017

@author: Salim
'''



        

class AcceptTypeHTTPFormatNotParsable(Exception):
    
    def __init__(self, message):
        # Call the base class constructor with the parameters it needs
        super(AcceptTypeHTTPFormatNotParsable, self).__init__("AcceptType http syntax not parsable = \"" + str(message) + "\"")
        
        
        
        

class AcceptTypeNotSupported(Exception):
    
    def __init__(self, accept):
        # Call the base class constructor with the parameters it needs
        super(AcceptTypeNotSupported, self).__init__("SerializationFromat http syntax not parsable = \"" + str(accept) + "\"")
        
        

class ApplicationSpecificErrorException(Exception):
    
    def __init__(self, errorcode, content):
        # Call the base class constructor with the parameters it needs
        super(ApplicationSpecificErrorException, self).__init__("ApplicationSpecificError,  code: " + str(errorcode) + ", content: " + str(content))                        
        self.errorcode = errorcode
        self.content = content




class ContentTypeHTTPFormatNotParsable(Exception):
    
    def __init__(self, txt):
        # Call the base class constructor with the parameters it needs
        super(ContentTypeHTTPFormatNotParsable, self).__init__("ContentType http syntax not parsable = \"" + str(txt) + "\"")
        
        
        
        
class ContentTypeNotSupported(Exception):
    
    def __init__(self, sformat):
        # Call the base class constructor with the parameters it needs
        super(ContentTypeNotSupported, self).__init__("ContentType not supported:  \"" + str(sformat.httpFormat()) + "\"")
        
        
        
        
class ExecuteInternalError(Exception):
    
    def __init__(self):
        # Call the base class constructor with the parameters it needs
        super(ExecuteInternalError, self).__init__()
        
        
class InvalidArgsException(Exception):
    
    def __init__(self, txt):
        # Call the base class constructor with the parameters it needs
        super(InvalidArgsException, self).__init__(txt)
                        
                        
                        
                        
class PingResponseNotParsable(Exception):
    
    def __init__(self, txt):
        # Call the base class constructor with the parameters it needs
        super(PingResponseNotParsable, self).__init__("Response \"" + txt + "\" is not parsable as boolean. Ping response should be 0 or 1")
        
        
        
class ResponseContentTypeCannotBePrasedException(Exception):
    
    def __init__(self, txt):
        # Call the base class constructor with the parameters it needs
        super(ResponseContentTypeCannotBePrasedException, self).__init__("contentType:" + str(txt))
        
        
        
        
class RPCProviderFailureException(Exception):
    
    def __init__(self):
        # Call the base class constructor with the parameters it needs
        super(RPCProviderFailureException, self).__init__()
        
        
        
class SerializationFormatHTTPNotParsable(Exception):
    
    def __init__(self, txt):
        # Call the base class constructor with the parameters it needs
        super(SerializationFormatHTTPNotParsable, self).__init__("SerializationFromat http syntax not parsable = \"" + str(txt) + "\"")           
        
        
        
class SerializationFormatNotSupported(Exception):
    
    def __init__(self, sformat):
        # Call the base class constructor with the parameters it needs
        super(SerializationFormatNotSupported, self).__init__("SerializationFormat not supported: " + str(sformat.httpFormat()))           
        
        
        
        
class ServiceNotSupportedException(Exception):
    
    def __init__(self,service ):
        # Call the base class constructor with the parameters it needs
        super(ServiceNotSupportedException, self).__init__("Service not supported by provider - service info: " + str(service))           
        
        
class ServiceProviderNotAvailable(Exception):
    
    def __init__(self, service):
        # Call the base class constructor with the parameters it needs
        super(ServiceProviderNotAvailable, self).__init__("NameService didn't return an ServiceProviderInfo for service: " + str(service))           
        
        
class UnderterminableCodeException(Exception):
    
    def __init__(self ):
        # Call the base class constructor with the parameters it needs
        super(UnderterminableCodeException, self).__init__()                                                                                                                   


class WrongHTTPMethodException(Exception):
    
    def __init__(self , method):
        # Call the base class constructor with the parameters it needs
        super(WrongHTTPMethodException, self).__init__(method)
        
        
        
        