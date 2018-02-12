import os
from bymtesting.Lib.EnvironmentService import *


class AutentiseringUrlService:

    def __init__(self, serviceName):
        self.environmentService = EnvironmentService()
        self.serviceName = serviceName.lower()

    def getAutentiseringServiceRootUrl(self):
        env = self.environmentService.getPythonEnv()
        if env == 'local':
            return 'http://localhost:5015'

        if env == 'localdocker':
            return 'http://autentiseringservice:5015'

        if env == 'development':
            return 'https://autentisering-{}-service-dev.bymoslo.no'.format(self.serviceName)

        if env == 'testing':
            return 'https://autentisering-service-test.bymoslo.no'

        if env == 'staging':
            return 'https://autentisering-service-stage.bymoslo.no'

        # Må alltid være kommentert ut før git commit
        # if env == 'production':
        #     return 'http://autentisering-service-prod.bymoslo.no'

    def getAutentiseringServiceRootUrlForProduction(self):
        env = self.environmentService.getPythonEnv()
        if env == 'production':
            return 'http://autentisering-service-prod.bymoslo.no'
