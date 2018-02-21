"""
MIT License
Copyright (c) 2017 Roni Eliezer
"""

import os
import sys
from txtfile import Yaml
from http_session import Rest
import setup
import logger


class OchrusConfig(object):
    """
    Handle Ochrus base configuration
    Used by pytest-ochrus
    """
    
    def __init__(self, rootdir):
        self.rootdir = rootdir
        self._ochrus_file_name = "ochrus.yaml"
        self.file_path = self.rootdir +"/"+ self._ochrus_file_name
        self.file_yaml = Yaml(self.file_path)
        self.params = None

    #==================================================================
    def init(self):
        """ initialize ochrus main modules.
        
        This method must be called after instancing OchrusConfig class 
        and setting its 'rootdir' parameter
        """
        logger.out = logger.TextLogger(rootdir=self.get_logs_dir())
        setup.setup_dirs =  self.get_setups_dirs()
         
    #==================================================================
    def _get_defaults(self):
        """ 
        Default configuration.
        Can be sets through the main config file "ochrus.yaml" 
        """
        data =  {'server':{'ip'       : 'ochrus',
                           'port'     : '80',
                           'username' : '',
                           'password' : '',
                           'ssl'      : 'False'
                           },
                 'logger':{"output":"."},
                 'setups':{"dirs":["./setups/"]},
                 }
        return data
            
    #==================================================================
    def _get_config(self):
        """ 
        Return a dictionary with config params. 
        
        Note:
            If config file was not found at the given self.rootdir then
            it will create the config file at the rootdir with default 
            values
        
        Returns:
            Dictionary with data as read from config file or setting from
            current build-in parameters 
            
        """
        if os.path.exists(self.file_path):
            self.params = self.file_yaml.load()
        else:
            self.params = self._get_defaults()
            self.file_yaml.dump(self.params)
            print "file '{}' with default values was created at: '{}'\n"\
                  .format(self._ochrus_file_name, self.rootdir)+\
                  "you can add the 'ochros' domain name at the "+\
                  "'hosts' file of the runner machine "+\
                  "or replace it with the server IP address"   
        return self.params
    

    #==================================================================
    def _get_dir(self, section, key):
        """ 
        Get the directory written under given 'section' 'key'.
        If user entered dot (".") then it will return 'self.rootdir'
        """
        self._get_config()
        try:
            dirc = self.params[section].get(key)
            if len(dirc)==1 and dirc[0].strip().lower()==".":
                return self.rootdir
            else:
                return dirc
        except:
            return self.rootdir

    #==================================================================
    def get_logs_dir(self):
        """ 
        Return the 'logs' directory.
        If user entered dot (".") then it will return 'self.rootdir'
        """
        section="logger"
        key="output"
        
        self._get_config()
        try:
            dirc = self.params[section].get(key)
            if dirc.strip().lower()==".":
                return self.rootdir
            else:
                return dirc
        except:
            return self.rootdir

    #==================================================================
    def get_setups_dirs(self):
        """ 
        Return the setups files directory.
        If user entered dot (".") then it will return 'self.rootdir'
        """
        section="setups"
        key="dirs"

        self._get_config()
        try:
            directories = self.params[section].get(key)
            
            if type(directories) is str:    #list is expected
                directories = [directories]
                
            for i in range(0, len(directories)):
                if directories[i].strip().lower()==".":
                    directories[i] = self.rootdir
        except:
            return [self.rootdir]
        
        return directories


    #======================================================================
    def get_result_server(self):
        """ 
        Return a Rest interface to the Ochrus result server
        
        Note:
            This method used by the pytest-ochrus plugin
        """
        self._get_config()
        try:    
            ip       = self.params["server"].get("ip")
            username = self.params["server"].get("username")
            password = self.params["server"].get("password")
            port     = self.params["server"].get("port")
            ssl      = self.params["server"].get("ssl")
        except Exception as e:
            print "Got exception while trying to read Ochrus params: {}"+\
                  "Exception: {}"+format(self.params, e)
            sys.exit(1)
            
        return Rest(ip=ip, username=username, password=password, port=port, ssl=ssl)

