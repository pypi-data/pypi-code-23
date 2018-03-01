'''
example for reading report file
[section1]
option1:1.2
option2:3

'''
import ConfigParser
import os
import pySAXS
rpt=ConfigParser.ConfigParser()
testfile=os.path.dirname(pySAXS.__file__)+os.sep+"saxsdata"+os.sep+"testrpt.txt"
test=rpt.read(testfile)
if len(test)==0:
    print 'error when reading file :', testfile

print rpt.sections()  #print the list of all the sections
expName=rpt.get('experiment','name') #get the option in the specified section
print "Experiment name is : ",expName
print rpt.options('experiment')
print "Average is ",rpt.get('acquisition','average')
print rpt.get('acquisition','exposure time')


    
