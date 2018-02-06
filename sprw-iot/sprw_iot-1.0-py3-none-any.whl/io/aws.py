import requests
import json
from .config import Config
from easydict import EasyDict as edict
from .exceptions import ValidationError, NetworkError, ServerError, Error
import sys
class AwsService:

    __aws_credentials = None
    __access_token = None
    __headers = None
    __network_error_message = 'Please check your internet connection. Could not connect with ' + Config.APP_URL
    __server_error_message = 'SPRW Server Error'
    __generic_error_message = 'Failed to communicate with the server'

    def __init__(self, access_token):

        self.__set_access_token(access_token)
    
    def __set_access_token(self, access_token):
        self.__access_token = access_token
        self.__headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + access_token
        }
        self.__fetch_aws_credentials()

    def get_aws_credentials(self):
        return self.__aws_credentials

    def __fetch_aws_credentials(self):
        try:
            json_response = requests.get(Config.SPRWIO_GATEWAY_URL + 'aws-credentials', headers=self.__headers)

        except requests.exceptions.ConnectionError:
            raise NetworkError(0, self.__network_error_message)

        try:
            response = edict(json.loads(json_response.text))
        except ValueError as e:
            raise ServerError(json_response.status_code,
                              self.__server_error_message)


        if json_response.status_code == 200 or json_response.status_code == 201:
            self.__aws_credentials = response.data
        elif json_response.status_code == 500:    
            if hasattr(response, 'message'):
                raise ServerError(json_response.status_code, response.message)
            else:
                raise ServerError(json_response.status_code, response)

        else:
            raise Error(Exception(response))


