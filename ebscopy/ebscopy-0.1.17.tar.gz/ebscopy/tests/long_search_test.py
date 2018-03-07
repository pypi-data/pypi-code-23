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

#q = 'TI ( (Caribbean or "Antigua and Barbuda" or Aruba or Barbados or Cuba or Dominica or "Dominican Republic" or Grenada or Haiti or Jamaica or "Puerto Rico" or "St. Kitts and Nevis" or "Saint Kitts and Nevis" or "St. Lucia" or "Saint Lucia" or "St. Vincent and the Grenadines" or "Saint Vincent and the Grenadines" or "St. Vincent" or "Saint Vincent" or "Trinidad and Tobago") ) OR AB ( (Caribbean or "Antigua and Barbuda" or Aruba or Barbados or Cuba or Dominica or "Dominican Republic" or Grenada or Haiti or Jamaica or "Puerto Rico" or "St. Kitts and Nevis" or "Saint Kitts and Nevis" or "St. Lucia" or "Saint Lucia" or "St. Vincent and the Grenadines" or "Saint Vincent and the Grenadines" or "St. Vincent" or "Saint Vincent" or "Trinidad and Tobago") ) OR SU ( (Caribbean or "Antigua and Barbuda" or Aruba or Barbados or Cuba or Dominica or "Dominican Republic" or Grenada or Haiti or Jamaica or "Puerto Rico" or "St. Kitts and Nevis" or "Saint Kitts and Nevis" or "St. Lucia" or "Saint Lucia" or "St. Vincent and the Grenadines" or "Saint Vincent and the Grenadines" or "St. Vincent" or "Saint Vincent" or "Trinidad and Tobago") )'
q = '((TI ( (Afghanistan or Azerbaijan or Bangladesh or Bhutan or Burma or Cambodia or China or Georgia or India or Iran or Iraq or Jordan or Kazakhstan or Korea or "Kyrgyz Republic" or Kyrgyzstan or Lao or Laos or Lebanon or Macao or Mongolia or Myanmar or Nepal or Oman or Pakistan or Russia or "Russian Federation" or "Saudi Arabia" or Bahrain or Indonesia or Malaysia or Philippines or Sri Lanka or Syria or "Syrian Arab Republic" or Tajikistan or Thailand or Timor-Leste or Timor or Turkey or Turkmenistan or Uzbekistan or Vietnam or "West Bank" or Gaza or Yemen or Comoros or Maldives or Mauritius) ) OR AB ( (Afghanistan or Azerbaijan or Bangladesh or Bhutan or Burma or Cambodia or China or Georgia or India or Iran or Iraq or Jordan or Kazakhstan or Korea or "Kyrgyz Republic" or Kyrgyzstan or Lao or Laos or Lebanon or Macao or Mongolia or Myanmar or Nepal or Oman or Pakistan or Russia or "Russian Federation" or "Saudi Arabia" or Bahrain or Indonesia or Malaysia or Philippines or Sri Lanka or Syria or "Syrian Arab Republic" or Tajikistan or Thailand or Timor-Leste or Timor or Turkey or Turkmenistan or Uzbekistan or Vietnam or "West Bank" or Gaza or Yemen or Comoros or Maldives or Mauritius) ) OR SU ( (Afghanistan or Azerbaijan or Bangladesh or Bhutan or Burma or Cambodia or China or Georgia or India or Iran or Iraq or Jordan or Kazakhstan or Korea or "Kyrgyz Republic" or Kyrgyzstan or Lao or Laos or Lebanon or Macao or Mongolia or Myanmar or Nepal or Oman or Pakistan or Russia or "Russian Federation" or "Saudi Arabia" or Bahrain or Indonesia or Malaysia or Philippines or Sri Lanka or Syria or "Syrian Arab Republic" or Tajikistan or Thailand or Timor-Leste or Timor or Turkey or Turkmenistan or Uzbekistan or Vietnam or "West Bank" or Gaza or Yemen or Comoros or Maldives or Mauritius) ) OR TI ( ("Pacific Islands" or "American Samoa" or Fiji or Guam or Kiribati or "Marshall Islands" or Micronesia or "New Caledonia" or "Northern Mariana Islands" or Palau or "Papua New Guinea" or Samoa or "Solomon Islands" or Tonga or Tuvalu or Vanuatu) ) OR AB ( ("Pacific Islands" or "American Samoa" or Fiji or Guam or Kiribati or "Marshall Islands" or Micronesia or "New Caledonia" or "Northern Mariana Islands" or Palau or "Papua New Guinea" or Samoa or "Solomon Islands" or Tonga or Tuvalu or Vanuatu) ) OR SU ( ("Pacific Islands" or "American Samoa" or Fiji or Guam or Kiribati or "Marshall Islands" or Micronesia or "New Caledonia" or "Northern Mariana Islands" or Palau or "Papua New Guinea" or Samoa or "Solomon Islands" or Tonga or Tuvalu or Vanuatu) ) OR TI ( ("Eastern Europe" or Balkans or Albania or Armenia or Belarus or Bosnia or Herzegovina or Bulgaria or Croatia or Cyprus or "Czech Republic" or Estonia or Greece or Hungary or "Isle of Man" or Kosovo or Latvia or Lithuania or Macedonia or Malta or Moldova or Montenegro or Poland or Portugal or Romania or Serbia or "Slovak Republic" or Slovakia or Slovenia or Ukraine) ) OR AB ( ("Eastern Europe" or Balkans or Albania or Armenia or Belarus or Bosnia or Herzegovina or Bulgaria or Croatia or Cyprus or "Czech Republic" or Estonia or Greece or Hungary or "Isle of Man" or Kosovo or Latvia or Lithuania or Macedonia or Malta or Moldova or Montenegro or Poland or Portugal or Romania or Serbia or "Slovak Republic" or Slovakia or Slovenia or Ukraine) ) OR SU ( ("Eastern Europe" or Balkans or Albania or Armenia or Belarus or Bosnia or Herzegovina or Bulgaria or Croatia or Cyprus or "Czech Republic" or Estonia or Greece or Hungary or "Isle of Man" or Kosovo or Latvia or Lithuania or Macedonia or Malta or Moldova or Montenegro or Poland or Portugal or Romania or Serbia or "Slovak Republic" or Slovakia or Slovenia or Ukraine) ) OR TI ( (Caribbean or "Antigua and Barbuda" or Aruba or Barbados or Cuba or Dominica or "Dominican Republic" or Grenada or Haiti or Jamaica or "Puerto Rico" or "St. Kitts and Nevis" or "Saint Kitts and Nevis" or "St. Lucia" or "Saint Lucia" or "St. Vincent and the Grenadines" or "Saint Vincent and the Grenadines" or "St. Vincent" or "Saint Vincent" or "Trinidad and Tobago") ) OR AB ( (Caribbean or "Antigua and Barbuda" or Aruba or Barbados or Cuba or Dominica or "Dominican Republic" or Grenada or Haiti or Jamaica or "Puerto Rico" or "St. Kitts and Nevis" or "Saint Kitts and Nevis" or "St. Lucia" or "Saint Lucia" or "St. Vincent and the Grenadines" or "Saint Vincent and the Grenadines" or "St. Vincent" or "Saint Vincent" or "Trinidad and Tobago") ) OR SU ( (Caribbean or "Antigua and Barbuda" or Aruba or Barbados or Cuba or Dominica or "Dominican Republic" or Grenada or Haiti or Jamaica or "Puerto Rico" or "St. Kitts and Nevis" or "Saint Kitts and Nevis" or "St. Lucia" or "Saint Lucia" or "St. Vincent and the Grenadines" or "Saint Vincent and the Grenadines" or "St. Vincent" or "Saint Vincent" or "Trinidad and Tobago") ) OR TI ( ("South America" or "Latin America" or "Central America" or Argentina or Belize or Bolivia or Brazil or Chile or Colombia or "Costa Rica" or Ecuador or "El Salvador" or Guatemala or Guyana or Honduras or Mexico or Nicaragua or Panama or Paraguay or Peru or Suriname or Uruguay or Venezuela) ) OR AB ( ("South America" or "Latin America" or "Central America" or Argentina or Belize or Bolivia or Brazil or Chile or Colombia or "Costa Rica" or Ecuador or "El Salvador" or Guatemala or Guyana or Honduras or Mexico or Nicaragua or Panama or Paraguay or Peru or Suriname or Uruguay or Venezuela) ) OR SU ( ("South America" or "Latin America" or "Central America" or Argentina or Belize or Bolivia or Brazil or Chile or Colombia or "Costa Rica" or Ecuador or "El Salvador" or Guatemala or Guyana or Honduras or Mexico or Nicaragua or Panama or Paraguay or Peru or Suriname or Uruguay or Venezuela) ) OR TI ( (Africa or "sub Saharan Africa" or "North Africa" or "West Africa" or "East Africa" or Algeria or Angola or Benin or Botswana or Burkina Faso or Burundi or Cameroon or "Cape Verde" or "Cabo Verde" or "Central African Republic" or Chad or "Democratic Republic of the Congo" or "Republic of the Congo" or Congo or "Cote dIvoire" or "Ivory Coast" or Djibouti or Egypt or "Equatorial Guinea" or Eritrea or Ethiopia or Gabon or Gambia or Ghana or Guinea or Guinea-Bissau or Kenya or Lesotho or Liberia or Libya or Madagascar or Malawi or Mali or Mauritania or Morocco or Mozambique or Namibia or Niger or Nigeria or Rwanda or "Sao Tome" or Principe or Senegal or Seychelles or "Sierra Leone" or Somalia or Somaliland or "South Africa" or "South Sudan" or Sudan or Swaziland or Tanzania or Togo or Tunisia or Uganda or Zambia or Zimbabwe) ) OR AB ( (Africa or "sub Saharan Africa" or "North Africa" or "West Africa" or "East Africa" or Algeria or Angola or Benin or Botswana or Burkina Faso or Burundi or Cameroon or "Cape Verde" or "Cabo Verde" or "Central African Republic" or Chad or "Democratic Republic of the Congo" or "Republic of the Congo" or Congo or "Cote dIvoire" or "Ivory Coast" or Djibouti or Egypt or "Equatorial Guinea" or Eritrea or Ethiopia or Gabon or Gambia or Ghana or Guinea or Guinea-Bissau or Kenya or Lesotho or Liberia or Libya or Madagascar or Malawi or Mali or Mauritania or Morocco or Mozambique or Namibia or Niger or Nigeria or Rwanda or "Sao Tome" or Principe or Senegal or Seychelles or "Sierra Leone" or Somalia or Somaliland or "South Africa" or "South Sudan" or Sudan or Swaziland or Tanzania or Togo or Tunisia or Uganda or Zambia or Zimbabwe) ) OR SU ( (Africa or "sub Saharan Africa" or "North Africa" or "West Africa" or "East Africa" or Algeria or Angola or Benin or Botswana or Burkina Faso or Burundi or Cameroon or "Cape Verde" or "Cabo Verde" or "Central African Republic" or Chad or "Democratic Republic of the Congo" or "Republic of the Congo" or Congo or "Cote dIvoire" or "Ivory Coast" or Djibouti or Egypt or "Equatorial Guinea" or Eritrea or Ethiopia or Gabon or Gambia or Ghana or Guinea or Guinea-Bissau or Kenya or Lesotho or Liberia or Libya or Madagascar or Malawi or Mali or Mauritania or Morocco or Mozambique or Namibia or Niger or Nigeria or Rwanda or "Sao Tome" or Principe or Senegal or Seychelles or "Sierra Leone" or Somalia or Somaliland or "South Africa" or "South Sudan" or Sudan or Swaziland or Tanzania or Togo or Tunisia or Uganda or Zambia or Zimbabwe) )) AND ((TI ( (program* or intervention* or project or projects or initiative or policy or policies) ) OR AB ( (program* or intervention* or project or projects or initiative or policy or policies) ) OR SU ( (program* or intervention* or project or projects or initiative or policy or policies) ) AND (TI ( ("program* evaluation" OR "project evaluation" OR "evaluation research" OR ("natural experiment*")) ) OR SU ( ("program* evaluation" OR "project evaluation" OR "evaluation research" OR ("natural experiment*")) ) OR AB ( ("program* evaluation" OR "project evaluation" OR "evaluation research" OR ("natural experiment*")) ) OR TI ( (effect* N2 (evaluati* or assess* or analy* or estimat*)) ) OR SU ( (effect* N2 (evaluati* or assess* or analy* or estimat*)) ) OR AB ( (effect* N2 (evaluati* or assess* or analy* or estimat*)) ) OR TI ( (impact N2 (evaluati* or assess* or analy* or estimat*)) ) OR SU ( (impact N2 (evaluati* or assess* or analy* or estimat*)) ) OR AB ( (impact N2 (evaluati* or assess* or analy* or estimat*)) ) )) OR (TI ( (program* or intervention* or project or projects or initiative or policy or policies) ) OR AB ( (program* or intervention* or project or projects or initiative or policy or policies) ) OR SU ( (program* or intervention* or project or projects or initiative or policy or policies) ) AND (TI ( ((match* N2 (propensity or coarsened or covariate or score or neighbo#r)) or (propensity score) or (nearest neighbo#r) or ("difference in difference*" or "difference-in-difference*" or "differences in difference*" or "differences-in-difference*" or "double difference*") or (quasi-experiment* or quasi experiment*) (instrumental variable*) or (IV W2 (estimation or approach)) or (regression discontinuity) or ((estimator or counterfactual) and evaluation*)) ) OR SU ( ((match* N2 (propensity or coarsened or covariate or score or neighbo#r)) or (propensity score) or (nearest neighbo#r) or ("difference in difference*" or "difference-in-difference*" or "differences in difference*" or "differences-in-difference*" or "double difference*") or (quasi-experiment* or quasi experiment*) (instrumental variable*) or (IV W2 (estimation or approach)) or (regression discontinuity) or ((estimator or counterfactual) and evaluation*)) ) OR AB ( ((match* N2 (propensity or coarsened or covariate or score or neighbo#r)) or (propensity score) or (nearest neighbo#r) or ("difference in difference*" or "difference-in-difference*" or "differences in difference*" or "differences-in-difference*" or "double difference*") or (quasi-experiment* or quasi experiment*) (instrumental variable*) or (IV W2 (estimation or approach)) or (regression discontinuity) or ((estimator or counterfactual) and evaluation*)) ) OR TI ( (experiment* N2 (design or study or research or evaluation or evidence)) or ((random or randomi#ed) N2 (trial or assignment or treatment or control*)) ) OR SU ( (experiment* N2 (design or study or research or evaluation or evidence)) or ((random or randomi#ed) N2 (trial or assignment or treatment or control*)) ) OR AB ( (experiment* N2 (design or study or research or evaluation or evidence)) or ((random or randomi#ed) N2 (trial or assignment or treatment or control*)) )))))'




defaults						= {
									"query":	q,
									"mode":		"bool",
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
									#["view", "detailed"],
									#["rpp", 50],
									#["rpp", 100],
									#["hl", "n"],
									##["exp", ["fulltext"]],
									#["exp", ["relatedsubjects"]],
									#["lim", ["LA99:English"]],
									#["lim", ["FT:Y"]],
									#["lim", ["RV:Y"]],
									#["lim", ["FT:Y", "RV:Y"]],
									#["sleep", 2],
									#["sleep", 5],
								  ]


for case in test_cases:
	print "-------------------"
	print "Test Case: %s is %s" % (case[0], case[1])

	settings					= copy.deepcopy(defaults)
	settings[case[0]]			= case[1]

	print "------"
	print settings
	print "------"
	print "Length of query: %d" % len(q)

	for trial in range(1, 2):
		s							= Session()
		sys.stdout.write("Trial number %d ... " % trial)

		hits					= 0
		success					= True
	
		for page in range(1, int(hits_to_get/settings["rpp"]) + 1):
		
			if page == 1:
				r				= s.search(settings["query"], mode=settings["mode"], view=settings["view"], rpp=settings["rpp"], highlight=settings["hl"], expanders=settings["exp"], limiters=settings["lim"])
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
