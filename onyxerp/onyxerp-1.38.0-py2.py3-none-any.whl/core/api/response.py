"""
Created on 10 de jan de 2017
Abstract Response Object
@author: rinzler
"""
import json
from collections import OrderedDict


class Response(object):
    """
    Objeto response de uma requisição HTTP utilizada pelas APIs do OnyxERP
    """
    app = object
    __status_code = 200
    __decoded = None
    __content = {}
    __headers = {}

    def __init__(self, app: object):
        self.app = app

    def set_status_code(self, status_code):
        """
        Seta o status-code da requisição
        :param status_code: int
        :return: self
        """
        self.__status_code = status_code
        return self

    def get_status_code(self) -> int:
        """
        Retorna o status-code da requisição
        :return: int
        """
        return self.__status_code

    def set_decoded(self, data: OrderedDict):
        """
        Seta o objeto resultante da decodificação do response content(txt) como JSON
        :param data: OrderedDict
        :return: self
        """
        self.__decoded = data
        return self

    def get_decoded(self) -> OrderedDict:
        """
        Decodifica(se necessário) o response content(txt) como JSON, seta no atributo __decoded e retorna o resultado.
        :return: OrderedDict
        """
        if self.__decoded is None:
            try:
                self.set_decoded(json.loads(self.__content, object_pairs_hook=OrderedDict))
            except BaseException as e:
                self.app['log'].warning(str(e), exc_info=True)
                self.set_decoded(OrderedDict())
        return self.__decoded

    def set_content(self, content: str):
        """
        Seta o response content da requisição em texto plano, sem decodificar
        :param content: str
        :return: self
        """
        self.__content = content
        return self

    def get_content(self) -> str:
        """
        Retorna o response content da requisição em texto plano, sem decodificar
        :return: str
        """
        return self.__content

    def set_headers(self, headers):
        """
        Seta os response headers da requisição
        :param headers: dict
        :return: self
        """
        self.__headers = headers
        return self

    def get_headers(self) -> dict:
        """
        Retorna os response headers da requisição
        :return: dict
        """
        return self.__headers
