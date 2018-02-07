#!/usr/bin/python
# Copyright (c)2012 EMC Corporation
# All Rights Reserved

# This software contains the intellectual property of EMC Corporation
# or is licensed to EMC Corporation from third parties.  Use of this
# software and the intellectual property contained therein is expressly
# limited to the terms and conditions of the License Agreement under which
# it is provided by or on behalf of EMC.

import json
import common
import glob
import os
import sys
from sys import version_info
from common import SOSError
from common import getToken
from os.path import expanduser


from common import SOSError
#from ecsclient.client import Client



####################################################
#
####################################################
'''
def get_client():
    theToken = getToken()
    print('theToken: ' + theToken)
    cfgDict = getConfigDict()
    ep = 'https://' + cfgDict[Config.HOSTNAME] + ':' + cfgDict[Config.PORT]

    print('using endpoint: ' + ep)
    client = Client('3',
                    token=theToken,
                    ecs_endpoint=ep)
    return client
'''

####################################################
#
####################################################
def get_profile_version():
    c = Config()
    cfgDict = getConfigDict()

    #there is no current config because no configs exist yet
    if cfgDict.has_key(Config.VERS) == False:
        cfgDict[Config.VERS] = Config.DEFAULT_VERS

    return cfgDict[Config.VERS]
 

class Config(object):
    CONFIG_BASE_NAME      = "ecscliconfig_"
    CONFIG_PATH           = expanduser("~")
    CONFIG_BASE_NAME_PATH = CONFIG_PATH + "/" + CONFIG_BASE_NAME
    CONFIG_CURRENT        = '' #to be filled in on init()
    CONFIG_CURRENT_FILE   = CONFIG_PATH + "/." + CONFIG_BASE_NAME + ".json" # the dot name stops collision with the configs list
    CONFIG_DICT = {}

    HOSTNAME = "hostname"
    PORT = "port"
    USER = "user"
    VERS = "ecsversion"
    DEFAULT_VERS = 3.0
    ALLOWED_VERS = [2.2, 3.0, 3.1, 3.2]
    COOKIEDIR = "cookiedir" #defaults to Config.CONFIG_PATH + '/' + args.profile where args.profile is the name of the config

    def __init__(self):
        loadCurrentConfig();
        return


##################################################################
# convenience method not sure if it will be used
##################################################################
def getActiveConfigName():
    return Config.CONFIG_CURRENT

##################################################################
#
##################################################################
def loadConfig(profileName):
    profileFile = Config.CONFIG_BASE_NAME_PATH + profileName + "_.json"
    in_file = open(profileFile,"r")
    result = json.load(in_file)
    in_file.close()

    #This is here in case users have already created profiles that don't have the version field
    if result.has_key(Config.VERS) == False:
       result[Config.VERS] = Config.DEFAULT_VERS

    return result

##################################################################
# internally used to load these default values for other cli commands
##################################################################
def getConfigDict():
    return Config.CONFIG_DICT

##################################################################
# internally used to load these default values for other cli commands
##################################################################
def loadCurrentConfig():
    #print("JMC Entered loadCurrentConfig")
    #print("Config.CONFIG_CURRENT_FILE = " + Config.CONFIG_CURRENT_FILE)
    if os.path.exists(Config.CONFIG_CURRENT_FILE) == False:
        return None

    in_file = open(Config.CONFIG_CURRENT_FILE,"r")
    result = json.load(in_file)
    Config.CONFIG_CURRENT = result['current']
    in_file.close()

    in_file = open(Config.CONFIG_CURRENT,"r")
    result = json.load(in_file)
    in_file.close()

    #This is here in case users have already created profiles that don't have the version field
    if result.has_key(Config.VERS) == False:
       result[Config.VERS] = Config.DEFAULT_VERS
    Config.CONFIG_DICT = result
    return result


##################################################################
# 
##################################################################
def saveConfig(data , profileName):
    print("Entered saveConfig profileName = " + profileName)
    if ("_" in profileName):
        print("Profile names are NOT allowed to contain underscore characters.\n This profile will NOT be saved.\n\n")
        return

    print("will be saved to base path: " + Config.CONFIG_BASE_NAME_PATH)
    profileFile = Config.CONFIG_BASE_NAME_PATH + profileName + "_.json"
    print("Saving profile config to: " + profileFile)
    out_file = open(profileFile,"w")
    json.dump(data, out_file, indent=4)
    out_file.close()
    try:
        out_file = open(Config.CONFIG_CURRENT_FILE,"w")
        result = {'current': profileFile}
        json.dump(result, out_file, indent=4)
        out_file.close()
        Config.CONFIG_CURRENT = profileFile
    except:
        print('exception thrown in saveConfig')
    return

