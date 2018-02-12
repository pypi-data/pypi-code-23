import os
import json
import requests
from requests import Response
from bymtesting.Lib.RequestService import *
from bymtesting.Lib.ServiceBasePayload import *
from bymtesting.Lib.Exceptions import *


class ServiceBase():

    def printObjectToJson(self, object):
        print(json.dumps(object, default=self.obj_dict))

    def obj_dict(self, obj):
        return obj.__dict__

    def __init__(self, isRaiseResponseExceptionWhenStatus200NotOk=True):
        self.isRaiseResponseExceptionWhenStatus200NotOk = isRaiseResponseExceptionWhenStatus200NotOk
        self.request = RequestService()

    #################
    def getResponseModel(self, response, ViewModelType):
        viewModel = None
        errorMessage = ""
        text = json.loads(response.text)
        if (response.ok == True):
            viewModel = ViewModelType(text["result"])
        else:
            errorMessage = text["errorMessage"]
        model = ResponseModel(response, viewModel, errorMessage)
        if (self.isRaiseResponseExceptionWhenStatus200NotOk
                and model.response.status_code != 200):
            raise ResponseException(model)
        return model

    def getResponseModelWithExpectedError(self, response, ViewModelType):
        viewModel = None
        errorMessage = ""
        text = json.loads(response.text)
        if (response.ok == True):
            viewModel = ViewModelType(text["result"])
        else:
            errorMessage = text["errorMessage"]
        model = ResponseModel(response, viewModel, errorMessage)

        return model

    def getRequest(self, url, ViewModelType):
        response = self.request.get(url)
        return self.getResponseModel(response, ViewModelType)

    def getRequestWithFile(self, url):
        response = self.request.downloadFile(url)
        return response

    def postRequest(self, url, payload, ViewModelType=GenericViewModel):
        self.printObjectToJson(payload)
        response = self.request.post(url, payload)
        return self.getResponseModelWithExpectedError(response, ViewModelType)

    def postRequestWithout(self, url, ViewModelType=GenericViewModel):
        response = self.request.post(url, {})
        return self.getResponseModel(response, ViewModelType)

    def postRequestWithExpectedError(self,
                                     url,
                                     payload,
                                     ViewModelType=GenericViewModel):
        self.printObjectToJson(payload)
        response = self.request.post(url, payload)
        return self.getResponseModelWithExpectedError(response, ViewModelType)

    def putRequest(self, url, payload, ViewModelType=GenericViewModel):
        response = self.request.put(url, payload)
        return self.getResponseModel(response, ViewModelType)

    def deleteRequest(self, url, ViewModelType=GenericViewModel):
        response = self.request.delete(url)
        return self.getResponseModel(response, ViewModelType)

    #################

    def getWithoutReadingBodyRequest(self, url):
        response = self.request.get(url)
        return ResponseModel(response, None, None)

    def post_with_filesRequest(self, url, payload, files):
        self.printObjectToJson(payload)
        response = self.request.post_with_files(url, payload, files)
        viewModel = None
        errorMessage = ""
        text = json.loads(response.text)
        if (response.ok == True):
            viewModel = text["result"]
        else:
            errorMessage = text["errorMessage"]
        return ResponseModel(response, viewModel, errorMessage)

    def put_with_filesRequest(self, url, payload, files):
        self.printObjectToJson(payload)
        response = self.request.put_with_files(url, payload, files)
        viewModel = None
        errorMessage = ""
        text = json.loads(response.text)
        if (response.ok == True):
            viewModel = text["result"]
        else:
            errorMessage = text["errorMessage"]
        return ResponseModel(response, viewModel, errorMessage)

    def getSwaggerJsonUrl(self):
        requestURL = '{}/swagger/v1/swagger.json'.format(self.root)
        return requestURL

    def clean_and_initialize_database(self):
        requestURL = '{}/api/clean_and_initialize_database'.format(self.root)
        return self.postRequest(requestURL, "")

    def getIsServiceRunning(self):
        print("getIsServiceRunning")
        try:
            self.request.get(self.root)
        except requests.exceptions.ConnectionError:
            return False
        except requests.packages.urllib3.exceptions.NewConnectionError:
            return False
        except requests.packages.urllib3.exceptions.ConnectionError:
            return False
        else:
            return True

    def getIsServiceRunningWithDatabase(self):
        print("getIsServiceRunningWithDatabase")
        try:
            requestURL = '{}/api/healthcheck'.format(self.root)
            result = self.request.get(requestURL)
            return result.status_code == 200
        except requests.exceptions.ConnectionError:
            return False
        except requests.packages.urllib3.exceptions.NewConnectionError:
            return False
        except requests.packages.urllib3.exceptions.ConnectionError:
            return False
        else:
            return True

    # Start ServiceInfoTilstand
    def updateServiceInfoTilstandParams(self, serviceTilstandId):
        requestURL = '{}/api/serviceinfotilstand'.format(self.root)
        payload = {'serviceinfotilstand': serviceTilstandId}
        return self.putRequest(requestURL, payload)

    def getServiceInfoTilstand(self):
        requestURL = '{}/api/serviceinfotilstand'.format(self.root)
        return self.getRequest(requestURL, ServiceInfoTilstandViewModel)

    def getServiceInfoTilstander(self):
        requestURL = '{}/api/serviceinfotilstander'.format(self.root)
        return self.getRequest(requestURL, ServiceInfoTilstanderViewModel)

    # End ServiceInfoTilstand
