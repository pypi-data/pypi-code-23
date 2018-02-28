# -*- coding: utf-8 -*-
"""
Created on Thu Dec 29 10:40:58 2011

@author: cedric
"""

import os
import logging

def has_env(var):
    """ function to check existence of an environment variable
    or return an explicit exception message"""
    if var in os.environ or var.upper() in os.environ:
        return True
    return False
    #raise KeyError('%s is not defined in environment variables'%var)

def get_env(var):
    """ function to check and retrieve environment variable """
    has_env(var)
    if var in os.environ:
        return os.environ[var]
    if var.upper() in os.environ:
        return os.environ[var.upper()]

from ._project import ProjectManager


def check_dev_envs():
    """ function to check all environment variables """
    for var in ENVVARS.keys():
        if not has_env(var):
            raise KeyError('%s is not defined in environment variables'%var)

def createUserEnvVar(var,value):
    """ function to create a user environment variable permanently """
    logger = logging.getLogger(__name__)
    # user variables are stored in HKEY_CURRENT_USER\Environment
    try :
        import _winreg
        root = _winreg.HKEY_CURRENT_USER
        subkey  =r'Environment'
        h = _winreg.OpenKey(root,subkey,0,_winreg.KEY_ALL_ACCESS)
        _winreg.SetValueEx(h,var,0,_winreg.REG_SZ,value)
        _winreg.CloseKey(h)
        logger.info('setting environment variable %s to %s'%(var,value))
    except Exception, er:
        logger.error('problem while setting environment variable %s to %s'%(var,value), exc_info=True)		

        
def createDevEnvVar(proj=True):
    from manageEnv import createUserEnvVar
    for k,v in EnvVars.iteritems():
        createUserEnvVar(k,v)
    if proj:
        from projects import MyProjects
        for p in MyProjects:
            createUserEnvVar(p.get_env(),p.getPath())
