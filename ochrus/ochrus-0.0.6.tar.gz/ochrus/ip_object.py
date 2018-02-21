"""
MIT License
Copyright (c) 2017 Roni Eliezer
"""

##############################################################################
class BasicObject(object):
    """ 
    Root class for all objects at the project.
    
    Attributes:
        name (str):       to identify the object by name
        enable (bool):    sign the class status
        
    """   
    def __init__(self, name=None, enable=True):
        self._name = name
        self._enable = enable

    #-------------------------------------------------------------------------
    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, name):
        self._name = name            

    #-------------------------------------------------------------------------
    @property
    def enable(self):
        return self._enable
    
    @enable.setter
    def enable(self, enable):
        self._enable = enable            

    #==================================================================
    def get_params_as_dict(self):
        """
        Return a dictionary with all object parameters 
        """
        return  {"name": "{}".format(self.name),
                 "enable": "{}".format(self.enable),
                }


##############################################################################
class IpObject(BasicObject):
    '''
    Represent any object that required IP 
    '''   
    def __init__(self, ip=None, port=None, username=None, password=None, name=None, enable=True):
        '''
        Constructor
        '''
        super(IpObject, self).__init__(name, enable)
        self._ip = ip
        self._port = port
        self._username = username
        self._password = password

    #==================================================================
    @property
    def ip(self):
        return self._ip
    
    @ip.setter
    def ip(self, ip):
        self._ip = ip

    #==================================================================
    @property
    def port(self):
        return self._port
    
    @port.setter
    def port(self, port):
        self._port = port

    #==================================================================    
    @property
    def username(self):
        return self._username
    
    @username.setter
    def username(self, username):
        self._username = username
    

    #==================================================================    
    @property
    def password(self):
        return self._password
    
    @password.setter
    def password(self, password):
        self._password = password


    #==================================================================
    def get_params_as_dict(self):
        params = {"ip": "{}".format(self.ip),
                "port": "{}".format(self.port),
                "username":"{}".format(self.username),
                "password":"{}".format(self.password)
                }
        return super(IpObject,self).get_params_as_dict().update(params)
        