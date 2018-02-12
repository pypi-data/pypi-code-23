import os

str = """
import unittest
import datetime
import uuid

from bymtesting.Cache.DockerTestCacheService import *
from bymtesting.Cache.CachingForTestCase import *
from bymtesting.WebApi.WebApiService import *
from bymtesting.Seed.SeedDataTemplate import *
from bymtesting.Seed.SeedDatabaseServiceData import *
from bymtesting.WebApi.LoginService import *


class TestapiControll(unittest.TestCase, CachingForTestCase):
    @classmethod
    def setUpClass(self):
        self.webapi = WebApiService()
        LoginService().loginAsWebApiAdmin()
        self.id=""
        self.navn = ""
        self.beskrivelse="" 
        self.fraDato = datetime.datetime.now()
        self.tilDato = self.fraDato + datetime.timedelta(days=1)       
       

    def setUp(self):
        print(datetime.datetime.now())
        #datatemplate = SeedDataTemplate()
        #datatemplate.createGrunnDataTemplate()
        #datatemplate.createTestDataTemplate()
        #self.testdata = SeedDatabaseServiceData(datatemplate)
        ## Choose a setup by uncommenting
        # self.setUp_delete_all_containers_pull_new_restart_everything_and_populate()
        # self.setUp_use_cached()
        # self.setUp_use_cached_only_populate()
        #self.setUp_use_non_cached(self.testdata)


    def cleanup(self):
        self.webapi.clean_and_initialize_database()

    def test_add_and_get_apiControll(self):
        self.cleanup()
        createResponse = self.webapi.createapiControll(self.navn)
        self.assertEqual(createResponse.response.status_code, 200)
        id = createResponse.model.id
        self.assertIsNotNone(id)

        getResponse = self.webapi.getapiControll(id)
        self.assertEqual(getResponse.response.status_code, 200)
        navn = getResponse.model.navn
        self.assertEqual(self.navn, navn)

    def test_get_all_apiController(self):
        getResponse = self.webapi.getapiController()
        self.assertEqual(getResponse.response.status_code, 200)
        self.assertEqual(len(getResponse.model.items), 1)

    def test_update_apiControll(self):
        self.cleanup()
        createResponse = self.webapi.createapiControll(self.navn)
        self.assertEqual(createResponse.response.status_code, 200)
        self.assertIsNotNone(createResponse.model.id)
        id = createResponse.model.id
        updatedNameToCompareWith="blabla"

        updateResponse=self.webapi.updateapiControll(id, updatedNameToCompareWith)
        self.assertEqual(updateResponse.response.status_code, 200)


        getResponse = self.webapi.getapiControll(id)
        navn = getResponse.model.navn
        self.assertIsNotNone(navn)
        self.assertEqual(navn, updatedNameToCompareWith)
    
    
    def test_delete_apiControll(self):
        self.cleanup()
        createResponse = self.webapi.createapiControll( self.navn)
        self.assertEqual(createResponse.response.status_code, 200)
        id = createResponse.model.id
        deleteResponse = self.webapi.deleteapiControll(id)
        self.assertEqual(deleteResponse.response.status_code, 200)

    # def test_create_duplicate_apiControll_navn(self):
    #     self.cleanup()
    #     createResponse = self.webapi.createapiControll(self.navn)
    #     self.assertEqual(createResponse.response.status_code, 200)
    #     id = createResponse.model.id
    #     self.assertIsNotNone(id)

    #     createResponse2 = self.webapi.createapiControll(self.navn)
    #     self.assertEqual(createResponse2.response.status_code, 400)
    #     self.assertIsNotNone(createResponse2.errorMessage)
    #     print(createResponse2.errorMessage)
    #     self.assertIn("er allerede opprettet", createResponse2.errorMessage.lower())
    


if __name__ == '__main__':
    environmentService = EnvironmentService()
    environmentService.setPythonEnv(EnvironmentSetting.local)
    environmentService.setLocalDockerTargetEnv(EnvironmentSetting.local)
    unittest.main()

"""


def createWebApi(str):
    servicePosifix = "Service"
    WebApi = ""
    str = str.lower()
    if ("servic" in str):
        splitt = str.split("service")[0]
        WebApi = splitt.capitalize() + servicePosifix
    else:
        WebApi = str.capitalize() + servicePosifix
    return WebApi


def replace_WebApi_and_apicontrollname_in_string():

    apiControllName = input("ApiControllName:")
    apiControllName = apiControllName.strip()
    if len(apiControllName) == 0:
        print("Controllername for creating test class is required...")
        exit(0)

    apiControllNameCapitalized = apiControllName.title()
    output = str.replace("apiControll", apiControllNameCapitalized)
    filename = "Test{}.py".format(apiControllNameCapitalized)

    currentDir = os.path.dirname(os.path.realpath(__file__))
    filenameWithFullpath = os.path.join(currentDir, filename)
    print("You created a new file:", filename)
    file = open(filenameWithFullpath, 'w+')
    file.write(output)


def run():
    try:
        replace_WebApi_and_apicontrollname_in_string()
    except (EOFError, InterruptedError, SystemExit):
        raise

if __name__ == '__main__':
    run()
