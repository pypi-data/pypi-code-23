from bymtesting.WebApi.WebApiService import *
from bymtesting.WebApi.WebApiSetupService import *
from bymtesting.Autentisering.AutentiseringService import *
from bymtesting.Lib.EnvironmentService import *
from bymtesting.WebApi.UrlService import *
from bymtesting.WebApi.LoginService import *
from bymtesting.Seed.SeedDatabaseServiceData import *
from bymtesting.Seed.SeedDataTemplate import *
from bymtesting.WebApi.WebApiServiceInfo import *


class SeedDatabase:

    def __init__(self):
        self.autentiseringService = AutentiseringService(
            WebApiServiceInfo.webapiServiceName)
        self.loginService = LoginService()
        self.WebApiService = WebApiService()
        self.WebApiSetupService = WebApiSetupService()
        self.environmentService = EnvironmentService()

    def seedDatabase(self):
        # Denne funksjonen sletter også AutentiseringService sin database.
        response = self.WebApiSetupService.setupWebApiWithAutentisering(
        )

        datatemplate = SeedDataTemplate()
        datatemplate.createGrunnDataTemplate()
        datatemplate.createTestDataTemplate()
        self.testdata = SeedDatabaseServiceData(datatemplate)
        self.testdata.populate()


if __name__ == '__main__':
    environmentService = EnvironmentService()
    environmentService.setPythonEnv(EnvironmentSetting.development)
    # environmentService.setLocalDockerTargetEnv(EnvironmentSetting.local)
    seed = SeedDatabase()
    seed.seedDatabase()
