import json
import os
from collections import OrderedDict

from rinzler.exceptions.invalid_input_exception import InvalidInputException
from onyxerp.core.services.generator import simpleflake


class BaseService(object):
    """
    BaseService
    """
    __app = object()
    __payload = dict()
    __jwt_data = dict()
    __jwt = str()
    uupfid = object()

    def __init__(self, app, param=None):
        self.__app = app

    def set_payload(self, payload: str()):
        """

        :param payload:
        :return:
        """
        try:
            self.set_payload_obj(json.loads(payload, object_pairs_hook=OrderedDict))
        except Exception as e:
            raise InvalidInputException("JSON inválido ou mal-formatado.")
        return self

    def set_payload_obj(self, payload: dict()):
        """

        :param payload:
        :return:
        """
        self.__payload = payload
        return self

    def get_payload(self):
        """

        :return:
        """
        return self.__payload

    def set_jwt_data(self, jwt_data: dict()):
        """

        :param jwt_data:
        :return:
        """
        self.__jwt_data = jwt_data
        return self

    def get_jwt_data(self):
        """

        :return:
        """
        return self.__jwt_data

    def set_jwt(self, token: str()):
        """

        :param token:
        :return:
        """
        self.__jwt = token
        return self

    def get_jwt(self):
        """

        :return:
        """
        return self.__jwt

    def set_uupfid(self, uupfid: object()):
        """

        :param uupfid:
        :return:
        """
        self.uupfid = uupfid
        return self

    @staticmethod
    def get_uniqid(bytes=15) -> str:
        """

        :param bytes: int
        :return: str
        """
        return str(simpleflake(int(os.urandom(4).hex().upper(), 16)))
