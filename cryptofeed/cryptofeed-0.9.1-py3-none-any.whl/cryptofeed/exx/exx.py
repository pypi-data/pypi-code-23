'''
Copyright (C) 2017-2018  Bryant Moscon - bmoscon@gmail.com

Please see the LICENSE file for the terms and conditions
associated with this software.
'''
import json
from decimal import Decimal

from cryptofeed.feed import Feed
from cryptofeed.callback import Callback


class EXX(Feed):
    def __init__(self, pairs=None, channels=None, callbacks=None):
        super(EXX, self).__init__('wss://ws.exx.com/websocket')
        self.channels = channels
        self.pairs = pairs
        self.book = {}
        self.callbacks = {'trades': Callback(None),
                          'ticker': Callback(None),
                          'book': Callback(None)}
        if callbacks:
            for cb in callbacks:
                self.callbacks[cb] = callbacks[cb]
    
    async def message_handler(self, msg):
        print(msg)



    async def subscribe(self, websocket):
        await websocket.send(json.dumps(
            {
                "dataType":"1_TRADE_ETH_HSR",
                "dataSize":1,
                "action":"ADD"
            }
        ))

        await websocket.send(json.dumps(
            {
                "dataType": 'EXX_MARKET_LIST_BTC_USDT',
                "dataSize": 1,
                "action": "ADD"
            }
        ))