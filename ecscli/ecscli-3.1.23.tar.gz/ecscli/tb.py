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



######################################################################
## synopsis buckets need this search metadata
##
######################################################################
def setSynopsisMeta(bucket, ns, silent=False):
    sys.argv = ["", "bucket", "set-metadata", "-name", bucket,
        "-ht", "S3", "-namespace", ns, "-metaset", "metaName1^metaVal1", "metaName2^metaVal2"]
    result = runCmd()
    pSilent(result)
    
    return result

######################################################################
## synopsis buckets need this search metadata
##
######################################################################
def updateBucketOwner(owner, ns, bucket, silent=False):
    print('Entered updateBucketOwner: owner: ' + owner + ' ns: ' + ns + ' bucket: ' + bucket )
    sys.argv = ["", "bucket", "update-owner", "-ns", ns, "-name", bucket, "-owner", owner]
    result = runCmd()
    pSilent(result, silent)
    return result


######################################################################
## synopsis buckets need this search metadata
##
######################################################################
def createSynopsisBucket(bucket, namespace, owner, silent=False):
    sys.argv = ["", "bucket", "create", "-name", bucket, "-fs", "false", "-ht", "S3", "-stale_allowed",
        "false", "-ns", namespace, "-sm", 
        "x-amz-meta-x-emc-posix-owner-name^string^string",
        "x-amz-meta-x-emc-posix-group-owner-name^string^string",
        "LastModified^string^datetime",
        "Size^string^integer",
        "ObjectName^string^string"]
    result = runCmd()
    pSilent(result)

    result = updateBucketOwner(owner, namespace, bucket)


######################################################################
## 
## list Buckets/Owners for all namespaces
##
######################################################################
def lbAll(silent=False):
    template = "{0:50}|{1:50}|{2:50}"
    str = template.format('NAMESPACE', 'BUCKET', 'OWNER')
    pSilent(str, silent)

    sys.argv = ["", "namespace", "list"]
    result = runCmd(silent)
    
    for n in result['namespace']:
        nameSpace = n['name']
        bucketResult = listBucketsAndOwners(True, nameSpace)

        for b in bucketResult['object_bucket']:
            output = []
            output.append(nameSpace)

            bucketName = b['name']
            bucketOwner = b['owner']
            output.append(bucketName)
            output.append(bucketOwner)
            str = template.format(*output)
            pSilent(str, silent)


######################################################################
##
## 
######################################################################
def listBucketsAndOwners(silent=False, theNs = None):

    template = "{0:50}|{1:50}|{2:50}|{3:50}"
    str = template.format('BUCKETNAME', 'OWNER', 'SECRETKEY1', 'SECRETKEY2')
    pSilent(str, silent)

    if theNs is not None:
        sys.argv = ["", "bucket", "list", "-ns", theNs]
    else:
        sys.argv = ["", "bucket", "list"]
    result = runCmd(silent)
    '''
    for r in result['object_bucket']:
        output = []
        bucketName = r['name']
        bucketOwner = r['owner']


        #str = template.format(*output)
    '''
    return result


######################################################################
## not quite working completly right
## seems to have an issue when there's an objectuser with no secret keys
######################################################################
def bucketAndCreds(silent=False):
    #theNs = 'conerj'
    theNs = 'stu' #for synopsis testing

    sys.argv = ["", "objectuser", "list", "-ns", theNs]
    result = runCmd('True')
    objectUsers = result['blobuser']
    ouList = []
    for o in objectUsers:
        ou = o['userid']
        ouList.append(ou)


    sys.argv = ["", "bucket", "list", "-ns", theNs]
    result = runCmd(True)
    num = result['object_bucket']
    numStr = str(len(num))
    print('There are ' + numStr + " buckets in namespace: " + theNs)

    #print('BUCKETNAME\t\t\tOWNER\tSECRETKEY\tSECRETKEY')
    template = "{0:25}|{1:20}|{2:35}|{3:35}"
    print template.format('BUCKETNAME', 'OWNER', 'SECRETKEY1', 'SECRETKEY2')

    for r in result['object_bucket']:
        try:
            bucketName = r['name']
            bucketOwner = r['owner']
            #print('\nbucketName.........' + bucketName )

            #check if the owner is an object user.
            #could be a mgmt user or possibly a swift user if that's the head type
            output = []
            if bucketOwner in ouList:
                sys.argv = ["", "secretkeyuser", "user-show", "-uid", bucketOwner]
                result2 = runCmd(True)
                sc1 = result2['secret_key_1']
                sc2 = result2['secret_key_2']
                output.append(bucketName)
                output.append(bucketOwner)
                output.append(sc1)
                output.append(sc2)

                #print(bucketName + '\t\t\t' + bucketOwner + '\t' + sc1 + '\t' + sc2)
                print(template.format(*output) )

            else:
                output.append(bucketName)
                output.append(bucketOwner)
                output.append('NONE')
                output.append('NONE')

                #print(bucketName + '\t\t\t' + bucketOwner + '\t' + 'N/A')
                print(template.format(*output) )

        except Exception:
            print('exception...........')
    return result


######################################################################
## save the ECS license to a file, for reload testing
##
######################################################################
def licenseToFile(silent=False):
    sys.argv = ["", "system", "get-license"] 
    result = runCmd()
    pSilent(result)

    
    with open('templicense.json', 'w') as fp:
        json.dump(result, fp, indent=4)
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
