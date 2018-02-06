from ecscli import runCmd
from ecscli import main_parser
import common
import sys
import json

from test_common import *


######################################################################
##
##
######################################################################
def pSilent(s, silent=True):
    if not silent:
        print(s)



def listAll(silent=False):
    thelist = []
    sys.argv = ["", "varray", "list"]
    result = runCmd()
    printit(result, silent)
    return result

def list_all_vdc(silent=False):
    sys.argv = ["", "vdc_data", "list"]
    result = runCmd()
    printit(result, silent)
    return result


def create1(silent=False):
    vpoolName = 'jigitty'

    varrayResult = listAll()
    varrays = varrayResult['varray']
    varray = varrays[0]
    varrayName = varray['name']
    print('Using varray name: ' + varrayName)

    vdcName = ''
    vdcResult = list_all_vdc(True)
    vdcs = vdcResult['vdc']
    for v in vdcs:
        print("Investigating VDC:")
        printit(v, silent)
        if v['local'] == True:
            vdcName = v['name']
            print('Going to use VDC:' + vdcName)
            break

    if vdcName == '':
        print('Did NOT test. No local VDCs')
        return
    print('Using VDC name: ' + vdcName)

    zp = varrayName + '^' + vdcName
    sys.argv = ["", "objectvpool", "create", '-name', vpoolName, '-desc', 'just for testing and will be removed',
        '-zp', zp, '-allowallnamespaces', 'true']

    result = runCmd()
    printit(result, silent)
    return result




if __name__ == "__main__":
    if (len(sys.argv) > 1):
        possibles = globals().copy()
        possibles.update(locals())
        method = possibles.get(sys.argv[1])

        if (len(sys.argv) > 2):
            funcArgs = sys.argv[2:]
            method(*funcArgs)
        else:
            method()

