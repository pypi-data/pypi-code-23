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

hits_to_get						= 5000

defaults						= {
									"query":	"blue",
									"view":		"brief",
									"rpp":		100,
									#"rpp":		20,
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
									["hl", "n"],
									["exp", ["fulltext"]],
									["exp", ["relatedsubjects"]],
									["lim", ["LA99:English"]],
									["lim", ["FT:Y"]],
									["lim", ["RV:Y"]],
									["lim", ["FT:Y", "RV:Y"]],
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

	for trial in range(1, 6):
		s							= Session()
		sys.stdout.write("Trial number %d ... " % trial)

		hits					= 0
		success					= True
	
		for page in range(1, int(hits_to_get/settings["rpp"]) + 1):
		
			if page == 1:
				r				= s.search(settings["query"], view=settings["view"], rpp=settings["rpp"], highlight=settings["hl"], expanders=settings["exp"], limiters=settings["lim"])
			else:
				r				= s.next_page()
			
			if not r:
				print "Error on page %d / hit %d!" % (page, hits + 1)
				success			= False
				break

			hits				= hits + settings["rpp"]
			if settings["sleep"] > 0:
				time.sleep(settings["sleep"])
		else:
			print "Successfully got %d pages / %d hits!" % (page, hits)
		# End of page loop

		s.end()
	# End of trial loop
# End of case loop
	
print "-------------------"
# EOF
