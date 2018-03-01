''' Crackle API Wrapper setup '''
from collections import namedtuple
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry


class AuthKeyMissingError(Exception):
    """ Missing API Auth key exception """
    pass


SESSION = requests.session()
RETRY = Retry(connect=3, backoff_factor=0.5)
ADAPTER = HTTPAdapter(max_retries=RETRY)
SESSION.mount('http://', ADAPTER)
SESSION.mount('https://', ADAPTER)
SESSION.headers.update({'Accept': 'application/json'})
SESSION.headers.update({'Content-Type': 'application/json'})
