import json
import requests
from requests import Response
from bymtesting.Lib.ServiceBase import *
import re
import collections
import uuid


class SwaggerService:

    # def __init__(self):

    def __getSwaggerJsonUrl(self):
        return ServiceBase().getSwaggerJsonUrl()

    def getPathDictFromSwagger(self):
        url = self.__getSwaggerJsonUrl()
        response = requests.get(url)
        swaggerObject = json.loads(response.text)
        return swaggerObject['paths']

    def InsertValueForParameters(self, url, parameterList):
        url = url.lower()
        if (parameterList is None):
            return
        for parameter in parameterList:
            if not (parameter['required']):
                continue
            if(self.parameterIsBearer(parameter)):
                continue
            name = parameter['name'].lower()
            if(self.parameterIsString(parameter)):
                url = self.insertString(name, url)
            if not (self.parameterIsString(parameter)):
                url = self.insertParameter(parameter, name, url)
        return url

    def parameterIsBearer(self, parameter):
        if not (parameter.get('default') is None):
            if(parameter['default'].strip() == 'Bearer'):
                return True
        return False

    def parameterIsString(self, parameter):
        if (parameter.get('format') is None):
            return True
        return False

    def insertString(self, name, url):
        return url.replace('{' + name + '}', str('test'))

    def insertParameter(self, parameter, name, url):
        if(parameter['type'] == 'string' and parameter['format'] == 'uuid'):
            return url.replace('{' + name + '}',  str(uuid.uuid1()))
        else:
            return url.replace('{' + name + '}', str(1))

    def getRestApi(self, url):
        response = requests.get(url)
        swaggerObject = json.loads(response.text)
        paths = swaggerObject['paths']
        sortedPaths = collections.OrderedDict(sorted(paths.items()))
        for key, value in sortedPaths.items():
            for httpverb, valueValue in value.items():
                # print("#{}".format(key))

                self.operationId = valueValue['operationId']
                self.operationIdRegex = re.match(
                    r'Api(.*)(Get|Post|Put|Delete)', self.operationId)
                self.functionVerb = httpverb
                self.resourceName = self.operationIdRegex.group(1)

                self.routeParameters = []
                if('parameters' in valueValue):
                    self.parameters = valueValue['parameters']
                    self.parametersString = ""
                    self.formatString = ""
                    if (len(self.parameters) > 0):
                        for parameter in self.parameters:
                            if(parameter['in'] == 'path'):
                                self.routeParameters.append(parameter)

                    for routeParameter in self.routeParameters:
                        self.parametersString = '{}, {}'.format(
                            self.parametersString, routeParameter['name'])
                        self.formatString = '{}, {}={}'.format(self.formatString, routeParameter[
                                                               'name'], routeParameter['name'])

                    if (len(self.routeParameters) == 0):
                        print('    def {}(self):'.format(self.functionName))
                    else:
                        print('    def {}(self{}):'.format(
                            self.functionName, self.parametersString))

                else:
                    print('    def {}{}(self):'.format(
                        self.functionVerb, self.functionName))

                if (len(self.routeParameters) == 0):
                    print(
                        '        return \'http://{}{}\'.format(self.root)'.format("{}", key))
                else:
                    print(
                        '        return \'http://{}{}\'.format(self.root{})'.format("{}", key, self.formatString))

    def getPaths(self, url):
        response = requests.get(url)
        swaggerObject = json.loads(response.text)
        paths = swaggerObject['paths']
        keys = []
        sortedPaths = collections.OrderedDict(sorted(paths.items()))
        for key, value in sortedPaths.items():
            print(key)
            keys.append(key)
        return keys

    def getPathsWithHttpVerbs(self, url):
        response = requests.get(url)
        swaggerObject = json.loads(response.text)
        paths = swaggerObject['paths']
        sortedPaths = collections.OrderedDict(sorted(paths.items()))
        for key, value in sortedPaths.items():
            for httpverb, valueValue in value.items():
                print("{} {}".format(httpverb, key))

    def getOperationIds(self, url):
        response = requests.get(url)
        swaggerObject = json.loads(response.text)
        paths = swaggerObject['paths']
        operationIds = []
        sortedPaths = collections.OrderedDict(sorted(paths.items()))
        for key, value in sortedPaths.items():
            for httpverb, valueValue in value.items():
                operationIds.append(valueValue['operationId'])
                print(valueValue['operationId'])
                self.operationIdRegex = re.match(
                    r'Api(.*)(Get|Post|Put|Delete)', valueValue['operationId'])

                self.functionVerb = httpverb
                self.functionName = self.operationIdRegex.group(1)
        return operationIds

    def getDefaultConfigurationAsJson(self, url):
        response = requests.get(url)
        swaggerObject = json.loads(response.text)
        paths = swaggerObject['paths']
        sortedPaths = collections.OrderedDict(sorted(paths.items()))
        self.config = {}
        for key, value in sortedPaths.items():
            for httpverb, valueValue in value.items():
                # print("#{}".format(key))

                self.operationIdRegex = re.match(
                    r'Api(.*)(Get|Post|Put|Delete)', valueValue['operationId'])
                self.functionVerb = httpverb
                self.resourceName = self.operationIdRegex.group(1)

                self.functionName = '{}{}'.format(
                    self.functionVerb, self.resourceName)
                self.config[valueValue['operationId']] = SwaggerOperation(
                    valueValue['operationId'], httpverb, key, self.functionName)
        return json.dumps(self.config, default=obj_dict)


class SwaggerOperation(object):

    def __init__(self, operationId, httpverb, path, functionName):
        self.operationId = operationId
        self.httpverb = httpverb
        self.path = path
        self.functionName = functionName


def obj_dict(obj):
    return obj.__dict__

if __name__ == '__main__':
    environmentService = EnvironmentService()
    environmentService.setPythonEnv(EnvironmentSetting.local)
    swaggerService = SwaggerService()
    url = ServiceBase().getSwaggerJsonUrl()
    print(url)
    restapi = swaggerService.getPathsWithHttpVerbs(url)
    # Sorter Rest API funksjoner
    # Lager til FIL
