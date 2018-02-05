'''
Created on Nov 6, 2017

@author: Salim
'''
from pylods.decorators import order_attr, rename_attr, type_attr
from lessrpc_common.info.basic import ServiceInfo, EnvironmentInfo


@rename_attr('requestid','rid')
@order_attr('service',1)
@type_attr('service',ServiceInfo)
@type_attr('env',EnvironmentInfo)
class ServiceRequest():
    
    def __init__(self, service=None, env=None, requestid=None, args=None):
        self.service = service
        self.env = env
        self.requestid = requestid
        self.args = args
        
        
    @classmethod
    def create(cls, service, env, requestid, args):
        return ServiceRequest(service, env, requestid, args)        
        
    
    def __str__(self):
        tmp = "["
        for arg in self.args:
            tmp += getattr(arg, "__class__") + ","
        tmp = "]"
        return "{ServiceRequest service: " + self.service + "   env: " + self.env + "   requestId: " + self.requestid + "   args: " + tmp + "}"
    
    def __eq__(self, o):
        if isinstance(o, ServiceRequest):
            if not self.service is o.service and self.env is o.env and self.requestid is o.requestid :
                return False
            
            if not len(self.args) is len(o.args):
                return False
            
            for i in range(self.args):
                if self.args[i] is not o.args[i]:
                    return False
            
            return True            
    
        return False
    
    
    def __ne__(self, o):
        return not self == o
