#!/usr/bin/python
import os, socket, time, datetime
import sys, getopt

from config import *
#debug = False

###################################################
#
# useful utils
#
###################################################
def debug_on ():
	global debug
	debug = True

def debug_off ():
	global debug
	debug = False
	
def trace(msg):
	global debug
	if debug:
		print msg

def error(msg):
	print 'Error: ' + msg

