from bymtesting.Autentisering.AutentiseringServiceInfo import *
from bymtesting.Autentisering.AutentiseringService import *
import time


class AutentiseringSetupService:

    def __init__(self, serviceName):
        self.autentiseringService = AutentiseringService(
            serviceName=serviceName)

    # Denne funksjonen starter opp AutentiseringService med kun de data som den selv trenger uten å vite noe om de Servicer som bruker den.
    # Andre Servicer må legge seg selv inn i AutentiseringService via sine
    # egne xxxServiceScript
    def setupInitialAutentiseringService(self, waitForStartingService=False):
        numberRetries = 0
        numberRetriesMax = 10

        if(waitForStartingService):
            # TEMP wait for ReverseProxy
            time.sleep(180)    # 3min

        while self.autentiseringService.getIsServiceRunning() == False:
            if(numberRetries == numberRetriesMax):
                raise Exception(
                    'Service not running. Error connecting to the service')
            print("getIsServiceRunning() => Waiting 5 seconds")
            numberRetries = numberRetries + 1
            time.sleep(5)

        numberRetries = 0
        while self.autentiseringService.getServiceInfoTilstand().model.id != ServiceTilstandEnum().KlarForScript:
            if(numberRetries == numberRetriesMax):
                raise Exception(
                    'Service running, but not getting the correct ServiceTilstand')
            print("getServiceInfoTilstand() => Waiting 5 seconds")
            numberRetries = numberRetries + 1
            time.sleep(5)

        addAutentiseringAdminResponse = self.autentiseringService.addAutentiseringAdminParams(
            "autentiseringadmin@bym.no", "TheAutentiseringAdmin", "bymelding")
        if (addAutentiseringAdminResponse.response.status_code != 200):
            return addAutentiseringAdminResponse
        print("La til AutentiseringAdmin")

        getTokenResponse = self.autentiseringService.getToken(
            AutentiseringServiceInfo.ServiceId, "autentiseringadmin@bym.no", "bymelding")
        if (getTokenResponse.response.status_code != 200):
            return getTokenResponse

        RequestToken.setToken(getTokenResponse.model.access_token)
        print("Logget inn som autentiseringadmin@bym.no")

        print("SetupInitialAutentiseringService OK")
        return getTokenResponse

# if __name__ == '__main__':
#     # os.environ["PYTHON_ENV"] = "staging"
#     # autentiseringScript = AutentiseringSetupService(serviceName="")
#     # autentiseringScript.setupInitialAutentiseringService(
#     #     waitForStartingService=True)
