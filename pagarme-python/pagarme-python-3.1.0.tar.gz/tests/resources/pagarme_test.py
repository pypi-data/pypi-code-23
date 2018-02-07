from datetime import datetime, timedelta
from pagarme.resources import handler_request
import requests
import time


AUTH_TEST = handler_request.authentication_key(None, True)

REQUESTBIN_BASE = 'https://requestb.in/api/v1/bins'


def create_postback_url():
    request_bin_response = requests.post(REQUESTBIN_BASE)
    valid_resquest_bin = handler_request.validate_response(request_bin_response)
    if valid_resquest_bin:
        return 'http://requestb.in/'+valid_resquest_bin['name']
    else:
        return 'http://teste.url.com'


def generate_timestamp():
    return int(time.mktime((datetime.now()+timedelta(days=3)).timetuple()) * 1000)
