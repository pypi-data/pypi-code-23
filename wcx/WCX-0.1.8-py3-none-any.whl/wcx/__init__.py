from Crypto.Cipher import AES
import base64
import base58
from binascii import hexlify, unhexlify
import json
import requests

import random
from decimal import *
import sys

import time
import hashlib
import hmac

from urllib.parse import urlencode


# import urllib3
# import urlparse3

# import pkg_resources
# from . import pbkdf2

import six

VERSION=2
# pkg_resources.get_distribution("crypto-wallet").version

class WcxInvalidResponseError(Exception):
    """Thrown when we receive an unexpected/unparseable response from Block.io"""

class WcxUnknownError(Exception):
    """Thrown when response status codes are outside of 200-299, 419-420, 500-599."""

class WcxAPIThrottleError(Exception):
    """Thrown when API call gets throttled at Block.io."""

class WcxAPIInternalError(Exception):
    """Thrown on 500-599 errors."""

class WcxAPIError(Exception):
    """Thrown when block.io API call fails."""


class Wcx(object):
    global payload

    def __init__(self, api_key, secret_key, version = 1):
        # initiate the object
        self.api_key = api_key
        self.secret_key = secret_key
        self.version = version
        self.clientVersion = VERSION
        self.encryption_key = None
        self.base_url = 'https://wcx.io/api/v'+str(version)+'/API_CALL'

    def __getattr__(self, attr, *args, **kwargs):

        def hook(*args, **kwargs):
            return self.api_call(attr, **kwargs)

        return hook

    def api_call(self, method, **kwargs):
        # the actual API call

        # http parameters
        payload = {}
        headers = {}

        if self.api_key is not None:
            payload["api_key"] = self.api_key 

        if self.secret_key is not None:
            payload["secret_key"] = self.secret_key

            payload["request"] = method
           
            payload["nonce"] = str(int(time.time()))+'-wcx'
           
            
            payload.update(kwargs)



        # six.print_(payload)
        # six.print_(json.dumps(payload).encode('utf-8'))
        post_data = base64.b64encode(json.dumps(payload).encode('utf-8'))
        #print(payload)
        
        signature = hmac.new(bytearray(self.secret_key,'utf-8'), post_data, hashlib.sha384).hexdigest()
        
        headers["X-WCX-APIKEY"] = self.api_key
        headers["X-WCX-PAYLOAD"] = post_data
        headers["X-WCX-SIGNATURE"] = signature
        # if kwargs is not None:
        #     base_url = self.base_url.replace('API_CALL',method)
        #     url_parts = list(urlparse3.parse_url(base_url))
        #     query = dict(urlparse3.parse_qsl(url_parts[4]))
        #     query.update(kwargs)
        #     url_parts[4] = urllib3.urlencode(query)
        #     url = urlparse3.urlunparse(url_parts) 
        # else:
        #     url = self.base_url.replace('API_CALL',method)

        url = self.base_url.replace('API_CALL',method)


       
        # update the parameters with the API key
        session = requests.session()
        response = session.post(url, data = payload, headers = headers)
        status_code = response.status_code
        #print(response)
       
        try:
            response = response.json() # convert response to JSON                        
        except:
            response = {}

       
        session.close() # we're done with it, let's close it
        if not ('status' in response.keys()):
            # unexpected response
            raise WcxInvalidResponseError("Failed, invalid response received from Crypto Wallet, method %s" % method)
        elif ('status' in response.keys()) and (response['status'] == '0'):

            if 'status' in response.keys() and 'result' in response.keys():
                # call failed, and error_message was provided
                raise WcxAPIError('Failed: '+response['result'])
            else:
                # call failed, and error_message was NOT provided
                raise WcxAPIError("Failed, error_message was not provided, method %s" % method)

        elif 500 <= status_code <= 599:
            # using the status_code since a JSON response was not provided
            raise WcxAPIInternalError("API call to Crypto Wallet failed externally, method %s" % method)
        elif 419 <= status_code <= 420:
            # using the status_code since a JSON response was not provided
            raise WcxAPIThrottleError("API call got throttled by rate limits at Crypto Wallet, method %s" % method)
        elif not (200 <= status_code <= 299):
            # using the status_code since a JSON response was not provided
            raise WcxUnknownError("Unknown error occurred when querying Crypto Wallet, method %s" % method)

        return response

