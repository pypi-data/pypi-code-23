"""AgilePoint API Lib"""
from hammock import Hammock
from .admin import Admin
from .workflow import Workflow
# pylint: disable=too-few-public-methods

class AgilePoint(object):
    """AgilePoint API

    Host: https://fqdn-of-agilepoint-server:14490
    Path: AgilePointServer
    These are pretty self explanatory: username, password"""
    def __init__(self, host, path, username, password):
        url = '{}/{}'.format(host, path)
        self.agilepoint = Hammock(url, auth=(username, password),
                                  headers={'Content-Type': 'application/json'})
        self.workflow = Workflow(self)
        self.admin = Admin(self)
