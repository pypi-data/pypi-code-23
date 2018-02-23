from .settings import CBCI_SERVER
import requests
import datetime
import base64
import logging
import fire
import json

logger = logging.getLogger(__name__)


class Connect():
    """ API Wrapper for CBCI goldmine

       Usage:
           from cbci_wrapper import Connect
           cbci_connect = Connect()
           cbci_connect.get_transactions(
                        biller_code="MWSIN",
                        account_no="54537170")

    """

    def __init__(self,
                 url=CBCI_SERVER['URL'],
                 username=CBCI_SERVER['USERNAME'],
                 secret=CBCI_SERVER['SECRET'],
                 ):
        self.url = url
        self.secret = secret
        self.username = username
        self.authorization = self.encode_authorization()
        try:
            self.jwt_token = self.get_jwt()
        except Exception as e:
            logger.error("Failed to get token")
            raise e

    def encode_authorization(self):
        """ Convert username and secret to base64"""
        username = self.username
        secret = self.secret
        now = datetime.datetime.now()
        now = now.strftime('%m/%d/%Y %H:%M:%S')
        data = "{}|{}|{}".format(username, secret, now)
        authorization = base64.b64encode(data.encode())
        return authorization

    def get_jwt(self):
        """ Grab JWT everytime since it has expiration """
        logging.info("Grabing JWT")
        url = "{}/v2/oauth/accesstoken".format(self.url)
        headers = {
            "Authorization": "Basic {}".format(self.authorization.decode())
        }
        response = requests.post(url=url, headers=headers)
        try:
            r = response.json()
        except json.decoder.JSONDecodeError as jde:
            return jde
        return r

    def get_transactions(self, biller_code, account_no):
        """ Get Transactions of account based on biller code

        Parameter:
            biller_code:
            account_no
        """
        logging.info(
            "Grabing Transactions for {}: {}".format(
                biller_code,
                account_no))
        url = "{}/api/getdata".format(self.url)
        data = {
            "billerCode": biller_code,
            "accountNo": account_no,
            "apiKey": self.secret,
            "accessToken": self.jwt_token['accessToken'],
        }
        response = requests.post(url, data=data)
        return response.json()


if __name__ == '__main__':
    fire.Fire(Connect)
