#!/usr/bin/python3
# -*- encoding: utf-8 -*-
import requests
import time
import os
import sys
import logging
import xmltodict

from .trains import Trains


class stations(Trains):
    """
        class for fetching and parsing NS train stations data
    """
    def getData(self):
        try:
            #fetch the elements from the NS API
            url = "http://webservices.ns.nl/ns-api-stations-v2"
            root = self.goFetch(url)
            
            #parse elements into dict
            elements = xmltodict.parse(root, dict_constructor=dict)
            
            if elements['Stations'] is not None:
                return elements['Stations'] 
            else:
                return False
            
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(str(e) + " | " + str(exc_type) + " | " + str(fname) + " | " + str(exc_tb.tb_lineno)) 