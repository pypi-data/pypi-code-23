'''
Created on Nov 7, 2017

@author: Salim
'''
from abc import abstractmethod, ABCMeta


class ProviderLoadBalancer():
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def select(self, service, supports):
        pass
    
    
