from bymtesting.Lib.RequestService import *
from bymtesting.Autentisering.AutentiseringUrlService import *
import json
from bymtesting.Autentisering.AutentiseringServicePayload import *
from bymtesting.Lib.Exceptions import *
from bymtesting.Lib.ServiceBase import *


class AutentiseringService(ServiceBase):

    def printObjectToJson(self, object):
        print(json.dumps(object, default=self.obj_dict))

    def obj_dict(self, obj):
        return obj.__dict__

    def __init__(self, isRaiseResponseExceptionWhenStatus200NotOk=True, serviceName=""):
        ServiceBase.__init__(self, isRaiseResponseExceptionWhenStatus200NotOk)
        self.root = AutentiseringUrlService(
            serviceName).getAutentiseringServiceRootUrl()

    def addAutentiseringAdmin(self, payload):
        requestURL = '{}/api/autentiseringadmin'.format(self.root)
        return self.postRequest(requestURL, payload, BrukerViewModel)

    def addAutentiseringAdminParams(self, epost, navn, passord):
        payload = {'epost': epost, 'navn': navn, 'passord': passord}
        return self.addAutentiseringAdmin(payload)

    def getAutentiseringServiceRoller(self):
        requestURL = '{}/api/roller'.format(self.root)
        return self.getRequest(requestURL, RollerViewModel)

    def addBruker(self, payload):
        requestURL = '{}/api/brukere'.format(self.root)
        return self.postRequest(requestURL, payload, BrukerViewModel)

    def updateBruker(self, bruker):
        requestURL = '{}/api/brukere/{brukerId}'.format(
            self.root, brukerId=bruker.brukerId)
        return self.putRequest(requestURL, bruker.__dict__, BrukerViewModel)

    def updateBrukerPassord(self, brukerId, payload):
        requestURL = '{}/api/brukere/{brukerId}/passord'.format(
            self.root, brukerId=brukerId)
        return self.putRequest(requestURL, payload, GenericViewModel)

    def updateBrukerPassordParams(self, brukerId, passord):
        payload = {"passord": passord}
        requestURL = '{}/api/brukere/{brukerId}/passord'.format(
            self.root, brukerId=brukerId)
        return self.putRequest(requestURL, payload, GenericViewModel)

    def getBrukerByEpost(self, epost):
        requestURL = '{}/api/brukere/epost/{epost}'.format(
            self.root, epost=epost)
        return self.getRequest(requestURL, BrukerViewModel)

    def getBrukere(self):
        requestURL = '{}/api/brukere'.format(self.root)
        return self.getRequest(requestURL, BrukereViewModel)

    def addService(self, payload):
        requestURL = '{}/api/servicer'.format(self.root)
        return self.postRequest(requestURL, payload, ServiceViewModel)

    def updateService(self, service):
        requestURL = '{}/api/servicer/{serviceId}'.format(
            self.root, serviceId=service.serviceId)
        return self.putRequest(requestURL, service.__dict__, ServiceViewModel)

    def getService(self, serviceId):
        requestURL = '{}/api/servicer/{serviceId}'.format(
            self.root, serviceId=serviceId)
        return self.getRequest(requestURL, ServiceViewModel)

    def getServicer(self):
        requestURL = '{}/api/servicer'.format(self.root)
        return self.getRequest(requestURL, ServicerViewModel)

    def deleteService(self, serviceId):
        requestURL = '{}/api/servicer/{serviceId}'.format(
            self.root, serviceId=serviceId)
        return self.deleteRequest(requestURL)

    def addService(self, payload):
        requestURL = '{}/api/servicer'.format(self.root)
        return self.postRequest(requestURL, payload, ServiceViewModel)

    def addServiceParams(self, apiAdresse):
        payload = {'apiAdresse': apiAdresse}
        requestURL = '{}/api/servicer'.format(self.root)
        return self.postRequest(
            requestURL, payload, ServiceViewModel
        )  # api/prosessroller only POST and DELETE because a Prosessrolle can not be changed after creation.

    def addProsessrolle(self, serviceId, prosessrolle):
        requestURL = '{}/api/servicer/{serviceId}/prosessroller'.format(
            self.root, serviceId=serviceId)
        return self.postRequest(requestURL, prosessrolle,
                                ProsessrolleViewModel)

    def addProsessrolleParams(self, serviceId, prosessrolleId):
        payload = {'eierrolleId': prosessrolleId}
        requestURL = '{}/api/servicer/{serviceId}/prosessroller'.format(
            self.root, serviceId=serviceId)
        return self.postRequest(requestURL, payload, ProsessrolleViewModel)

    def deleteProsessrolle(self, serviceId, eierrolleId):
        requestURL = '{}/api/servicer/{serviceId}/prosessroller/{eierrolleId}'.format(
            self.root, serviceId=serviceId, eierrolleId=eierrolleId)
        return self.deleteRequest(requestURL)

    def getProsessrolle(self, serviceId, eierrolleId):
        requestURL = '{}/api/servicer/{serviceId}/prosessroller/{eierrolleId}'.format(
            self.root, serviceId=serviceId, eierrolleId=eierrolleId)
        return self.getRequest(requestURL, ProsessrolleViewModel)

    def getProsessroller(self, serviceId):
        requestURL = '{}/api/servicer/{serviceId}/prosessroller'.format(
            self.root, serviceId=serviceId)
        return self.getRequest(requestURL, ProsessrollerViewModel)

    def addProsessrolleRolle(self, prosessrolleId, prosessrolleRolle):
        requestURL = '{}/api/prosessroller/{prosessrolleId}/prosessrolleroller'.format(
            self.root, prosessrolleId=prosessrolleId)
        return self.postRequest(requestURL, prosessrolleRolle, RolleViewModel)

    def addProsessrolleRolleParams(self, prosessrolleId,
                                   prosessrolleRolleServiceId,
                                   prosessrolleRolleId):
        prosessrolleRolle = {
            'ProsessrolleRolleId': prosessrolleRolleId,
            'ProsessrolleRolleServiceId': prosessrolleRolleServiceId
        }
        requestURL = '{}/api/prosessroller/{prosessrolleId}/prosessrolleroller'.format(
            self.root, prosessrolleId=prosessrolleId)
        return self.postRequest(requestURL, prosessrolleRolle, RolleViewModel)

    def deleteProsessrolleRolle(self, prosessrolleId, prosessrolleRolleId):
        requestURL = '{}/api/prosessroller/{prosessrolleId}/prosessrolleroller/{prosessrolleRolleId}'.format(
            self.root,
            prosessrolleId=prosessrolleId,
            prosessrolleRolleId=prosessrolleRolleId)
        return self.deleteRequest(requestURL)

    def addBrukerToProsessrolle(self, prosessrolleId, prosessrollebruker):
        requestURL = '{}/api/prosessroller/{prosessrolleId}/brukere'.format(
            self.root, prosessrolleId=prosessrolleId)
        return self.postRequest(requestURL, prosessrollebruker,
                                BrukerTilgangViewModel)

    def addBrukerToProsessrolleParams(self, prosessrolleId, brukerId):
        payload = {
            'brukerId': brukerId,
            'clientId': "dfe198ae-68f0-4979-9939-55d8175f9d6b"
        }
        requestURL = '{}/api/prosessroller/{prosessrolleId}/brukere'.format(
            self.root, prosessrolleId=prosessrolleId)
        return self.postRequest(requestURL, payload, BrukerTilgangViewModel)

    def deleteBrukerFromProsessrolle(self, prosessrolleId, brukerId):
        requestURL = '{}/api/prosessroller/{prosessrolleId}/brukere/{brukerId}'.format(
            self.root, prosessrolleId=prosessrolleId, brukerId=brukerId)
        return self.deleteRequest(requestURL)

    def getToken(self, serviceId, epost, passord):
        payload = {'serviceId': serviceId, 'epost': epost, "passord": passord}
        requestUrl = '{}/api/token'.format(self.root)
        # postRequest er riktig selv om funksjonen heter getToken. Gjelder
        # spesielt token genering.
        return self.postRequest(requestUrl, payload, TokenViewModel)

    def postGlemtPassord(self, serviceId, epost):
        payload = {'serviceId': serviceId, 'epost': epost}
        requestUrl = '{}/api/glemtpassord'.format(self.root)
        # postRequest er riktig selv om funksjonen heter getToken. Gjelder
        # spesielt token genering.
        return self.postRequest(requestUrl, payload, GenericViewModel)

    # The key that you recieved by running glemtPassord() function which sent
    # to your email
    def oppdaterGlemtPassord(self, nyttpassord, key):
        payload = {'key': key, 'nyttpassord': nyttpassord}
        requestUrl = '{}/api/glemtpassord'.format(self.root)
        return self.putRequest(requestUrl, payload, GenericViewModel)

    def postSendingEmail(self, epost, subject, bodyText):
        payload = {'epost': epost, "subject": subject, 'body': bodyText}
        requestUrl = '{}/api/epost'.format(self.root)
        return self.postRequest(requestUrl, payload, GenericViewModel)

    def getIsServiceRunning(self):
        print("getIsServiceRunning")
        try:
            self.request.get(self.root)
        except requests.exceptions.ConnectionError:
            return False
        except requests.packages.urllib3.exceptions.NewConnectionError:
            return False
        except requests.packages.urllib3.exceptions.ConnectionError:
            return False
        else:
            return True

    def getIsServiceRunningWithDatabase(self):
        print("getIsServiceRunningWithDatabase")
        try:
            requestURL = '{}/api/healthcheck'.format(self.root)
            result = self.request.get(requestURL)
            return result.status_code == 200
        except requests.exceptions.ConnectionError:
            return False
        except requests.packages.urllib3.exceptions.NewConnectionError:
            return False
        except requests.packages.urllib3.exceptions.ConnectionError:
            return False
        else:
            return True

    def updateServiceInfoTilstandParams(self, serviceTilstandId):
        requestURL = '{}/api/serviceinfotilstand'.format(self.root)
        payload = {'serviceinfotilstand': serviceTilstandId}
        return self.putRequest(requestURL, payload, GenericViewModel)

    def getServiceInfoTilstand(self):
        requestURL = '{}/api/serviceinfotilstand'.format(self.root)
        return self.getRequest(requestURL, ServiceInfoTilstandViewModel)

    def getServiceInfoTilstander(self):
        requestURL = '{}/api/serviceinfotilstander'.format(self.root)
        return self.getRequest(requestURL, ServiceInfoTilstanderViewModel)
