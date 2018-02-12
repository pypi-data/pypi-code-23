import datetime
import pydash
import json
from bymtesting.Lib.JsonBase import *
from bymtesting.Lib.EnvironmentService import *
from bymtesting.WebApi.WebApiService import *
import jsonpickle
from bymtesting.WebApi.LoginService import *
from bymtesting.WebApi.WebApiFactoryService import *


class SeedDatabaseServiceData:

    def __init__(self, datatemplate):
        self.environmentService = EnvironmentService()
        self.WebApiService = WebApiService()
        self.developers = datatemplate.developers

    def _buildDataTemplate(self):
        LoginService().loginAsWebApiAdmin()
        WebApiFactoryService = WebApiFactoyService()
        WebApiFactoryService.createDevelopers(self.developers)
        if (self.environmentService.getPythonEnv() != 'production'):
            print("caching data for all except production env.")

    def populate(self, useCache=False, updateCache=False):
        if (useCache == True and updateCache == False):
            self._cacheLoadDataForFasterDebugging()
            return

        self._buildDataTemplate()

        if (useCache == True and updateCache == True):
            self._cacheSaveDataForFasterDebugging()

    def _cacheLoadDataForFasterDebugging(self):
        cacheDirectory = os.path.join(os.path.dirname(__file__), "Cache")
        if not os.path.exists(cacheDirectory):
            raise Exception("No Cache directory." + cacheDirectory)

        self._cacheLoadProperty(self.developers, "developers")

    def _cacheLoadProperty(self, classProperty, propertyname):
        jsonFile = ""
        relativeFilename = os.path.join(
            os.path.dirname(__file__), "Cache",
            "Test_cache_{}.cache".format(propertyname))
        with open(relativeFilename, 'r') as the_file:
            jsonFile = the_file.read()
        classProperty = jsonpickle.decode(jsonFile)

    def _cacheSaveDataForFasterDebugging(self):
        cacheDirectory = os.path.join(os.path.dirname(__file__), "Cache")
        if not os.path.exists(cacheDirectory):
            os.makedirs(cacheDirectory)

        self._cacheSaveProperty(self.developers, "developers")

    def _cacheSaveProperty(self, classProperty, propertyname):
        relativeFilename = os.path.join(
            os.path.dirname(__file__), "Cache",
            "Test_cache_{}.cache".format(propertyname))
        with open(relativeFilename, 'w') as the_file:
            the_file.write(jsonpickle.encode(classProperty))
