'''
Created on Nov 7, 2017

@author: Salim
'''
from __builtin__ import property
from lessrpc_common.info.basic import  ServiceProviderInfo, \
    ServiceSupportInfo, ServiceInfo, ServiceLocator
from abc import abstractmethod, ABCMeta
from pylods.decorators import type_attr, use_deserializer, rename_attr,\
    order_attr
from pylods.deserialize import EventBasedDeserializer, DeserializationContext, \
    POPState
from pylods.mapper import ObjectMapper



@type_attr('service', ServiceInfo)
@rename_attr('requesid', 'rid')
@rename_attr('__content', 'content')
@order_attr("service",1)
@order_attr("requestid",2)
@order_attr("content",3)
class ServiceResponse():
    """
    <p>
      Every call to /execute method will result with a response from the
      ServiceProvider which will follow the specifications below for a
      ServiceResponse object. LESS-RPC unlike
      <a href="http://www.jsonrpc.org/specification">JSON-RPC</a> does not
      differentiate between normal method calls and notifications. However, the
      response for notifications will be minimal. Requiring a response for
      notification can assure client application whether the service provider has
      been successful in retrieving and processing the notification.
      ServiceResponse object contains the following fields:
      </p>
      <ul style="list-style-type: circle; margin-left: 3em;">
      <li><strong>service*: </strong>Instance of ServiceInfo object</li>
      <li><strong>rid*: </strong>contains the request id generated for the request.
      request id can be used by the client to identify responses in asynchronous or
      batch mode.</li>
      <li><strong>status*: </strong> result status code</li>
      <li><strong>content*: </strong> result object which must be contain fields of
      a SerializedObject if the result is a value. In case the function called is
      finished with an error status the content will contain additional information
      regarding the error in plain text format</li>
      </ul>
      <br/>
      </p>
    """
    def __init__(self, service=None, content=None, requestId=None):
        self.service = service
        self.content = content
        self.requestId = requestId  
        
        
    
    def __get_content(self):
        return self.__content
    
    def __set_content(self, content):
        self.__content = content
    
    
    def __eq__(self, o):
        if isinstance(o, ServiceResponse):
            if not self.service is o.service and self.content is o.content and self.requestid is o.requestid :
                return False                        
            return True            
    
        return False
    
    
    def __ne__(self, o):
        return not self == o
    
    
    def __str__(self):
        return "{ServiceResponse service: " + str(self.service) + " ,  requestId: " + str(self.requestId) + ",  content: " + str(self.content) + " }"
    
    
    content = property(__get_content, __set_content);
        
        
        

class RequestResponse():
    __metaclass__ = ABCMeta
    
    def __init__(self, status=None , content=None):
        self.status = status
        self._content = content
        
    
    def validate_type(self, content):
        """
            Checks the type of content and makes sure it is the right type
        """
        return isinstance(content, self.accepted_type())
    
    def __str__(self):
        return "RequestResponse  type: " + str(self.__class__) + " ,  status: " + str(self.status) + " ,   content: " + str(self.content) + "}"
        
    @abstractmethod   
    def accepted_type(self):
        pass
    
    def __get_content(self):
        return self._content
    
    def __set_content(self, content):
        if(content is None or self.validate_type(content)):
            self._content = content
        else:
            raise Exception(str(content) + ' is not an instance of valid type ' + str(self.accepted_type()))
    
    content = property(__get_content, __set_content);
    
class ExecuteRequestResponseDeserializer(EventBasedDeserializer):
    
    def deserialize(self, events, pdict, ctxt=DeserializationContext.create_context()):
        response = ExecuteRequestResponse()
        
        fieldname = None
        eventitr = events
        
        event = eventitr.next()
        try:
            while event:
                if(pdict.is_obj_property_name(event)):
                    fieldname = pdict.read_value(event)
                elif(fieldname is not None):
                    if(fieldname == 'status'):
                        if pdict.is_value(event):
                            response.status = pdict.read_value(event)
                    elif(fieldname == 'content'):
                        resp = ServiceResponse()
                        response.content = resp
                        fieldname2 = None
                        if pdict.is_obj_start(event):
                            while not pdict.is_obj_end(event):
                                if(pdict.is_obj_property_name(event)):
                                    fieldname2 = pdict.read_value(event)
                                elif(fieldname2 is not None):
                                    if(fieldname2 == 'rid'):
                                        resp.requestId = pdict.read_value(event);
                                    elif(fieldname2 == 'service'):
                                        mapper = ObjectMapper(pdict)
                                        resp.service = mapper.read_obj(events, ServiceInfo, state=POPState.EXPECTING_OBJ_PROPERTY_OR_END, ctxt=ctxt)
                                    elif(fieldname2 == 'content'):
                                        mapper = ObjectMapper(pdict)
                                        locator = ctxt.get_attribute('CLSLOCATOR', ServiceLocator.create())
                                        if pdict.is_value(event):
                                            resp.content = pdict.read_value(event)
                                        elif pdict.is_array_start(event):
                                            resp.content = mapper.read_array(events, state=POPState.EXPECTING_VALUE, cls=locator.lookup(resp.service.sid).resultclspath, ctxt=ctxt)
                                        elif pdict.is_obj_start(event):    
                                            resp.content = mapper.read_obj(events, locator.lookup(resp.service.sid).resultclspath, state=POPState.EXPECTING_OBJ_PROPERTY_OR_END, ctxt=ctxt)
                                        
                                
                                
                                event = eventitr.next()
                    fieldname = None
                event = eventitr.next()
                
        except StopIteration:
            pass
        
        return response
    
        
@type_attr('content', ServiceResponse)
@use_deserializer(ExecuteRequestResponseDeserializer)
class ExecuteRequestResponse(RequestResponse):
    '''
        
    '''
    def accepted_type(self):
        return ServiceResponse;
        
        
@type_attr('content', int)    
class IntegerResponse(RequestResponse):
    '''
        
    '''
    def accepted_type(self):
        return int;
    

@type_attr('content', ServiceProviderInfo)
class ProviderInfoResponse(RequestResponse):
    '''
        
    '''
    def accepted_type(self):
        return ServiceProviderInfo;
    
@type_attr('content', ServiceSupportInfo)    
class ServiceSupportResponse(RequestResponse):
    '''
        
    '''
    def accepted_type(self):
        return ServiceSupportInfo;    
    

@type_attr('content', str)    
class TextResponse(RequestResponse):
    '''
        
    '''
    def accepted_type(self):
        return unicode;
    
    
    
        
class ServiceRequestDeserializer(EventBasedDeserializer):
    
    def deserialize(self, events, pdict, ctxt=DeserializationContext.create_context()):
        pass
        
    
