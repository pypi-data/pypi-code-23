import base64, hashlib, hmac, time, urllib.request, json
from collections import OrderedDict


#Default API limit: 25 calls per 10 seconds
base_url = 'https://api.btcmarkets.net'
instruments = ['BCH','BTC','LTC','ETH','XRP','ETC']
#TODO Implement websockets - https://github.com/BTCMarkets/API/wiki/websocket
#socket_url = 'https://socket.btcmarkets.net'

# Trade values (price or volume) require this modifier - https://github.com/BTCMarkets/API/wiki/Trading-API
CONVERSION = 100000000 #e.g. Price of $130 = 13000000000, Volume of 1 BTC = 100000000


def request(action, key, signature, timestamp, path, data):
    header = {
        'User-Agent': 'btc markets python client',
        'Accept': 'application/json', 
        'Accept-Charset': 'utf-8',  
        'Content-Type': 'application/json',
        'apikey': key,
        'timestamp': timestamp,
        'signature': signature
    }
    request = urllib.request.Request(base_url + path, data, header)
    if action == 'post':
        payload = urllib.request.urlopen(request, data.encode('utf-8'))
    else:
        payload = urllib.request.urlopen(request) 
    try:
        response = json.load(payload)
    except:
        response = {}
    return response


def get_request(key, secret, path):
    nowInMilisecond = str(int(time.time() * 1000))
    stringToSign = str(path + "\n" + nowInMilisecond + "\n").encode('utf-8')
    signature = base64.b64encode(hmac.new(secret, stringToSign, digestmod=hashlib.sha512).digest())
    return request('get', key, signature, nowInMilisecond, path, None)    


def post_request(key, secret, path, postData):
    nowInMilisecond = str(int(time.time() * 1000))
    stringToSign = str(path + "\n" + nowInMilisecond + "\n" + postData).encode('utf-8')
    signature = base64.b64encode(hmac.new(secret, stringToSign, digestmod=hashlib.sha512).digest())
    return request('post', key, signature, nowInMilisecond, path, postData)

def convert_response(response_list, response_keys):
    for item in response_list:
        for key in response_keys:
            conversion = {key:item[key]/CONVERSION}
            item.update(conversion)
    return response_list

class Client:

    def __init__(self, key, secret):
        self.key = key
        self.secret = base64.b64decode(secret)

    # Market Data - https://github.com/BTCMarkets/API/wiki/Market-data-API
    def market_tick(self,instrument,currency):
        response = get_request(self.key, self.secret, '/market/{}/{}/tick'.format(instrument.upper(),currency.upper()))
        return response

    def market_all_ticks(self,currency):
        response = []
        for instrument in instruments:
            response.append(Client.market_tick(self,instrument,currency))
        return response

    def market_orderbook(self,instrument,currency):
        response = get_request(self.key, self.secret, '/market/{}/{}/orderbook'.format(instrument.upper(),currency.upper()))

    def market_trades(self,instrument,currency):
        response = get_request(self.key, self.secret, '/market/{}/{}/trades'.format(instrument.upper(),currency.upper()))
        return response
    
    # Account data - https://github.com/BTCMarkets/API/wiki/Account-API
    def account_balance(self):
        response = get_request(self.key, self.secret, '/account/balance')
        response = convert_response(response, ['balance', 'pendingFunds'])
        return response

    def account_trading_fee(self,instrument,currency):
        response = get_request(self.key, self.secret, '/account/{}/{}/tradingfee'.format(instrument.upper(),currency.upper()))
        print(type(response))
        response = convert_response([response], ['tradingFeeRate', 'volume30Day'])
        return response[0]
    
    # Order Data - https://github.com/BTCMarkets/API/wiki/Trading-API
    def trade_history(self, instrument, currency, limit, since):
        data = OrderedDict([('currency', currency.upper()),('instrument', instrument.upper()),('limit', limit),('since', since)])
        postData = json.dumps(data, separators=(',', ':'))
        response = post_request(self.key, self.secret, '/order/trade/history', postData) 
        response['trades'] = convert_response(response['trades'], ['price', 'volume','fee'])
        return response

    def order_history(self, instrument, currency, limit, since):
        data = OrderedDict([('currency', currency.upper()),('instrument', instrument.upper()),('limit', limit),('since', since)])
        postData = json.dumps(data, separators=(',', ':'))
        response = post_request(self.key, self.secret, '/order/history', postData) 
        response['orders'] = convert_response(response['orders'], ['price', 'openVolume','volume'])
        for order in response['orders']:
             order['trades'] = convert_response(order['trades'], ['price', 'volume','fee'])
        return response

    def open_orders(self, instrument, currency, limit, since):
        data = OrderedDict([('currency', currency.upper()),('instrument', instrument.upper()),('limit', limit),('since', since)])
        postData = json.dumps(data, separators=(',', ':'))
        response = post_request(self.key, self.secret, '/order/open', postData) 
        response['orders'] = convert_response(response['orders'], ['price', 'openVolume','volume'])
        for order in response['orders']:
             order['trades'] = convert_response(order['trades'], ['price', 'volume','fee'])
        return response
    
    def order_detail(self, order_ids):
        orders = {'orderIds':order_ids} 
        postData = json.dumps(orders, separators=(',', ':'))
        response = post_request(self.key, self.secret, '/order/detail', postData) 
        response['orders'] = convert_response(response['orders'], ['price', 'openVolume','volume'])
        for order in response['orders']:
             order['trades'] = convert_response(order['trades'], ['price', 'volume','fee']) 
        return response

    def order_create(self, instrument, currency, price, volume, side, order_type):
        #Conversion to fit the trade API requirements
        price = price*CONVERSION
        volume = volume*CONVERSION
        data = OrderedDict([('currency', currency),('instrument', instrument),('price', price),('volume', volume),
                            ('orderSide', side),('ordertype', order_type),('clientRequestId', 'btcmarketsapi')]) # client_request_id will be required once they update the API
        postData = json.dumps(data, separators=(',', ':'))
        response = post_request(self.key, self.secret, '/order/create', postData)
        return response

    def order_cancel(self, order_ids):
        orders = {'orderIds':order_ids} 
        postData = json.dumps(orders, separators=(',', ':'))
        response = post_request(self.key, self.secret, '/order/cancel', postData) 
        return response

    
    

    