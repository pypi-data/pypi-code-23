import treq

from typing import Dict
from ice3x.clients.abc import IceCubedClientBase
from ice3x.decorators import add_nonce, requires_authentication
from twisted.internet.defer import Deferred
from twisted.internet.defer import inlineCallbacks


class IceCubedAsyncClient(IceCubedClientBase):
    @inlineCallbacks
    def _fetch_resource(self, method: str, suffix: str, params: Dict={}) -> Deferred:
        headers = {
            'User-Agent': 'Mozilla/4.0 (compatible; Ice3x Async Python client)'
        }

        if method == 'post':
            headers.update({
                'Key': self.api_key,
                'Sign': self.sign(params)
            })

        kwargs = {
            'params': params,
            'headers': headers
        }

        url = f'{self.BASE_URI}{suffix}'
        resp = yield treq.request(method, url, **kwargs)
        data = yield resp.json()
        return data

    def __init__(self, api_key: str=None, secret: str=None) -> None:
        """Instantiate the client

        Args:
            api_key: An ICE3X public API key
            secret: An ICE3X private API key
        """
        self.api_key = api_key
        self.secret = secret

    def get_public_trade_info(self, trade_id: int, **params: Dict) -> Deferred:
        """Fetch public info relating to a specified trade

        Args:
            trade_id: A valid trade id

        Returns:
            Data relating to the specified trade id
        """
        params.update({'trade_id': trade_id})
        return self._fetch_resource('get', 'trade/info', params)
            
    def get_public_trade_list(self, **params: Dict) -> Deferred:
        """Fetch a public facing list of trades

        Returns:
            A list of public trade data
        """
        return self._fetch_resource('get', 'trade/list', params)
    
    def get_market_depth(self, **params: Dict) -> Deferred:
        """Fetch the public market depth

        Returns:
            A market depth data
        """        
        return self._fetch_resource('get', 'stats/marketdepth', params)
        
    def get_pair_info(self, pair_id: int, **params: Dict) -> Deferred:
        """"""
        params.update({'pair_id': pair_id})        
        return self._fetch_resource('get', 'pair/info', params)
    
    def get_pair_list(self, **params: Dict) -> Deferred:
        """"""        
        return self._fetch_resource('get', 'pair/list', params)
    
    def get_currency_info(self, currency_id: int, **params: Dict) -> Deferred:
        """"""    
        params.update({'currency_id': currency_id})
        return self._fetch_resource('get', 'currency/info', params)
    
    def get_currency_list(self, **params: Dict) -> Deferred:
        """"""        
        return self._fetch_resource('get', 'currency/list', params)
    
    def get_orderbook_info(self, pair_id: int, **params: Dict) -> Deferred:
        """"""    
        params.update({'pair_id': pair_id})
        return self._fetch_resource('get', 'orderbook/info', params)
    
    def get_market_depth_full(self, **params: Dict) -> Deferred:
        """"""        
        return self._fetch_resource('get', 'stats/marketdepthfull', params)
    
    def get_market_depth_bt_cav(self, **params: Dict) -> Deferred:
        """"""        
        return self._fetch_resource('get', 'stats/marketdepthbtcav', params)
    
    @add_nonce
    @requires_authentication
    def get_invoice_list(self, **params: Dict) -> Deferred:
        """"""        
        return self._fetch_resource('post', 'invoice/list', params)
    
    @add_nonce
    @requires_authentication
    def get_invoice_info(self, invoice_id: int, **params: Dict) -> Deferred:
        """"""        
        params.update({'invoice_id': invoice_id})        
        return self._fetch_resource('post', 'invoice/info', params)
    
    @add_nonce
    @requires_authentication
    def get_invoice_pdf(self, invoice_id: int, **params: Dict) -> Deferred:
        """"""        
        params.update({'invoice_id': invoice_id})        
        return self._fetch_resource('post', 'invoice/pdf', params)
    
    @add_nonce
    @requires_authentication
    def cancel_order(self, order_id: int, **params: Dict) -> Deferred:
        """"""        
        params.update({'order_id': order_id})        
        return self._fetch_resource('post', 'order/cancel', params)
    
    @add_nonce
    @requires_authentication
    def create_order(self, pair_id: int, amount: float, otype: str, **params: Dict) -> Deferred:
        """"""
        params.update(
            {
                'pair_id': pair_id,
                'amount': amount,
                'type': otype
            }
        )
        
        return self._fetch_resource('post', 'order/new', params)
    
    @add_nonce
    @requires_authentication
    def get_order_info(self, order_id: int, **params: Dict) -> Deferred:
        """"""        
        params.update({'order_id': order_id})        
        return self._fetch_resource('post', 'order/info', params)
    
    @add_nonce
    @requires_authentication
    def get_order_list(self, **params: Dict) -> Deferred:
        """"""        
        return self._fetch_resource('post', 'order/list', params)
    
    @add_nonce
    @requires_authentication
    def get_transaction_info(self, transaction_id: int, **params: Dict) -> Deferred:
        """"""        
        params.update({'transaction_id': transaction_id})        
        return self._fetch_resource('post', 'transaction/info', params)
    
    @add_nonce
    @requires_authentication
    def get_transaction_list(self, **params: Dict) -> Deferred:
        """"""
        return self._fetch_resource('post', 'transaction/list', params)
    
    @add_nonce
    @requires_authentication
    def get_trade_info(self, trade_id: int, **params: Dict) -> Deferred:
        """"""        
        params.update({'trade_id': trade_id})        
        return self._fetch_resource('post', 'trade/info', params)
    
    @add_nonce
    @requires_authentication
    def get_trade_list(self, **params: Dict) -> Deferred:
        """"""        
        return self._fetch_resource('post', 'trade/list', params)
    
    @add_nonce
    @requires_authentication
    def get_balance_list(self, **params: Dict) -> Deferred:
        """"""        
        return self._fetch_resource('post', 'balance/list', params)
    
    @add_nonce
    @requires_authentication
    def get_balance_info(self, currency_id: int, **params: Dict) -> Deferred:
        """"""
        params.update({'currency_id': currency_id})        
        return self._fetch_resource('post', 'balance/info', params)