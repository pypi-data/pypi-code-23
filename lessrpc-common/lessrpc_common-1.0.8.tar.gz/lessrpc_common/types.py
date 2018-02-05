'''
Created on Nov 7 = 
2017

@author: Salim
'''
from enum import Enum


class DBType(Enum):
    
    MYSQL, SQLLITE, ORACLE = range(1,4)


class StatusType(Enum):
    '''
        List of status types and their codes. APPLICATION_SPECIFIC_ERROR codes are all treated as 3000
    '''
    
    OK = 1000
    PARSE_ERROR = 2001
    SERIALIZATION_NOT_SUPPORTED = 2002 
    ARGS_CANNOT_BE_PARSED =  2003
    SERVICE_NOT_SUPPORTED = 2004
    CONTENT_TYPE_NOT_SUPPORTED =  2005
    INVALID_ARGS =  2006
    ACCEPT_TYPE_NOT_SUPPORTED = 2007 
    INTERNAL_ERROR =  2008
    SERIALIZATION_ERROR =  2009 
    ACCEPT_TYPE_CANNOT_BE_PARSED = 2010 
    CONTENT_TYPE_CANNOT_BE_PARSED =  2011
    POST_CONTENT_NOT_AVAILABLE = 2012
    WRONG_HTTP_METHOD = 2013
    APPLICATION_SPECIFIC_ERROR = 3000 
    UNKOWN = -1
    
    @classmethod
    def from_code(cls,code):
        if(code >= 3000 and code <=4000):
            return StatusType.APPLICATION_SPECIFIC_ERROR
        return StatusType(code)

