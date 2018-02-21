"""
MIT License
Copyright (c) 2017 Roni Eliezer
"""

import ip_object
import http_session
from ssh import SSHI

#######################################################################
class BlackBox(ip_object.IpObject):
    """ Implements the black-box methods.
    
    Unlike unit-test where tests call directly to the tested software 
    functions, in black-box testing tests should access the tested software  
    through its interfaces, the most common interfaces are:
    CLI     = Command Line Interface
    GUI     = Graphic User Interface
    TCP     = HTTP, WebGUI, REST, SOAP, FTP
    UDP     = SNMP
    Virtual = VM/Docker, access or control the software through its VM/Container
    
    This class provide the above interfaces by using third party open-source
    modules.
    It initialized the interfaces according to configuration.
    
    e.g.: At the below configuration file example, rest & ssh are enable.
    
    content of file: setup_file_name.yaml
    server1:
        class: ochrus.blackbox.BlackBox
        ip: 1.1.1.1
        port: 8000
        username: admin
        password: admin
        rest: True
        ssh: True  
    
    Available Interfaces:
        - CLI is implemented by the ssh.SSHI class                   self.ssh
        - REST is implemented by http_session.Rest class             self.rest
        - SOAP is implemented by http_session.Soap class             self.soap
        - HTTP is implemented by http_session.Http class             self.http
        - WebUI will be implemented by Selenium                      self.selenium
        - SNMP - **NOT IMPLEMENTED YET**                             ???
        - MobileUI - **NOT IMPLEMENTED YET*                          ???
        - FTP - **NOT IMPLEMENTED YET**                              ???
        - Virtual Machine - will be implemented by Docker Machine    ???
        - Docker container - **NOT IMPLEMENTED YET**                 ???

                
    How to use:
    1. Subclass and add the relevant methods using the available interfaces.
        e.g.: for example, if our SUT (System Under Test) has a feature to 
              add user via CLI & REST
              
        to implement adding a user to the SUT via SSH
            self.ssh.send("adduser {}".format(username))
              
        to implement adding a user to the SUT via RESTfull API
            self.rest.post("adduser/" {"username": "{}".format(username)}) 

    
    2. Enable the interfaces at the configuration file
       The following configuration example define an instance of ochrus.blackbox.BlackBox
       class, called 'server1' and enabling 'ssh' and 'rest'
       
       server1:           # Instance name. Will be available through: setup.server1
          class: ochrus.blackbox.BlackBox  
          ip: 1.1.1.1     
          password: '' 
          port: '8080'
          ssl: 'False' 
          username: ''
          ssh: True
          rest: True   

    
    Args:
        ssl (bool):      [default disable], enable HTTPS connection only
        ssh (bool):      [default disable], enable SSH interface
        http (bool):     [default disable], enable HTTP interface
        rest (bool):     [default disable], enable REST interface
        soap (bool):     [default disable], enable SOAP interface
        selenium (bool): [default disable], enable & initialize Selenium 
         
    """

    #==================================================================
    def __init__(self, ssl=False, ssh=False, http=False, rest=False, soap=False, selenium=False, **kwargs):
        '''
        Constructor
        '''
        super(BlackBox, self).__init__(**kwargs)

        if ssh:
            self.ssh = SSHI(ip=self.ip, 
                            username=self.username, 
                            password=self.password)
        if http:
            self.http = http_session.Http(ip=self.ip, 
                                          port=self.port, 
                                          username=self.username, 
                                          password=self.password,
                                          ssl=ssl)
        if rest:
            self.rest = http_session.Rest(ip=self.ip, 
                                          port=self.port, 
                                          username=self.username, 
                                          password=self.password,
                                          ssl=ssl)
        if soap:
            self.soap = http_session.Soap(ip=self.ip, 
                                          port=self.port, 
                                          username=self.username, 
                                          password=self.password,
                                          ssl=ssl)
        #if selenium:
        #    self.selenium = 


    #==================================================================
    def get_params_as_dict(self):
        params = {"ssl":"{}".format(self.ssl)}
        super(BlackBox, self).get_params_as_dict().update(params)
        

            