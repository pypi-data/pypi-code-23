'''
Created on Nov 7, 2017

@author: Salim
'''
from abc import abstractmethod, ABCMeta
from lessrpc_common.info.basic import ServiceInfo, ServiceDescription, \
    ServiceProviderInfo, ServiceSupportInfo




class NameServerFunctions():
    __metaclass__ = ABCMeta
    '''
        service definitions for a working name server. This class is extended by both a NameServer implementation and a NameServer client
    '''
    
    
    @abstractmethod
    def get_provider(self, service):
        '''
            Returns one service provider information for a service given the
            service's id. The process of choosing a service provider may have been
            random or based on a load balancing strategy. However, the decision is
            made by the name server        
        :param service:
        '''
        pass
    
    
    @abstractmethod
    def get_providers(self, service):
        '''
            This function returns all service providers implementing the requested service
        :param service:
        '''
        pass
    
    
    @abstractmethod
    def get_all_providers(self):
        '''
            returns all Service Provider informations for all available services
        '''
        pass
    
    
    @abstractmethod
    def get_service_info_by_name(self, name):
        '''
            returns a service information object for given service name
        :param name:
        '''
        pass
    
    
    @abstractmethod
    def get_service_info_by_id(self, sid):
        '''
            returns a service information object for given service id
        :param sid:
        '''
        pass
    
    
    @abstractmethod
    def register(self, support):
        '''
            Registers a new service provider for given service information
        :param support:
        '''
        pass
    
    @abstractmethod
    def unregister(self, service, provider):
        '''
            Unregisters a new service provider for given service information
        :param service:
        :param provider:
        '''
        pass
    
    
    @abstractmethod
    def unregister_all(self, provider):
        '''
            Unregisters a new service provider for all of the registered services
        :param provider:
        '''
        pass
    
    
    @abstractmethod
    def check_provider_status(self, provider):
        '''
            This function forces the name server to check a provider's status and
            update its tables. The returned boolean indicates that the check was done
            or not and is not related to the actual status of the provider
        :param provider:
        '''
        pass
    
    
    @abstractmethod
    def ping(self):
        '''
            Determines if everything is working properly
        '''
        pass
    
    
    
    





class NameServerServices():
    '''
        Services' constants that a name server provides.  
    '''
    
    ''' =============================================================
        ==================Get Providers =============================
        =============================================================
    '''
    '''
        Service to get best provider for a specific service
    '''
    GET_PROVIDER = ServiceDescription(ServiceInfo("getProvider", 1), [ServiceInfo], ServiceSupportInfo) 
    
    
    '''
        Service to get all providers for a specific service
    '''
    GET_PROVIDERS = ServiceDescription(ServiceInfo("getProviders", 2), [ServiceInfo], ServiceSupportInfo)
    '''
        Service to get all providers available for all services
    '''
    GET_ALL_PROVIDERS = ServiceDescription(ServiceInfo("getAllProviders", 3), [], ServiceSupportInfo)
    
    ''' =============================================================
        ==================ServiceInfo ===============================
        =============================================================
    '''
    
    
    '''
        Service info for service that provides detail service info object given
        the name of service
    '''
    GET_SERVICE_INFO_BY_NAME = ServiceDescription(ServiceInfo("getServiceInfoByName", 4), [str], ServiceInfo)
    
    '''
        Service info for service that provides detail service info object given the id of the service
    '''
    GET_SERVICE_INFO_BY_ID = ServiceDescription(ServiceInfo("getServiceInfoById", 5), [int], ServiceInfo)
    
    ''' =============================================================
        ================== Register/Unregister ======================
        =============================================================
    '''
    
    '''
        Service info for service that allows unregistering a provider from a service
    '''
    REGISTER = ServiceDescription(ServiceInfo("register", 6), [ServiceSupportInfo], bool)
    
    '''
        Service info for unregistering a provider to a service
    '''
    UNREGISTER = ServiceDescription(ServiceInfo("unregister", 7), [ServiceInfo, ServiceProviderInfo], bool)
    
    '''
        Service info for unregistering a provider from all services
    '''
    UNREGISTER_ALL = ServiceDescription(ServiceInfo("unregisterAll", 8), [ServiceProviderInfo], bool)

    ''' =============================================================
        ========================= Status ============================
        =============================================================
    '''
    
    '''
        Service info for checking a provider status. The returned boolean
        determines that this task has been carried out or not. It doesn't
        indicate whether the provider is unreachable or not
    '''
    CHECK_PROVIDER_STATUS = ServiceDescription(ServiceInfo("checkProviderStatus", 9), [ServiceProviderInfo], bool)
    
    
    def set(self, value):
        raise TypeError
    
    
    


class ServiceProvider():
    __metaclass__ = ABCMeta
    '''
         ServiceProivder basic functional definition class. All service provider classes should support the methods in this class 
    '''
    
    @abstractmethod    
    def ping(self):
        '''
            This is called to check if the server is working. It has to just return a boolean flag
        '''
    
    
    @abstractmethod    
    def execute(self, request):
        '''
            This is called to execute a service
            
        :param request:
        '''
    
    
    @abstractmethod    
    def info(self):
        '''    
              This is called to get the ServiceProivder info regarding this service provider
        '''
    
    
    @abstractmethod    
    def service(self, service):
        '''
            This is called to get ServuceSupportInfo for a service. It will return ServiceNotSupported Exception
            
        :param service:
        '''
    
    
    
    @abstractmethod    
    def list_support(self):
        '''
            Returns the list of all supported services
        '''
        
        
    @abstractmethod    
    def list_services(self):
        '''
            Returns the list of all supported services
        '''
        
        
