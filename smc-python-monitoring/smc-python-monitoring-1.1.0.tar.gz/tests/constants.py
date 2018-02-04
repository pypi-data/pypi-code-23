'''
Created on Sep 26, 2017

@author: davidlepage
'''
from distutils.version import LooseVersion
from smc.administration.system import System

url = 'http://172.18.1.26:8082'
api_key = 'kKphtsbQKjjfHR7amodA0001'


def version_equal_to_or_greater(version):
    system = System()
    SMC_VERSION = system.smc_version.split(' ')[0]
    if LooseVersion(SMC_VERSION) >= LooseVersion(version):
        return True
    return False