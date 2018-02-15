#!/usr/bin/env python2.7

'''
FUNCTION: Export 10 samples from Production Google Cloud Storage.


NOTES:
    - Needs to run in the home directory. 
'''


import sys
sys.path.append("scripts")
import web_module_to_load as WMTL

fileName = "tmp/datastore_samples.txt"

query = WMTL.SearchResult.query(WMTL.SearchResult.urlsTabbed != "NA")
fileOUT = open(fileName, "w")
#Get at most 10 values. 
match = query.fetch(10)
for i in match:
    outString = i.keyName + "\t" + i.locationTabbed.rstrip() + "\t" + i.urlsTabbed.rstrip() + "\n"
    fileOUT.write(outString)
fileOUT.close()
