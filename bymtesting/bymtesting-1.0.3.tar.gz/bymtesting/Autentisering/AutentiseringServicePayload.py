import json


class ResponseModel(object):

    def __init__(self, response, viewmodel, errorMessage):
        self.response = response
        self.errorMessage = errorMessage
        if (response.ok == False):
            self.model = EmptyViewModel()
        else:
            self.model = viewmodel

    def getModelAsJson(self):
        return json.dumps(self.model.__dict__)


class GenericViewModel(object):

    def __init__(self, model):
        self.model = model


class EmptyViewModel(object):

    def __init__(self):
        self.empty = ""


class ResponseItemModel(object):

    def __init__(self, item):
        self.__dict__ = item

    def getModelAsJson(self):
        return json.dumps(self.__dict__)


class ResponseItemsModel(object):

    def __init__(self, items):
        self.items = []
        self.__len__ = self.items.__len__
        for item in items:
            self.items.append(ResponseItemModel(item))


class BrukerViewModel(object):

    def __init__(self, bruker):
        # enables intellisense
        self.brukerId = ""
        self.navn = ""
        self.epost = ""
        # overwrites __dict__, but the intellisense still works.
        self.__dict__ = bruker


class TokenViewModel(object):

    def __init__(self, token):
        self.access_token = ""
        self.exp = ""
        self.__dict__ = token


class BrukereViewModel(object):

    def __init__(self, brukere):
        self.brukere = []
        for bruker in brukere:
            self.brukere.append(BrukerViewModel(bruker))


class ServiceViewModel(object):

    def __init__(self, service):
        # enables intellisense
        self.serviceId = ""
        self.serviceNavn = ""
        self.apiAdresse = ""
        # overwrites __dict__, but the intellisense still works.
        self.__dict__ = service


class ServicerViewModel(object):

    def __init__(self, servicer):
        self.servicer = []
        for service in servicer:
            self.servicer.append(ServiceViewModel(service))


class ProsessrolleViewModel(object):

    def __init__(self, prosessrolle):
        # enables intellisense
        self.serviceId = ""
        self.eierrolleId = ""
        self.eierrolleNavn = ""
        self.__dict__ = prosessrolle


class ProsessrollerViewModel(object):

    def __init__(self, prosessroller):
        self.prosessroller = []
        for prosessrolle in prosessroller:
            self.prosessroller.append(ProsessrolleViewModel(prosessrolle))


class RolleViewModel(object):

    def __init__(self, rolle):
        # enables intellisense
        self.rolleId = ""
        self.navn = ""
        # overwrites __dict__, but the intellisense still works.
        self.__dict__ = rolle


class RollerViewModel(object):

    def __init__(self, roller):
        self.roller = []
        for rolle in roller:
            self.roller.append(RolleViewModel(rolle))


class BrukerTilgangViewModel(object):

    def __init__(self, bruker):
        # enables intellisense
        self.brukerId = ""
        self.prosessrolleId = ""
        self.clientId = ""
        # overwrites __dict__, but the intellisense still works.
        self.__dict__ = bruker


class BrukerTilgangViewModel(object):

    def __init__(self, model):
        # enables intellisense
        self.brukerId = ""
        self.prosessrolleId = ""
        self.clientId = ""
        # overwrites __dict__, but the intellisense still works.
        self.__dict__ = model


class ServiceTilstandEnum(object):

    def __init__(self):
        self.StarterOpp = 1
        self.KlarForScript = 2
        self.KlarTilBruk = 3


class ServiceInfoTilstandViewModel(object):

    def __init__(self, model):
        self.id = ""
        self.navn = ""
        self.__dict__ = model


class ServiceInfoTilstanderViewModel(object):

    def __init__(self, tilstander):
        self.tilstander = []
        for tilstand in tilstander:
            self.tilstander.append(ServiceInfoTilstandViewModel(tilstand))
