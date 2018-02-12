#!/usr/bin/python2.7
#-*- coding: utf-8 -*-

from datetime import datetime
from git import Git, Repo 
from git import *
from gitdb import *
import pexpect
import sys
import os
import re

os.system("export http_proxy=proxy=http://user:pw@192.168.238.3:80") 
# Cette fonction affiche un message à l'écran 
def print_coucou():
    print( "Bonjour le monde !" )

# Cette fonction affiche la date et l'heure  
def la_date():
    print( "{}".format( datetime.now() ))

