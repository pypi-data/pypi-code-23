import base64
import json
import urllib
from decimal import Decimal

from requests import Timeout
from requests.api import request

import error
import pystatsd

API_BASE_URL = 'https://coreapi.pexcard.com/v4/{endpoint}'
SANDBOX_BASE_URL = 'https://sandbox-coreapi.pexcard.com/V4/{endpoint}'
CARD_REQUEST_TEMPLATE = {'FirstName', 'LastName', 'Phone', 'ShippingPhone',
                        'ShippingMethod', 'DateOfBirth', 'Email',
                        'ProfileAddress', 'ShippingAddress'}
API_TIME_FORMAT = '%Y-%m-%dT%H:%M:%S'

PEX_REQUEST_TIMEOUT = 15  # 15 seconds

# pytstatsd related constants
METRIC_BASE = 'pex_wrapper'
METRIC_LATENCY = 'latency'
METRIC_RESPONSE_STATUS = 'response.status'
class JsonEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        else:
            return super(JsonEncoder, self).default(o)


class BaseAPI(object):
    def __init__(self, token=None, sandbox=False, api_base_url=None):
        self.token = token

        if api_base_url:
            self.api_base_url = api_base_url
        else:
            self.api_base_url = SANDBOX_BASE_URL if sandbox else API_BASE_URL

    def _request(self, name, method, endpoint, **kwargs):
        headers = kwargs.pop('headers', {})
        if self.token:
            headers['authorization'] = 'token {}'.format(self.token)

        headers['content-type'] = 'application/json'

        url = self.api_base_url.format(endpoint=endpoint)
        latency_metric = '.'.join([METRIC_BASE, name, method, METRIC_LATENCY])
        result_metric = '.'.join(
            [METRIC_BASE, name, method, METRIC_RESPONSE_STATUS])
        try:
            with pystatsd.Timer(latency_metric):
                response = request(
                    method,
                    url,
                    headers=headers,
                    timeout=PEX_REQUEST_TIMEOUT,
                    **kwargs
                )
        except Timeout as e:
            pystatsd.increment('.'.join([result_metric, '408']))
            raise error.PexTimeoutError(
                message=e.message,
                request_url=url,
                request_params=kwargs,
                status_code=None,
                response=None,
            )

        pystatsd.increment(
            '.'.join([result_metric, str(response.status_code)]))
        body = self._handle_api_error_retrieve_json(url, kwargs, response)

        return body

    def _handle_api_error_retrieve_json(self, rurl, rargs, response):
        rcode = response.status_code
        try:
            body = json.loads(response.text)
        except ValueError, e:
            raise error.InvalidPexServerResponseError(
                message="Invalid Pex json response: {}".format(response.text),
                request_url=rurl, request_params=rargs,
                status_code=rcode, response=response)
        err = body.get('Message', None)

        if rcode >= 300:
            err_params = {
                "message": err,
                "request_url": rurl,
                "request_params": rargs, "status_code": rcode,
                "response": response
            }
            if rcode == 429:
                raise error.RateLimitError(**err_params)
            elif rcode in [400, 404]:
                raise error.InvalidRequestError(**err_params)
            elif rcode == 401:
                raise error.AuthenticationError(**err_params)
            elif rcode == 403:
                raise error.RequesterForbiddenError(**err_params)
            elif 500 <= rcode < 600:
                raise error.PexServerSideError(**err_params)
            else:
                raise error.APIError(**err_params)
        else:
            return body

    def create_token(self, **kwargs):
        client_id = kwargs.get('client_id', '')
        client_secret = kwargs.get('client_secret', '')
        authorization = base64.b64encode(client_id + ':' + client_secret)

        headers = {'authorization': 'basic {}'.format(authorization)}

        data = {
            'Username': kwargs.get('username', ''),
            'Password': kwargs.get('password', '')}

        return self.post('create_token', 'Token', headers=headers, data=data)

    def get(self, name, endpoint, **kwargs):
        return self._request(name, 'get', endpoint, **kwargs)

    def post(self, name, endpoint, **kwargs):
        data = kwargs.get('data', {})
        kwargs['data'] = json.dumps(
                data, ensure_ascii=False, cls=JsonEncoder).encode('utf-8')
        return self._request(name, 'post', endpoint, **kwargs)

    def put(self, name, endpoint, **kwargs):
        data = kwargs.get('data', {})
        kwargs['data'] = json.dumps(
                data, ensure_ascii=False, cls=JsonEncoder).encode('utf-8')
        return self._request(name, 'put', endpoint, **kwargs)


