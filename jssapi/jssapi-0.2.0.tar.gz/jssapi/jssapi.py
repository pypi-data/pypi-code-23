# -*- coding: utf-8 -*-

"""Main JSSApi module."""

import requests
import sys

from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session

from .decorators import alias, aliased

try:
    from urllib import quote  # Python 2.X
except ImportError:
    from urllib.parse import quote  # Python 3+

try:
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
except ImportError:
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)



@aliased
class JSSApi:
    @alias('retrieve','find')
    def get(self, method='mobiledevices'):
        """ Interact with GET methods of JSS API"""
        self.head = {"Accept": "application/json"}
        try :
            self.r = requests.get(url=(self.url + method), headers=self.head, auth=self.auth)
            if self.r.status_code != 200 :
                pass
            json = self.r.json()
            return next(iter(json.values()))
        except :
            self.e = sys.exc_info()[0]
            pass
        return []

    @alias('insert','new','create')
    def post(self, method='mobiledevices', body=''):
        """ Interact with POST methods of JSS API"""
        self.head = {"Content-Type": "text/xml"}
        self.r=requests.post(url=(self.url + method), headers=self.head, data=body, auth=self.auth)
        return self.r.text

    @alias('update','edit','change','modify')
    def put(self, method='mobiledevices', body=''):
        """ Interact with PUT methods of JSS API"""
        self.head = {"Content-Type": "text/xml"}
        self.r=requests.put(url=(self.url + method), headers=self.head, data=body, auth=self.auth)
        return self.r.text

    @alias('remove')
    def delete(self, method='mobiledevices'):
        """ Interact with DELETE methods of JSS API"""
        self.r=requests.delete(url=(self.url + method), headers=self.head, auth=self.auth)
        return self.r.text

    def set_auth(self, user='',pwd=''):
        """ Provide login credentials"""
        self.auth = requests.auth.HTTPBasicAuth(user, pwd)

    def set_db(self,
               host=None, db='', user='', passwd='',
               ):
        """
        Provide DB credentials if you want to directly interact with MySQL DB
        """
        if host != None:
            self.Base = automap_base()
            self.engine = create_engine('mysql+pymysql://' + user + ':' + passwd + '@' + host + '/' + db)
            self.Base.prepare(self.engine, reflect=True)

    def __init__(self,
                 url='',
                 head={"Accept": "application/json"},
                 user='', pwd='',
                 dbhost='', db='', dbuser='', dbpasswd='',
                 ):
        self.url = url + '/JSSResource/'
        self.head = head
        self.auth = requests.auth.HTTPBasicAuth(user, pwd)
        self.r = requests.Response
        self.e = sys.exc_info()[0]

        if dbhost != None:
            self.set_db(host=dbhost,db=db,user=dbuser,passwd=dbpasswd)
        else:
            self.engine = None
