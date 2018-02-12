import os
import json
from bymtesting.Lib.RequestService import *
from bymtesting.WebApi.UrlService import *
#from bymtesting.WebApiServicePayload import *
from bymtesting.Lib.ServiceBase import *
from builtins import print
from typing import Dict, Tuple, List


class WebApiService(ServiceBase):

    def __init__(self, isRaiseResponseExceptionWhenStatus200NotOk=True):
        ServiceBase.__init__(self, isRaiseResponseExceptionWhenStatus200NotOk)
        self.root = UrlService().getWebApiServiceRootUrl()

    def createutvikler(self, navn):
        payload = {'navn': navn}
        requestURL = '{}/api/utvikler'.format(self.root)
        return self.postRequest(requestURL, payload, ResponseItemModel)

    def getutvikler(self, utviklerId):
        requestURL = '{}/api/utvikler/{}'.format(
            self.root, utviklerId)
        return self.getRequest(requestURL, ResponseItemModel)

    def updateutvikler(self, utviklerId, navn):
        payload = {'navn': navn}
        requestURL = '{}/api/utvikler/{}'.format(
            self.root, utviklerId)
        return self.putRequest(requestURL, payload)

    def getAllutvikler(self):
        requestURL = '{}/api/utvikler'.format(self.root)
        return self.getRequest(requestURL, ResponseItemsModel)

    def deleteutvikler(self, utviklerId):
        requestURL = '{}/api/utvikler/{}'.format(
            self.root, utviklerId)
        return self.deleteRequest(requestURL)
