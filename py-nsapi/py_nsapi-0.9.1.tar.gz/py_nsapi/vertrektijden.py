#!/usr/bin/python
# -*- encoding: utf-8 -*-
import requests
import sys
import time
import os
import logging
import xmltodict
from .trains import Trains
        
class vertrektijden(Trains):
    """
        class for fetching and parsing NS train departure data
    """    
    def getData(self, station=None):
        try:
            if self.isNotEmpty(station):
                #fetch the elements from the NS API
                url = "https://webservices.ns.nl/ns-api-avt?station={}".format(station)
                root = self.goFetch(url)
            
                #parse elements into dict
                elements =  xmltodict.parse(root, dict_constructor=dict)
                
                if elements['ActueleVertrekTijden'] is not None:
                    return elements['ActueleVertrekTijden'] 
                else:
                    return False
                
            else:
                raise Exception("You should use a station")
      
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(str(e) + " | " + str(exc_type) + " | " + str(fname) + " | " + str(exc_tb.tb_lineno)) 