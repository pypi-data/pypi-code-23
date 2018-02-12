import json
import datetime
from bymtesting.Lib.JsonBase import *


class ResponseModel(object):

    def __init__(self, response, viewmodel, errorMessage):
        self.response = response
        self.errorMessage = errorMessage
        if(response.ok == False):
            self.model = EmptyViewModel()
        else:
            self.model = viewmodel

    def getModelAsJson(self):
        return json.dumps(self.model.__dict__)


class EmptyViewModel(object):

    def __init__(self,):
        self.empty = ""


class GenericViewModel(object):

    def __init__(self, model):
        self.model = model


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


class StringListViewModel(object):

    def __init__(self, stringList):
        self.stringList = []
        self.__len__ = self.stringList.__len__
        for string in stringList:
            self.stringList.append(string)
