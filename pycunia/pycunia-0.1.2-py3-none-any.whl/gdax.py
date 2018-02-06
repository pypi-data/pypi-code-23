from pycunia.tools import *
from requests.auth import AuthBase
import json, hmac, hashlib, time, base64

class _GDAXAuth(AuthBase):
    def __init__(self, api_key, secret_key, passphrase):
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase

    def __call__(self, request):
        timestamp = str(time.time())
        message = timestamp + request.method + request.path_url + (request.body or '')
        message = message.encode('ascii')
        hmac_key = base64.b64decode(self.secret_key)
        signature = hmac.new(hmac_key, message, hashlib.sha256)
        signature_b64 = base64.b64encode(signature.digest()).decode('utf-8')

        request.headers.update({
            'Content-Type': 'Application/JSON',
            'CB-ACCESS-SIGN': signature_b64,
            'CB-ACCESS-TIMESTAMP': timestamp,
            'CB-ACCESS-KEY': self.api_key,
            'CB-ACCESS-PASSPHRASE': self.passphrase
        })
        return request

class _GDAXWebSocket:
    def __init__(self):
        self.endpoint = 'wss://ws-feed.gdax.com'

class GDAX:
    def __init__(self):
        self.endpoint = 'https://api.gdax.com'
        self.auth = None

    def get_products(self):
        return get_json(self.endpoint + '/products')

    def get_product_order_book(self, product_id, level=1):
        return get_json(self.endpoint + '/products/' + product_id + '/book?level=' + str(level))

    def get_product_ticker(self, product_id):
        return get_json(self.endpoint + '/products/' + product_id + '/ticker')

    def get_trades(self, product_id):
        return get_json(self.endpoint + '/products/' + product_id + '/trades')

    def get_historic_rates(self, product_id, start, end, granularity):
        if not granularity in {60, 300, 900, 3600, 21600, 86400}:
            raise Exception("Wrong granularity!")
        return get_json(self.endpoint + '/products/' + product_id + '/book?start=' + str(start) + '&end=' + str(
            end) + '&granularity=' + str(granularity))
    
    def set_auth(self, key, secret, passphrase):
        '''
        key: api key
        secret: secret key
        passphrase: passphrase
        '''
        self.auth = _GDAXAuth(key, secret, passphrase)
    
    def get_account(self, id=None):
        if not self.auth:
            raise Exception("Please set auth!")
        if not id:
            return get_json(self.endpoint + '/accounts', auth=self.auth)
        else:
            return get_json(self.endpoint + '/accounts/' + id, auth=self.auth)
    
    def get_account_history(self, id):
        if not self.auth:
            raise Exception("Please set auth!")
        return get_json(self.endpoint + '/accounts/' + id + '/ledger', auth=self.auth)
    
    def get_holds(self, id):
        if not self.auth:
            raise Exception("Please set auth!")
        return get_json(self.endpoint + '/accounts/' + id + '/holds', auth=self.auth)
    
    def connect_ws(self, auth=None):
        pass