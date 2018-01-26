#
# Copyright (c) 2017 BlueData Software, Inc.
#

"""
Subcommand to \"builder\" main command for specifying registry details.
"""

from __future__ import print_function
from ..image.image_file import OS_CLASS_DICT
from .. import SubCommand
from ..inmem_store import DELIVERABLE_DICT

class BuilderRegistry(SubCommand):
    """
    Subcommand to \"builder\" main command for specifying registry details.
    """

    def __init__(self, config, inmemStore, cmdObj):
        SubCommand.__init__(self, config, inmemStore, cmdObj, 'registry')


    def getSubcmdDescripton(self):
        return 'Set the registry URL for this catalog entry. For privately hosted ' +\
              'registries, the convention is \"registry-host:port\". For ' +\
              'Docker Hub, the value is \"default\". For other registries, ' +\
              'the value will be the URL of the registry without http or https prefix.'


    def populateParserArgs(self, subparser):
        subparser.add_argument('-u', '--url', dest='registryUrl', nargs='?',
                               required=False, default='default', const='default',
                               metavar="registry-host:port or HTTP URL without http prefix",
                               help='Registry URL for the image. ' + \
                               'In case of Docker Hub, use \'docker.io\'.')
        subparser.add_argument('--auth-enabled', dest='registryAuthEnabled', required=False,
                               action='store_true', help='Whether this registry requires authentication.')
        subparser.add_argument('-i', '--imagename', metavar='IMAGE_NAME', type=str,
                               required=False, action='store', default=None,
                               dest='imageName', help="Container Image name."
                               "Required only when image already resides in "
                               "a registry and does not need to be built "
                               "through AppWorkBench. This name would be "
                               "used as an argument to 'docker pull' command.")
        subparser.add_argument('--trust', dest="contentTrustEnabled", required=False,
                               action="store_true",
                               help="Whether Docker Content Trust is enabled "
                                    "for this container image or not.")
        subparser.add_argument('--os', metavar="OS", dest="os", required=False,
                               choices=['centos6', 'rhel6', 'centos7', 'rhel7',
                                        'ubuntu16'], action='store',
                               help="The OS distribution of the container image. "
                                    " Only needs to be supplied with the -i/--imagename "
                                    "option.")
        return

    def run(self, pargs):

        if pargs.registryUrl is not None and ' ' in pargs.registryUrl:
            print("ERROR: No space is allowed in the registry url.")
            return False
        self.inmemStore.addField(DELIVERABLE_DICT, "registryUrl", pargs.registryUrl.strip().lower())
        self.inmemStore.addField(DELIVERABLE_DICT, "registryAuthEnabled", pargs.registryAuthEnabled)
        self.inmemStore.addField(DELIVERABLE_DICT, "contentTrustEnabled", pargs.contentTrustEnabled)
        # If imagename is defined, user also needs to provide a value for OS option.
        # If both imagename and OS are defined, that means image already resides in a
        # registry and we dont need to build it through AppWorkBench.
        if pargs.imageName != None:
            if pargs.os == None:
                print ("ERROR: Need to specify the OS distribution of "
                   "the container image using the --os option "
                   "if the container image resides in a registry")
                return False
            else:
                if self.inmemStore.getDict(DELIVERABLE_DICT).has_key('imageName'):
                    print("ERROR: An 'image build' command has already been processed "
                          "in this session. Specifying --i/imagename option is not "
                          "allowed in this situation.")
                    return False
                self.inmemStore.addField(DELIVERABLE_DICT, "imageName", pargs.imageName)
                self.inmemStore.addField(DELIVERABLE_DICT, "imageOS", OS_CLASS_DICT[pargs.os][0])
                self.inmemStore.addField(DELIVERABLE_DICT, "imageOSMajor", OS_CLASS_DICT[pargs.os][1])
            
        return True

    def complete(self, text, argsList):
        return []