##################################################################
#
##################################################################
def promptUser(promptStr):
    py3 = version_info[0] > 2 #creates boolean value for test that Python major version > 2
    if py3:
        response = input(promptStr)
    else:
        response = raw_input(promptStr)
    return response

##################################################################
#
##################################################################
def configFileFromName(profileName):
    return Config.CONFIG_BASE_NAME_PATH + profileName + "_.json"

##################################################################
# deprecated and
# not currently used
##################################################################
def isProfileCurrent(profileName):
    status = False
    profileFile = configFileFromName(profileName)

    if os.path.exists(Config.CONFIG_CURRENT):
        if (os.readlink(Config.CONFIG_CURRENT) == profileFile):
            status = True
    return status
    



########################################################
#
# parser commands section
#
#########################################################
def cli_config_del_parser(subcommand_parsers):
    # create namespace command parser
    cli_config_del_parser = subcommand_parsers.add_parser(
        'delete',
        description='deletes a saved configuration profile from the profile list',
        conflict_handler='resolve',
        help='del a cli profile')

    cli_config_del_parser.add_argument(
        '-pf', '-profile',
        help='the name of the profile whose values will be the host, username, cookiefile and port',
        dest='profile',
        required=True)

    cli_config_del_parser.set_defaults(func=deleteProfile)

##################################################################
#
##################################################################
def deleteProfile(args):
    print "Entered deleteProfile"
    currentRemoved = False
    profileFile = configFileFromName(args.profile)
   
    #check on the current profile sym link and remove it if it points to this one
    if (Config.CONFIG_CURRENT == profileFile):
        Config.CONFIG_CURRENT = ''
        currentRemoved = True

    #delete the json config file with this profile name
    os.remove(profileFile)

    # if there are any current configs left and the current config was the one that was removed
    # then update current config to the first one in the list of configs
    configArr = glob.glob(Config.CONFIG_BASE_NAME_PATH + '*')
    if (currentRemoved == True):
        if (len(configArr)>0 ):
            updateCurrentProfileFile(configArr[0])
        else:
            os.remove(Config.CONFIG_CURRENT_FILE)
            Config.CONFIG_CURRENT = ''

    listConfigs()
    return


##################################################################
#
##################################################################
def cli_config_list_parser(subcommand_parsers):
    # create namespace command parser
    cli_config_list_parser = subcommand_parsers.add_parser(
        'list',
        description='list the available cli configuration profiles',
        conflict_handler='resolve',
        help='list cli profiles')
    cli_config_list_parser.set_defaults(func=listConfigs)


##################################################################
#
##################################################################
def listConfigsOld(args = None):
    configArr = glob.glob(Config.CONFIG_BASE_NAME_PATH + '*')
    print("list of existing configuration profiles: ")
    for configItem in configArr:
        fn_and_path = configItem.split('/')
        fn = fn_and_path[-1]
        profNameArr = fn.split('_')
        profName = profNameArr[1]
        line = "\t"
        if (Config.CONFIG_CURRENT == configItem):
            line += "* "
        else:
            line += "  "
        line += profName
        #TODO load the profile to add some details here
        c = loadConfig(profName)
        line += " -  \thostname:" + c[Config.HOSTNAME] + ":" + c[Config.PORT] + "\t\tuser:" + c[Config.USER] + "\t\tecs-version:" + str(c[Config.VERS])
        print(line)
    return 

def listConfigs(args = None):
    configArr = glob.glob(Config.CONFIG_BASE_NAME_PATH + '*')
    print("list of existing configuration profiles: ")

    template = "{0:6}|{1:25}|{2:25}|{3:10}|{4:25}|{5:11}"
    str = template.format('ACTIVE', 'PROFILE', 'HOSTNAME', 'PORT', 'MGMT USER', 'ECS VERSION')
    print(str)
    print("-" * len(str))

    for configItem in configArr:
        fn_and_path = configItem.split('/')
        fn = fn_and_path[-1]
        profNameArr = fn.split('_')
        profName = profNameArr[1]
        active = " "
        if (Config.CONFIG_CURRENT == configItem):
            active = "    * "
            
        c = loadConfig(profName)
        str = template.format(active, profName, c[Config.HOSTNAME], c[Config.PORT], c[Config.USER], c[Config.VERS])
        print(str)
    return


