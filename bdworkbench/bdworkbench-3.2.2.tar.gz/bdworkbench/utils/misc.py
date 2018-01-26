#
# Copyright (c) 2016 BlueData Software, Inc.
#
from __future__ import print_function

import os
import sys
import platform
import hashlib
import requests
import subprocess
from contextlib import closing
from .config import KEY_DEF_ORGNAME, SECTION_WB, KEY_STAGEDIR
from ..inmem_store import ENTRY_DICT, DELIVERABLE_DICT
from ..constants import DEFAULT_CONFIG_API_VER, SUPPORTED_DOCKER_VERSIONS

DIRNAME = os.path.dirname(os.path.realpath(__file__))
SDK_DIRNAME = os.path.abspath(os.path.join(DIRNAME, '..', '..'))

def calculateAndValidateDockerVersion(inMemStore):
    """
    We only support Docker 1.7 and Docker 1.12
    """
    currentVersion = None
    dockerVersion = ''
    try:
        p = subprocess.Popen(["docker", "info"], stdout=subprocess.PIPE,
                                                 stderr=subprocess.PIPE)
        p.wait()
        out, err = p.communicate()
        if p.returncode != 0:
            raise Exception("Running 'docker info' failed.")
    except Exception:
            print("ERROR: Failed to determine docker version.")
            print("       Please ensure you have a supported docker daemon running.")
            return False

    infoLines = out.split('\n')
    serverVerList = [x for x in infoLines if x.startswith('Server Version')]
    if len(serverVerList) != 0:
        dockerVersion = serverVerList[0].split()[-1]
    else:
        # As a backup strategy assume a docker daemon version based in the
        # running kernel version.
        kernelVerList = [x for x in infoLines if x.startswith('Kernel Version')]
        if len(kernelVerList) > 0:
            kver = kernelVerList[0].split()[-1]
            if kver.startswith('2.6'):
                dockerVersion = '1.7'
            elif kver.startswith('3.10'):
                dockerVersion = '1.12'

    for supportedVer in SUPPORTED_DOCKER_VERSIONS:
        if dockerVersion.startswith(supportedVer):
            currentVersion = supportedVer
            break

    if currentVersion != None:
        inMemStore.addField(DELIVERABLE_DICT, "built_on_docker", currentVersion)
        return True

    print ("ERROR: Failed to detect a supported docker server version.")
    print ("ERROR: Supported Docker versions " + str(SUPPORTED_DOCKER_VERSIONS))

    return False

def processArgs(parser, args):
    """
    Essentially performs the function of a shell wrt string processing.

    All arguments that are enclosed with in " or ' are concatinated with a space
    before handing it off to the parser for processing.
    """
    allsplit = []
    if type(args) == str:
        allsplit = args.split()
    elif  type(args) == list:
        allsplit = args
    else:
        raise Exception("Input args must be either a list or a str. (%s)" % type(args))

    retArgs = []

    appendStr = lambda x, y: ' '.join([x, y.strip('"').strip()]).strip()
    while len(allsplit) > 0:
        try:
            s = allsplit.pop(0).strip()
        except:
            break

        if s.startswith('"'):
            argString = ''
            while not s.endswith('"'):
                argString = appendStr(argString, s)
                try:
                    s = allsplit.pop(0).strip()
                except:
                    break
            argString = appendStr(argString, s)
            retArgs.append(argString)
        else:
            retArgs.append(s)

    try:
        return parser.parse_args(retArgs)
    except SystemExit:
        return None

def calculateMD5SUM(filepath):
    """

    """
    md5 = hashlib.md5()
    with open(filepath, 'rb') as f:
        for block in iter(lambda: f.read(4096), b''):
            md5.update(block)

    return md5.hexdigest()


