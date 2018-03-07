#!/usr/bin/python
#
# Test suite for API Bugs
#

from ebscopy import *
#import unittest
from requests import HTTPError
import os
import re
import time
from datetime import datetime
import sys
import copy

#    def search(self, query, mode="all", sort="relevance", view="brief", rpp=20, page=1, highlight="y", suggest="n", expanders=[], limiters=[]):

defaults						= {
									"query":	"volcano",
									"view":		"brief",
									"rpp":		20,
									"hl":		"y",
									"exp":		[],
									"lim":		[],
									"sleep":	0,
								  }


test_cases						= [
									["default", "default"],
									["view", "detailed"],
									["rpp", 50],
									["rpp", 100],
									["sleep", 2],
									["sleep", 5],
								  ]


for case in test_cases:
	print "-------------------"
	print "Test Case: %s is %s" % (case[0], case[1])

	settings					= copy.deepcopy(defaults)
	settings[case[0]]			= case[1]

	print "------"
	print settings
	print "------"

	for trial in range(1, 20):
		s							= Session()
		sys.stdout.write("Trial number %d ... " % trial)
		success					= True
		i						= s._request("Info", {})
		r						= s.search(settings["query"], view=settings["view"], rpp=settings["rpp"], highlight=settings["hl"], expanders=settings["exp"], limiters=settings["lim"])
			
		if not r:
			print "Error!"
			success			= False
			break
		else:
			print "Success!"
		# End of page loop

		s.end()
	# End of trial loop
# End of case loop
	
print "-------------------"
# EOF
