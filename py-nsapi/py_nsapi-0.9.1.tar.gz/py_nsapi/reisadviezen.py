#!/usr/bin/python3
# -*- encoding: utf-8 -*-
import requests
import sys
import time
import os
import logging
import xmltodict

from .trains import Trains


class reisadviezen(Trains):
    """
        class for fetching and parsing NS train advice data
    """    

    def getData(self, fromStation=None, toStation=None, viaStation="", previousAdvices=2,nextAdvices=3,dateTime="",Departure="true",hslAllowed="true",yearCArd="false"):
        try:
            """
            Let op: bij unplanned=true worden de geplande werkzaamheden geretourneerd. 
            Dit is dus net andersom dan wat de parameternaam doet vermoeden.
            """            
            if fromStation is None or toStation is None:
                raise Exception("You have to put in a From Station and To Station")
            
            url = "http://webservices.ns.nl/ns-api-treinplanner?fromStation={}&toStation={}&viaStation={}&previousAdvices={}&nextAdvices={}&dateTime={}&Departure={}&hslAllowed={}&yearCArd={}"
            url = url.format(fromStation,toStation,viaStation,previousAdvices,nextAdvices,dateTime,str(Departure).lower(),str(hslAllowed).lower(),str(yearCArd).lower())

            #fetch the elements from the NS API
            root = self.goFetch(url)
            
            #parse elements into dict
            elements = xmltodict.parse(root, dict_constructor=dict)
            
            if elements['ReisMogelijkheden'] is not None:
                return elements['ReisMogelijkheden'] 
            else:
                return False
            
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(str(e) + " | " + str(exc_type) + " | " + str(fname) + " | " + str(exc_tb.tb_lineno)) 