from bymtesting.Autentisering.AutentiseringService import *
from bymtesting.WebApi.WebApiServiceInfo import *


class LoginService:

    def __init__(self):
        self.autentiseringService = AutentiseringService(
            WebApiServiceInfo().webapiAdminNavn)
        self.bymelding = 'bymelding'

    def loginAsWebApiAdmin(self):
        getTokenResponse = self.autentiseringService.getToken(
            WebApiServiceInfo.webapiServiceId, WebApiServiceInfo.webapiAdminEpost, self.bymelding)
        if (getTokenResponse.response.status_code != 200):
            return getTokenResponse

        RequestToken.setToken(getTokenResponse.model.access_token)
        print("Logget inn som webApiAdmin")
        return getTokenResponse

    def login(self, user):
        getTokenResponse = self.autentiseringService.getToken(
            WebApiServiceInfo.webapiServiceId, user, self.bymelding)
        if (getTokenResponse.response.status_code != 200):
            return getTokenResponse

        RequestToken.setToken(getTokenResponse.model.access_token)
        print("Logget inn som" + user)
        return getTokenResponse

if __name__ == '__main__':
    # For å kjøre denne funksjonen manuelt, kjør heller
    # "TestBymeldingSetupService.py". Den setter alle servicer i riktig
    # tilstand først.
    loginService = LoginService()
    token = loginService.loginAsWebApiAdmin()
    i = 0
