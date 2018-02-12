from bymtesting.WebApi.UrlService import *
from bymtesting.WebApi.WebApiService import *
import time
from bymtesting.Autentisering.AutentiseringService import *
from bymtesting.WebApi.WebApiServiceInfo import *
from bymtesting.Autentisering.AutentiseringSetupService import *
from bymtesting.Lib.EnvironmentService import *
from bymtesting.Lib.Exceptions import *
from bymtesting.Autentisering.AutentiseringServiceInfo import *


class WebApiSetupService:

    def __init__(self):
        self.webapiService = WebApiService()
        self.serviceName = WebApiServiceInfo().webapiServiceName.lower()
        self.autentiseringService = AutentiseringService(
            isRaiseResponseExceptionWhenStatus200NotOk=True, serviceName=self.serviceName)
        self.autentiseringSetupService = AutentiseringSetupService(
            self.serviceName)
        self.environmentService = EnvironmentService()
        self.urlService = UrlService()
        self.clientId = "dfe198ae-68f0-4979-9939-55d8175f9d8b"

    def addWebApiService(self):
        apiAdresse = self.urlService.getWebApiServiceRootUrl(
            pythonEnv=self.environmentService.getLocalDockerTargetEnv())
        addServiceResponse = self.autentiseringService.addServiceParams(
            apiAdresse)

    def addWebApiProsessroller(self):
        addProsessrolleResponse = self.autentiseringService.addProsessrolleParams(
            WebApiServiceInfo.webapiServiceId, WebApiServiceInfo.webapiAdminId)

    def addWebApiAdminBruker(self, epost, navn, passord):
        return self.addWebApiBruker(WebApiServiceInfo.webapiAdminId, epost, navn, passord)

    def addWebApiBruker(self, prosessrolleId, epost, navn, passord):
        payload = {'navn': navn, 'Epost': epost}
        addBrukerResponse = self.autentiseringService.addBruker(payload)
        addBrukerToProsessrolleResponse = self.autentiseringService.addBrukerToProsessrolleParams(
            prosessrolleId, addBrukerResponse.model.brukerId)

        payload = {'passord': passord}
        updateBrukerPassordResponse = self.autentiseringService.updateBrukerPassord(
            addBrukerResponse.model.brukerId, payload)

    # Denne funksjonen setter opp både AutentiseringService og WebApiService,
    # og er kun til bruk når vi tester systemene lokalt(HOST eller GUEST)
    # eller lokalt-eksternt(Docker Cloud)
    def setupWebApiWithAutentisering(self):
        response = self.autentiseringService.clean_and_initialize_database()
        response = self.webapiService.clean_and_initialize_database()
        response = self.autentiseringSetupService.setupInitialAutentiseringService()
        response = self.setupInitialWebApiService()

    def setupWebApiService(self):
        response = self.webapiService.clean_and_initialize_database()
        response = self.setupInitialWebApiService(
            isWaitForStartingService=True)

    # Denne funksjonen starter opp WebApiService med kun de data som den selv trenger uten å vite noe om de Servicer som bruker den.
    # Andre Servicer må legge seg selv inn i WebApiService via sine egne
    # xxxServiceScript
    def setupInitialWebApiService(self, isWaitForStartingService=False):
        numberRetries = 0
        numberRetriesMax = 100

        if (isWaitForStartingService):
            time.sleep(20)

        while self.webapiService.getIsServiceRunning() == False:
            if (numberRetries == numberRetriesMax):
                raise Exception(
                    'WebApiService not running. Error connecting to the service')
            print("WebApiService.getIsServiceRunning() => Waiting 10 seconds")
            numberRetries = numberRetries + 1
            time.sleep(10)

        numberRetries = 0
        keepLooping = True
        while keepLooping:
            keepLooping = self.webapiService.getIsServiceRunningWithDatabase()
            print("keeplooping:", keepLooping)
            if (keepLooping == False):
                break
            if (numberRetries == numberRetriesMax):
                raise Exception(
                    'WebApiService running, but not getting the correct ServiceTilstand. Got: ({})'.format(tilstand))
            print("WebApiService.getServiceInfoTilstand() => Waiting 10 seconds")
            numberRetries = numberRetries + 1
            time.sleep(10)

        numberRetries = 0
        while self.autentiseringService.getIsServiceRunning() == False:
            if (numberRetries == numberRetriesMax):
                raise Exception(
                    'AutentiseringService not running. Error connecting to the service')
            print("autentiseringService.getIsServiceRunning() => Waiting 10 seconds")
            numberRetries = numberRetries + 1
            time.sleep(10)

        numberRetries = 0
        keepLooping = True
        while keepLooping:
            tilstand = self.autentiseringService.getServiceInfoTilstand()
            keepLooping = tilstand.model.id != ServiceTilstandEnum().KlarForScript
            if (keepLooping == False):
                break
            if (numberRetries == numberRetriesMax):
                raise Exception(
                    'AutentiseringService running, but not getting the correct ServiceTilstand. Got: ({})'.format(tilstand))
            print("autentiseringService.getServiceInfoTilstand() => Waiting 10 seconds")
            numberRetries = numberRetries + 1
            time.sleep(10)

        # Oppsett:
        # Legge WebApiService til AutentiseringService
        # Sett opp Prosessroller og ProsessrolleRolle i AutentiseringService

        getTokenResponseForAutentiseringAdmin = self.autentiseringService.getToken(
            AutentiseringServiceInfo.ServiceId, "autentiseringadmin@bym.no", "bymelding")
        RequestToken.setToken(
            getTokenResponseForAutentiseringAdmin.model.access_token)
        print("Logget inn som AutentiseringAdmin")

        addWebApiServiceResponse = self.addWebApiService()
        addWebApiProsessrollerResponse = self.addWebApiProsessroller()
        addWebApiAdminBrukerResponse = self.addWebApiAdminBruker(
            WebApiServiceInfo.webapiAdminEpost, WebApiServiceInfo.webapiAdminNavn, "bymelding")
        print("La til WebApiAdmin")

        getTokenResponseForWebApiAdmin = self.autentiseringService.getToken(
            WebApiServiceInfo.webapiServiceId, WebApiServiceInfo.webapiAdminEpost, "bymelding")
        RequestToken.setToken(
            getTokenResponseForWebApiAdmin.model.access_token)
        print("Logget inn som WebApiAdmin")

        print("SetupInitialWebApiService OK")


if __name__ == '__main__':
    # For å kjøre denne funksjonen manuelt, kjør heller
    # "TestWebApiSetupService.py" eller "SeedDatabase.py". Disse setter alle
    # servicer i riktig tilstand først.
    environmentService = EnvironmentService()
    environmentService.setPythonEnv(EnvironmentSetting.local)
    environmentService.setLocalDockerTargetEnv(EnvironmentSetting.local)
    webApiSetupService = WebApiSetupService()
    webApiSetupService.setupWebApiService()
