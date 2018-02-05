'''
This modules contains classes and abstract classes required by database access 

Created on Nov 6, 2017

@author: Salim
'''
from abc import abstractmethod, ABCMeta
import abc


'''
    class contains all information required for connecting database
'''
class DBInfo():
    
    def __init__(self, url, name, user, password, dbtype):
        self.url = url
        self.name = name
        self.user = user
        self.password = password
        self.dbtype = dbtype
        
        


'''
    class contains abstract definition of all functions required by a DBUtil implementation
'''
class DBUtils(abc):
    __metaclass__ = ABCMeta
        
    
    @abstractmethod
    def get_providers(self, conn, service):
        """
           get list of all Server info that implements service with given id 
        """ 
        pass
        
    
    @abstractmethod
    def get_all_providers(self, conn, service): 
        """
            get list of all Server info for all service
        """ 
        pass
        
        
    
    
    @abstractmethod
    def get_service_info_by_id(self, conn, service_id): 
        """
            get ServiceInfo for given service name
        """ 
        pass


    @abstractmethod
    def get_service_info_by_name(self, conn, service_name): 
        """
            get ServiceInfo for given service id
        """ 
        pass
    
    
    @abstractmethod
    def register(self, conn, support): 
        """
            register given server for given service
        """ 
        pass
    
    
    @abstractmethod
    def unregister(self, conn, service, provider): 
        """
           remove given server from given service 
        """ 
        pass
    
    @abstractmethod
    def unregister_all(self, conn, provider): 
        """
            remove given server from all its registered services
        """ 
        pass
    
        
        
        
    
