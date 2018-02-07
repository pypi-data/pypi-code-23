from ecscli import runCmd
from ecscli import main_parser
import common
import sys
import inspect

from test_common import *

def objectuser_list_uid(silent=False):
    #case5(True)
    sys.argv = ["", "objectuser", "list", "-uid", "joeouser", "-namespace", "conerj"]
    result = runCmd()
    printit(result, silent)

def case5(silent=False):
    objectuserList = []
    sys.argv = ["", "objectuser", "list", "-hostname"]
    result = runCmd()
    #printit(result)
    blobuser = result['blobuser']
    for b in blobuser:
        userid = b['userid']
        objectuserList.append(userid)
        print(userid)
    return objectuserList

def createtags(silent=False):
    sys.argv = ["", "objectuser", "set-usertag", "-uid", "joe", "-ts", "tag1^val1", "tag2^val2"] 
    result = runCmd()
    printit(result, silent)


def gettags(silent=False):
    sys.argv = ["", "objectuser", "get-usertag", "-uid", "user2"]
    result = runCmd()
    printit(result, silent)

def gettags_withns(silent=False):
    sys.argv = ["", "objectuser", "get-usertag", "-uid", "user2", "-ns", "rena"]
    result = runCmd()
    printit(result, silent)


def deletetags(silent=False):
    sys.argv = ["", "objectuser", "delete-usertag", "-uid", "user2"]
    result = runCmd()
    printit(result, silent)


def queryuser(silent=False):
    sys.argv = ["", "objectuser", "query", "-ts", "tag1^val1", "tag2^val2"]
    result = runCmd()
    printit(result, silent)

def queryuser1(silent=False):
    sys.argv = ["", "objectuser", "query", "-ts", "tag1^val1"]
    result = runCmd()
    printit(result, silent)

def queryuser_withns(silent=False):
    sys.argv = ["", "objectuser", "query", "-ns", "rena", "-ts", "tag1^val1", "tag2^val2"]
    result = runCmd()
    printit(result, silent)

def createuser(silent=False):
    sys.argv = ["", "objectuser", "create", "-uid", "joe", "-ns", "ns", "-ts", "tag1^val1", "tag2^val2"]
    result = runCmd()
    printit(result, silent)


def deleteuser(silent=False):
    sys.argv = ["", "objectuser", "delete", "-uid", "user2", "-ns", "rena"]
    result = runCmd()
    printit(result, silent)

