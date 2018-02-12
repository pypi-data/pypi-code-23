from bymtesting.Lib.EnvironmentService import *
from bymtesting.WebApi.WebApiServiceInfo import *


class UrlService:

    def __init__(self):
        self.environmentService = EnvironmentService()
        self.serviceName = WebApiServiceInfo().webapiServiceName.lower()

    def getWebApiServiceRootUrl(self, pythonEnv=None):
        env = pythonEnv
        if (pythonEnv == None):
            env = self.environmentService.getPythonEnv()

        if env == 'local':
            return "http://localhost:portnumber"

        if env == 'localdocker':
            return 'http://{}service:portnumber'.format(self.serviceName)

        if env == 'development':
            return 'https://{}-service-dev.bymoslo.no'.format(self.serviceName)

        if env == 'testing':
            return 'https://{}-service-test.bymoslo.no'.format(self.serviceName)

        if env == 'staging':
            return 'https://{}-service-stage.bymoslo.no'.format(self.serviceName)

        if env == 'https':
            return 'https://{}-service-https.bymoslo.no'.format(self.serviceName)
