#!/usr/local/bin/python3.5
# -*- coding: utf-8 -*-

__author__ = "Identidad"
__copyright__ = "Copyright (C) Identidad."

__revision__ = "$Id$"
__version__ = "0.0.1"

import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
import urllib3
urllib3.disable_warnings()

__all__ = ['Client']

# url account
account_url = 'https://api.identidadsms.net/rest/account'
# url tocken
url_token = 'https://api.identidadsms.net/rest/auth'
# url send sms
url_send_sms = 'https://api.identidadsms.net/rest/send_sms'


class Client():
    def __init__(self, user, password):
        """

        :param user:
        :param password:
        """
        self.user = user
        self.password = password

    def __request_account(self):
        """
        Realiza la solicitud de la cuenta
        """
        rsp = None
        try:
            auth = (self.user, self.password)
            r = requests.get(account_url, auth=auth, verify=False)
            rsp = r.json()
        except requests.exceptions.RequestException as err:
            print(err)

        return rsp

    def __request_token(self):
        """
        Realiza la solicitud del tocken
        """
        rsp = None
        try:
            auth = (self.user, self.password)
            r = requests.get(url_token, auth=auth, verify=False)
            rsp = r.json()
        except requests.exceptions.RequestException as err:
            print(err)

        return rsp

    def __request_send_sms(self, token, data):
        """
        Realiza la solicitud de envio del mensaje
        """
        rsp = None
        headers = {
            "Authorization": "Bearer {}".format(token),
            "Content-Type": data.content_type
        }

        try:
            r = requests.post(url_send_sms, headers=headers, data=data.to_string(), verify=False)
            rsp = r.json()
        except requests.exceptions.RequestException as err:
            print(err)

        return rsp

    def send_sms(self, **kwargs):
        """
        Envia SMS
        to="+15558675309",
        from_="+15017250604",
        body="Hello from Python!"
        """
        to = kwargs['to']
        from_ = kwargs['from_']
        body = kwargs['body']

        # Solicita la cuenta del usuario
        account = self.__request_account()
        if not account:
            return
        # verifica si la respuesta presenta error
        if "error_message" in account:
            print(account)
            return

        self.account = account[0]

        # Solicita token
        token = self.__request_token()
        if not token:
            return
        if "error_message" in token:
            print(token)
            return
        self.token = token['token']

        # Datos form
        multipart_data = MultipartEncoder(
            fields={
                "acc_id": str(self.account['id']),
                "from": from_,
                "message": body,
                "to": to
            }
        )

        # Envia SMS
        rsp_sms = self.__request_send_sms(self.token, multipart_data)
        if not rsp_sms:
            return

        print(rsp_sms)
