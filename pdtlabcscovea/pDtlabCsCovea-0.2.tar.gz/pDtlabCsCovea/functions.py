#!/usr/bin/python2.7
#-*- coding: utf-8 -*-

from datetime import datetime
import git  
import re
import os

# Cette fonction affiche un message à l'écran 
def print_coucou():
    print( "Bonjour le monde !" )

# Cette fonction affiche la date et l'heure  
def la_date():
    print( "{}".format( datetime.now() ))
