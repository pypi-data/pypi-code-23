"""Package skeleton

.. moduleauthor:: Wojciech Sobala <wojciech.sobala@pl.ibm.com>
"""

#import json
#import requests
#import urllib3
#import sys
#import os
#from pip.locations import site_packages, user_site
#
#if os.path.exists(os.path.join(site_packages, 'watson_machine_learning_client', 'libs')):
#    sys.path.insert(1, os.path.join(site_packages, 'watson_machine_learning_client', 'libs'))
#else:
#    sys.path.insert(1, os.path.join(user_site, 'watson_machine_learning_client', 'libs'))
#
#from repository_v3.mlrepositoryartifact import MLRepositoryArtifact
#from repository_v3.mlrepositoryclient import MLRepositoryClient
#from repository_v3.mlrepository import MetaProps, MetaNames
#from .utils import *
from .client import WatsonMachineLearningAPIClient
