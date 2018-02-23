import requests
import json
import logging
import requests
import time
import sys
import os

class domainAvailability:

    def __init__(self, usr=None, pwd=None):
        try:
            
            if usr is None:
                raise Exception("No User name!")
                
            if pwd is None: 
                raise Exception("No User password!")
            
            self.usr = usr
            self.pwd = pwd
            
            self.url = "https://www.whoisxmlapi.com/whoisserver/WhoisService?"\
                        "cmd=GET_DN_AVAILABILITY&domainName={}&username={}&"\
                        "password={}&getMode=DNS_AND_WHOIS&outputFormat=JSON"
            
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(str(e) + " | " + str(exc_type) + " | " + str(fname) + " | " + str(exc_tb.tb_lineno)) 


    def get_url(self, url=None):
        try:
            if url is None:
                raise Exception("No Url!")
            
            r = requests.get(url, timeout=1)
            if r.status_code == 200:
                content = r.content.decode("utf8")
                return content
            else:
                raise Exception("Error getting URL : "+ str(r.status_code))
            
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(str(e) + " | " + str(exc_type) + " | " + str(fname) + " | " + str(exc_tb.tb_lineno)) 
            return False

    def get_json(self, url=None):
        try:
            if url is None:
                raise Exception("No Url!")
            
            content = self.get_url(url)
            
            if content is None or content == "" or content is False:
                raise Exception("No content!")
            
            js = json.loads(content)
            return js

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(str(e) + " | " + str(exc_type) + " | " + str(fname) + " | " + str(exc_tb.tb_lineno)) 
    
    
    def getData(self, domain):
        try:
            
            url = self.url.format(domain, self.usr, self.pwd)
            
            data = self.get_json(url)
            
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(str(e) + " | " + str(exc_type) + " | " + str(fname) + " | " + str(exc_tb.tb_lineno)) 

        try:
            data = data['DomainInfo']
            return data['domainAvailability']
        except KeyError:
            return "Unknown"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(str(e) + " | " + str(exc_type) + " | " + str(fname) + " | " + str(exc_tb.tb_lineno))             