class PEXAPIWrapper(BaseAPI):
    @classmethod
    def create_with_credential(cls, **kwargs):
        wrapper = cls(sandbox=kwargs['sandbox'])
        response = wrapper.create_token(**kwargs)
        wrapper.token = response['Token']
        return wrapper

    @staticmethod
    def validate(request_data):
        template = CARD_REQUEST_TEMPLATE
        cards = request_data['Cards']

        for card in cards:
            if not template.issubset(set(card.keys())):
                raise ValueError('Missing key')

        return request_data

    def create(self, cardholder_info):
        request = PEXAPIWrapper.validate(cardholder_info)
        return self.post("create", "Card/CreateAsync", data=request)

    def activate(self, card_id=None):
        if not card_id:
            raise ValueError("You must specify a card id")

        return self.post("activate", "Card/Activate/{}".format(card_id))

    def fund(self, card_id=None, amount=None):
        if not card_id:
            raise ValueError("You must specify a card id")
        if not amount:
            raise ValueError("You must specify an amount")

        return self.post("fund", "Card/Fund/{}".format(card_id),
                         data={"Amount": amount})

    def block(self, card_id=None):
        if not card_id:
            raise ValueError("You must specify a card id")

        return self.put("block", "Card/Status/{}".format(card_id),
                        data={"Status": "Blocked"})

    def unblock(self, card_id=None):
        if not card_id:
            raise ValueError("You must specify a card id")
        # check if card is inactive, raise error (or unblock)

        return self.put("unblock", "Card/Status/{}".format(card_id),
                        data={"Status": "Active"})

    def terminate(self, card_id=None):
        if not card_id:
            raise ValueError("You must specify a card id")
        return self.post("terminate", "Card/Terminate/{}".format(card_id))

    def zero_balance(self, card_id=None):
        if not card_id:
            raise ValueError("You must specify a card id")

        return self.post("zero_balance", "Card/Zero/{}".format(card_id))

    def get_order(self, card_order_id):
        if not card_order_id:
            raise ValueError("You must specify a card order id")

        return self.get("get_order", "Card/CardOrder/{}".format(card_order_id))

    def get_transaction_list(self, start_date, end_date,
                             include_pendings=False, include_declines=False):
        if not start_date:
            raise ValueError("You must specify a start date")
        if not end_date:
            raise ValueError("You must specify a end data")

        params = {
            "StartDate": start_date.strftime(API_TIME_FORMAT),
            "EndDate": end_date.strftime(API_TIME_FORMAT),
            "IncludePendings": include_pendings,
            "IncludeDeclines": include_declines
        }
        url = "Details/AllCardholderTransactions?{params}"\
            .format(params=urllib.urlencode(params))

        return self.get("get_transaction_list", url)

    def get_transactions_for_account(self, start_date, end_date, acct_id,
                                     include_pendings=True, include_declines=True):
        if not start_date:
            raise ValueError("You must specify a start date")
        if not end_date:
            raise ValueError("You must specify a end date")
        if not acct_id:
            raise ValueError("You must specify a pex account id")

        params = {
            "StartDate": start_date.strftime(API_TIME_FORMAT),
            "EndDate": end_date.strftime(API_TIME_FORMAT),
            "IncludePendings": include_pendings,
            "IncludeDeclines": include_declines
        }
        url = "/Details/TransactionDetails/{acct_id}?{params}".format(
            acct_id=acct_id,
            params=urllib.urlencode(params)
        )
        return self.get("get_transactions_for_account", url)

    def get_account(self, account_id=None):
        if not account_id:
            raise ValueError("You must specify an account id")

        return self.get("get_account", "Details/AccountDetails/{}".format(account_id))

    def get_all_accounts(self):
        return self.get("get_all_accounts", "Details/AccountDetails")
