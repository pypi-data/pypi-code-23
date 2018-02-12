from requests import Response
import json
import collections
from bymtesting.WebApi.LoginService import *
from bymtesting.WebApi.UrlService import *
from bymtesting.WebApi.WebApiServiceInfo import *
from bymtesting.Autentisering.AutentiseringService import *
from bymtesting.Lib.SwaggerService import *
from bymtesting.Lib.Api import *
from bymtesting.Lib.ServiceBase import *


class ActualDictionaryService:

    def __init__(self):
        self.ServiceEndpointInfo = WebApiServiceInfo()
        self.root = UrlService().getWebApiServiceRootUrl()

    def createActual(self):
        dictionary = {}
        url = ServiceBase().getSwaggerJsonUrl()
        pathDict = SwaggerService().getPathDictFromSwagger(url)
        result = AutentiseringService().getProsessroller(
            self.ServiceEndpointInfo.webapiServiceId)

        ApiList = []
        for rolle in result.model.prosessroller:
            user = self.ServiceEndpointInfo.GetUsergivenRolle(
                rolle.eierrolleNavn)
            result = LoginService().login(user)
            for keyEndPoints, valueHttpVerbs in pathDict.items():
                for httpVerb, value in valueHttpVerbs.items():
                    self.createApiList(httpVerb, keyEndPoints,
                                       value.get('parameters'), ApiList)

            dictionary[rolle.eierrolleNavn] = ApiList
            ApiList = []
        roleAnonym = 'Anonym/Public'
        RequestToken.removeToken()
        for key, value in pathDict.items():
            for httpverb, valueValue in value.items():
                self.createApiList(
                    httpverb, key, valueValue.get('parameters'), ApiList)

        dictionary[roleAnonym] = ApiList
        ApiList = []
        return dictionary

    def createApiList(self, httpVerb, url, parameterList, ApiList):

        if (url == '/api/avtaler'):
            tets = ""

        urlWithInsertedParameters = SwaggerService(
        ).InsertValueForParameters(url, parameterList)

        urlToCall = self.root + urlWithInsertedParameters

        Response = RequestService().generic(urlToCall, httpVerb)

        ApiList.append(Api(httpVerb + ' ' + url,
                           self.mapStatusCode(Response.status_code)))

    def mapStatusCode(self, statusCode):
        if(statusCode == requests.codes.forbidden or statusCode == requests.codes.unauthorized):
            return 0
        else:
            return 1