def downloadFile(url, md5, config):
    """

    """
    try:
        stagingDir = config.get(SECTION_WB, KEY_STAGEDIR)
        if not os.path.exists(stagingDir):
            os.makedirs(stagingDir)

        localfile = os.path.join(stagingDir, os.path.basename(url))

        if md5 != None and os.path.exists(localfile):
            print ("Verifying checksum of existing file '%s' ... " %
                        (os.path.basename(localfile)), end='')
            sys.stdout.flush()
            recalc = calculateMD5SUM(localfile)
            if recalc == md5:
                print("passed.")
                return localfile
            else:
                print("mismatched.")

            sys.stdout.flush()

        print("Downloading: ", end='')
        sys.stdout.flush()
        with closing(requests.get(url, stream=True)) as req:
            size = req.headers['Content-Length']
            blockSize = int(size) / 60 ## Limit the progress bar to 60cols.
            with open(localfile, 'w') as f:
                for chunk in req.iter_content(chunk_size=blockSize):
                    if chunk:
                        f.write(chunk)
                        print('#', end='')
                        sys.stdout.flush()

        if md5 != None and os.path.exists(localfile):
            print()
            print ("Verifying checksum of downloaded file ... ", end='')
            newSum = calculateMD5SUM(localfile)
            if md5 != newSum:
                print("FAILED.")
                return None

        print()
        return localfile
    except Exception as e:
        print("ERROR: failed to download from %s:" % (url), e)
        return None

def getOrgname(inmem, config):
    """
    Best effort to figure out what organization name to use.
    """
    delivDict = inmem.getDict(DELIVERABLE_DICT)
    if delivDict.has_key("orgname"):
        orgname = delivDict["orgname"]
        if orgname.upper() == 'YOUR_ORGANIZATION_NAME':
            print("ERROR: 'YOUR_ORGANIZATION_NAME' must be replaced with the "
                  "actual name of your organization.")
            return None
    else:
        orgname = config.get(SECTION_WB, KEY_DEF_ORGNAME)
        if orgname == None:
            print("ERROR: Organization name must be speficied. Use "
                  "'builder organization --name NAME' to set it.")

    return orgname

def getBaseOSMajorVersion():
    """
    Function to figure out the major version number for the Base Operating System
    """
    (distroName, version, Id) = platform.linux_distribution()
    if version != '':
        return version.split('.')[0]
    else:
        raise ValueError('Could not calculate Base OS major version')

def constructDistroId(inmem, config, distroId):
    """

    """
    if distroId != None:
        orgname = getOrgname(inmem, config)

        if orgname != None:
            relList = distroId.split('/')
            if len(relList) == 1:
                return "%s/%s" % (orgname, relList[0])
            elif len(relList) == 2:
                return "%s/%s" % (orgname, relList[1])
            else:
                print("ERROR: unrecognized distro_id specification in the json file.")
                return None

    return None

def doSkipImageRebuild(destPath, md5File=None):
    if os.getenv('BDS_SDK_SKIP_IMAGE_REBUILD', 'false') == 'true':
        ## User asked to skip the image rebuild. So just use the existing
        ## files.
        if os.path.exists(destPath):
            if md5File and (not os.path.exists(md5File)):
                # We can regenerate the md5sum but, something must have happened
                # for the image file to exist and not the .md5sum file. So, to
                # prevent the developer from shooting themselves in the foot,
                # lets force them to rebuild the image.
                print("ERROR: Asked to not rebuild image but MD5 sum is unknown")
                print("       %s doesn't exist." % (md5File))
                return False

            print('\n', "WARNING: Using preexisting image file ", destPath, sep='')
            print("         To disable this behaviour set BDS_SDK_SKIP_IMAGE_REBUILD=false in your")
            print("         environment before invoking the workbench or the instruction file.", '\n')
            return True

    return False

def checkConfigApiVersion(configapi):
    """
    Utility function to validate the input config api version. This only logs
    a warning for now.
    """
    if configapi > DEFAULT_CONFIG_API_VER:
        print("WARNING: This SDK only supports up to config api v%s." % DEFAULT_CONFIG_API_VER)
