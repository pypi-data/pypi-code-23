"""Class that handles the interaction with the CentraXX
REST API and XML import"""

import requests

class CXXConnectException(Exception):
    """Exception class for raising CentraXX connection
    related exceptions"""

class CXXConnect():

    def __init__(self, authuser, password, **kwargs):
        self._authuser = authuser
        self._password = password
        self._infopath = kwargs['infopath'] if 'infopath' in kwargs else ""
    
    def check(self):
        """Access the info path of CentraXX's API"""
        print('Trying to connect to CentraXX server...')
        print(self._infopath)
        response = requests.get(self._infopath, verify=False, timeout=5)
        return response

