#!/usr/bin/python

import os
import shutil
import argparse
import sys

parser = argparse.ArgumentParser(description="Create a new Senscape project for Code Composer")
parser.add_argument('name', nargs=1, help="Name of the project that will be created")
script_path = os.path.dirname(os.path.abspath(__file__))
if (not os.path.exists(script_path + "/skel")):
    script_path = sys.exec_prefix + "sensproject/"
cwd = os.getcwd()

def main():
    args = parser.parse_args()
    name = args.name[0]
    print "Creating the project %s in a new folder..." % (name)
    shutil.copytree("%s/skel" % (script_path), "%s/%s" % (cwd, name))
    os.rename("%s/%s/leproject.cpp" % (cwd, name), "%s/%s/%s.cpp" % (cwd, name, name))
    projectFile(name)
    cprojectFile(name)
    print "Done!"

def projectFile(name):
    pFile = open("%s/%s/.project"  % (cwd, name), "r")
    lines = pFile.readlines()
    pFile.close()
    pFile = open("%s/%s/.project"  % (cwd, name), "w")
    for line in lines:
        if "<name>leproject</name>" in line:
            line = 	"<name>%s</name>\n" % (name)
        pFile.writelines(line)
        
    

def cprojectFile(name):
    pFile = open("%s/%s/.cproject"  % (cwd, name), "r")
    lines = pFile.readlines()
    pFile.close()
    pFile = open("%s/%s/.cproject"  % (cwd, name), "w")
    for line in lines:
        if "<project id=" in line:
            line = 	"		<project id=\"%s.com.ti.ccstudio.buildDefinitions.MSP430.ProjectType.355125497\" name=\"MSP430\" projectType=\"com.ti.ccstudio.buildDefinitions.MSP430.ProjectType\"/>\n" % (name)
        pFile.writelines(line)

if __name__ == "__main__":
    main()