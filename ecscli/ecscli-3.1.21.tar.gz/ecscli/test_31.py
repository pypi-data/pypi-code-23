from ecscli import runCmd
from ecscli import main_parser
import common
import sys
import json

from test_common import *

# ECS3.1:  10.245.133.65/66/67/68

######################################################################
##
##
######################################################################
def pSilent(s, silent=True):
    if not silent:
        print(s)




def createbucket(bucket, namespace, owner, silent=False):
    print('Entered test_31.py createbucket')
    sys.argv = ["", "bucket", "create", "-name", bucket, "-fs", "false", "-ht", "S3", "-stale_allowed",
        "false", "-ns", namespace]


    if owner is not None:
        sys.argv.append('-owner')
        sys.argv.append(owner)
        print('createbucket bucketname: ' + bucket + ' namespace: ' + namespace + ' owner: ' + owner)
    else:
        print('createbucket bucketname: ' + bucket + ' namespace: ' + namespace)

    result = runCmd()
    pSilent(result)


######################################################################
##
##
######################################################################
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