##################################################################
#
##################################################################
def config_set_active_parser(subcommand_parsers):
    # create namespace command parser
    parser = subcommand_parsers.add_parser(
        'set',
        description='sets the active cli configuration profile',
        conflict_handler='resolve',
        help='set active cli profile')

    parser.add_argument(
        '-pf', '-profile',
        help='the name of the profile whose values will be the host, username, cookiefile and port',
        dest='profile',
        required=True)

    parser.set_defaults(func=setActiveConfig)

##################################################################
#   
##################################################################
def updateCurrentProfileFile(profileFile):
    out_file = open(Config.CONFIG_CURRENT_FILE,"w")
    result = {'current': profileFile}
    json.dump(result, out_file, indent=4)
    out_file.close()
    Config.CONFIG_CURRENT = profileFile


##################################################################
#
##################################################################
def setActiveConfig(args):
    profileFile = Config.CONFIG_BASE_NAME_PATH + args.profile + "_.json"

    if os.path.isfile(profileFile):
        updateCurrentProfileFile(profileFile)
    else:
        print('This profile does NOT exist. Here is a list of existing profiles')
    listConfigs()
    return

##################################################################
#
##################################################################
def cli_config_parser(parent_subparser):
    subcommand_list = ['-h', '--help', 'list', 'set', 'delete']
    cli_config_parser = parent_subparser.add_parser(
        'config',
        description='ECS profile configuration to set default values for host, user, cookiefile and port. To create a profile no subcommand is needed just use "ecscli config" and you will be prompted for information, but you may optionally enter a profile name with the -pf/-profile arg',
        conflict_handler='resolve',
        help='ecscli profile configuration')
    cli_config_parser.add_argument(
        '-pf', '-profile',
        help='multiple profiles can be saved. If a profile name is not given, the prompted username value will be used',
        dest='profile')

    if (len(sys.argv) < 2):
        return

    if sys.argv[1] == "config":
        if len(sys.argv) > 2 and (sys.argv[2] in subcommand_list):
            subcommand_parsers = cli_config_parser.add_subparsers(help='Use One Of Commands')
            cli_config_list_parser(subcommand_parsers)
            config_set_active_parser(subcommand_parsers)
            cli_config_del_parser(subcommand_parsers)
        else:
            cli_config_parser.set_defaults(func=createConfig)

##################################################################
#
##################################################################
def createConfig(args):
    if ("_" in args.profile):
        print("Profile names are NOT allowed to contain an underscore character.\n")
        return

    h = promptUser("Please enter the default ECS hostname or ip (127.0.0.1):")
    if (h == ''):
        h = '127.0.0.1'
    h = h.strip()

    p = promptUser("Please enter the default command port (4443):")
    if (p == ''):
        p = '4443'
    p = p.strip()

    u = promptUser("Please enter the default user for the profile (root):")
    if (u == ''):
        u = 'root'
    u = u.strip()

    if (args.profile is None):
        tmpProf = u
        tmpProf = tmpProf.replace('_', '-')
        tmpProf = tmpProf.strip()
        args.profile = tmpProf
    
    v = 0
    while (v not in Config.ALLOWED_VERS):
        v = promptUser("Please enter the ECS version for the profile allowed:(2.2,3.0,3.1,3.2) default:(" + str(Config.DEFAULT_VERS)  + "):")
        if (v==''):
            v = Config.DEFAULT_VERS

        try:
            v = float(v)
        except:
            print('version must be an int or float')

        if (v not in Config.ALLOWED_VERS):
            print('version ' + str(v) + ' not allowed')
            
    
    d = Config.CONFIG_PATH + '/' + args.profile


    theCfg = {}
    theCfg[Config.HOSTNAME] = h
    theCfg[Config.PORT] = p
    theCfg[Config.USER] = u
    theCfg[Config.VERS] = v
    theCfg[Config.COOKIEDIR] = d

    
    saveConfig(theCfg, args.profile)

    listConfigs()
    return

