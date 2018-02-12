import json
from bymtesting.Lib.JsonBase import *
from bymtesting.WebApi.WebApiService import *
from bymtesting.WebApi.LoginService import *
import datetime


class WebApiFactoyService(JsonBase):

    def __init__(self):
        self.webapiService = WebApiService()
        LoginService().loginAsWebApiAdmin()

    def createDevelopers(self, developers):
        for developer in developers:
            createResponse = self.webapiService.createDeveloper(developer.navn)
            developer.id = createResponse.model.id
        return developers
