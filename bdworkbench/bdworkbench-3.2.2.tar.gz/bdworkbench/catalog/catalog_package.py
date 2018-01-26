#
# Copyright (c) 2016 BlueData Software, Inc.
#

from __future__ import print_function
from .. import SubCommand
from ..constants import *
from ..inmem_store import ENTRY_DICT, DELIVERABLE_DICT
from ..utils.config import KEY_SDKBASE, KEY_STAGEDIR, KEY_DELIVERABLES, SECTION_WB
from ..utils.misc import getBaseOSMajorVersion

import os
import subprocess

class CatalogPackage(SubCommand):
    """

    """
    def __init__(self, config, inmemStore, cmdObj):
        SubCommand.__init__(self, config, inmemStore, cmdObj, 'package')

    def getSubcmdDescripton(self):
        return 'Package all components of the catalog into a bundle (.bin file).'

    def populateParserArgs(self, subparser):
        subparser.add_argument('-v', '--verbose', action='store_true',
                               dest='verbose', default=False,
                               help='Show details of the packing process.')

    def run(self, pargs):
        stageDir = self.config.get(SECTION_WB, KEY_STAGEDIR)
        delivDir = self.config.get(SECTION_WB, KEY_DELIVERABLES)

        if not os.path.exists(stageDir):
            os.makedirs(stageDir)

        delivDict = self.inmemStore.getDict(DELIVERABLE_DICT)
        entryDict = self.inmemStore.getDict(ENTRY_DICT)

        logoDict = entryDict['logo'] if entryDict.has_key('logo') else {}
        imageDict = entryDict['image'] if entryDict.has_key('image') else {}
        appconfigDict = entryDict['setup_package'] if entryDict.has_key('setup_package') \
                                                            else {}

        if delivDict.has_key('entry'):
            entry = delivDict['entry']
        else:
            print("ERROR: 'catalog save' must be executed before packaging.")
            return False

        distro_id = entryDict['distro_id']
        version = entryDict['version']
        name = entryDict['label']['name']
        description = entryDict['label']['description']
        catalogApiVer = str(entryDict['catalog_api_version'])
        builtOnDocker = delivDict['built_on_docker']

        if logoDict.has_key('import_url'):
            logo = 'undefined'
            logoMd5 = 'undefined'
        elif logoDict.has_key('source_file') and delivDict.has_key('logo'):
            logo = delivDict['logo']
            logoMd5 = delivDict['logoSum']
        else:
            print("WARN: No logo to include in the bundle.")
            logo = "undefined"
            logoMd5 = "undefined"

        if delivDict.has_key('registryUrl'):
            image = 'undefined'
            imageMd5 = 'undefined'
            imageOS = delivDict['imageOS']
            imageOSMajor = delivDict['imageOSMajor']
            imageName = delivDict['imageName']
            registryUrl = delivDict['registryUrl']
            registryAuthEnabled = 'true' if delivDict['registryAuthEnabled'] else 'false'
            contentTrustEnabled = 'true' if delivDict['contentTrustEnabled'] else 'false'
        elif imageDict.has_key('import_url'):
            image = 'undefined'
            imageMd5 = 'undefined'
            imageOS = delivDict['imageOS']
            imageOSMajor = delivDict['imageOSMajor']
            imageName = delivDict['imageName']
            registryUrl = 'undefined'
            registryAuthEnabled = 'undefined'
            contentTrustEnabled = 'undefined'
        elif imageDict.has_key('source_file') and delivDict.has_key('imageFile'):
            image = delivDict['imageFile']
            imageMd5 = delivDict['imageSum']
            imageOS = delivDict['imageOS']
            imageOSMajor = delivDict['imageOSMajor']
            imageName = delivDict['imageName']
            registryUrl = 'undefined'
            registryAuthEnabled = 'undefined'
            contentTrustEnabled = 'undefined'
        else:
            print("WARN: No image to include in the bundle or push to a registry.")
            image = 'undefined'
            imageMd5 = 'undefined'
            imageOS = 'undefined'
            imageOSMajor = 'undefined'
            imageName = delivDict['imageName']
            registryUrl = 'undefined'
            registryAuthEnabled = 'undefined'
            contentTrustEnabled = 'undefined'

        if appconfigDict.has_key('import_url'):
            appconfig = 'undefined'
            appconfigMd5 = 'undefined'
        elif appconfigDict.has_key('source_file') and delivDict.has_key('appconfig'):
            appconfig = delivDict['appconfig']
            appconfigMd5 = delivDict['appconfigSum']
        else:
            print("ERROR: 'appconfig autogen|file|url <args>' must be executed before packaging.")
            return False

        if appconfigDict.has_key('config_api_version'):
            configApiVersion = str(appconfigDict['config_api_version'])
        else:
            print("ERROR: appconfig's 'config_api_version' is undefined.")
            configApiVersion = None

        if entryDict.has_key('distro_dependency'):
            independent = 'false'
        else:
            independent = 'true'

        if delivDict.has_key('sources'):
            sources = ';'.join(delivDict['sources'])
        else:
            sources = ''

        # Ensure all mandatory arguments are available.
        if (entry == None) or (appconfig == None) or (configApiVersion == None):
            return False

        # Populate a package conf file to pass all the required arguments.
        paramFile = os.path.join(stageDir, 'params.conf')

        try:
            with open(paramFile, 'w') as f:
                f.write('\n'.join([
                                '='.join(['STAGING_DIR', stageDir]),
                                '='.join(['DELIVERABLE_DIR', delivDir]),
                                '='.join(['IMAGEOSCLASS', imageOS]),
                                '='.join(['IMAGEOSMAJOR', imageOSMajor]),
                                '='.join(['BUILTONDOCKER', builtOnDocker]),
                                '',
                                '='.join(['DISTRO', distro_id]),
                                '='.join(['ENTRY', entry]),
                                '='.join(['VERSION', version]),
                                '='.join(['NAME', "'%s'" % (name)]),
                                '='.join(['DESCRIPTION', "'%s'" % (description)]),
                                '='.join(['INDEPENDENT', independent]),
                                '='.join(['CATALOG_API_VERSION', catalogApiVer]),
                                '',
                                '='.join(['LOGO', logo]),
                                '='.join(['LOGO_CHECKSUM', logoMd5]),
                                '',
                                '='.join(['IMAGE', image]),
                                '='.join(['IMAGE_CHECKSUM', imageMd5]),
                                '='.join(['IMAGE_NAME', imageName]),
                                '='.join(['REGISTRY_URL', registryUrl]),
                                '='.join(['REGISTRY_AUTH_ENABLED', registryAuthEnabled]),
                                '='.join(['CONTENT_TRUST_ENABLED', contentTrustEnabled]),
                                '',
                                '='.join(['APPCONFIG', appconfig]),
                                '='.join(['APPCONFIG_CHECKSUM', appconfigMd5]),
                                '='.join(['CONFIG_API_VERSION', configApiVersion]),
                                '',
                                '='.join(["SOURCES", "'%s'" % (sources)])
                              ]))
        except Exception as e:
            print("EXCEPTION: Failed to write params.conf.", e)
            return False

        baseDir = self.config.get(SECTION_WB, KEY_SDKBASE)
        pkgScript = os.path.join(baseDir, 'appbuild', 'bundle', 'package.sh')
        cmdList = ["bash", pkgScript, '--config', paramFile]
        if pargs.verbose:
            cmdList.append('--verbose')

        try:
            print("Packaging the catalog entry for %s." %(imageOS))
            subprocess.check_call(' '.join(cmdList), shell=True,
                                  stderr=subprocess.STDOUT)
            return True
        except subprocess.CalledProcessError as cpe:
            print(cpe)
            return False

    def complete(self, text, argsList):
        return []

    def _is_url(self, filed):
        return filed.startswith('http://') or filed.startswith('https://')
