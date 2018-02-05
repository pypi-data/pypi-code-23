'''
Created on Nov 7, 2017

@author: Salim
'''


class DatabaseNotSupported(Exception):
    
    def __init__(self, dtype):
        # Call the base class constructor with the parameters it needs
        super(DatabaseNotSupported, self).__init__("Database " + dtype + " not supported by the manager")


class RPCException(Exception):
    
    def __init__(self, status, content):
        # Call the base class constructor with the parameters it needs
        super(RPCException, self).__init__("RPCException  status: +" + str(status) + " , content" + str(content) + "")
        self.status = status
        self.content = content
        
    def __str__(self,):
        return "{RPCException  status: " + str(self.status) + " , content: " + str(self.content) + "}";
    
    
    
class ServerStubNotInitialized(Exception):
    
    def __init__(self):
        # Call the base class constructor with the parameters it needs
        super(ServerStubNotInitialized, self).__init__()           
    
    
        
class TranslationNotSupportedException(Exception):
    
    def __init__(self, txt):
        # Call the base class constructor with the parameters it needs
        super(TranslationNotSupportedException, self).__init__(txt)           
        
        
        
class NoProviderAvailableException(Exception):
    
    def __init__(self, service):
        # Call the base class constructor with the parameters it needs
        super(NoProviderAvailableException, self).__init__("Tried to fetch a provider info from NameServer but NameServer did not return any for service: "
                + service)        