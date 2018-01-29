import cryptoenv.components.order as o
import numpy as np

class Manager(object):
    def __init__(self, 
                 initial_asset,
                 initial_cash,
                 limit,
                 r_bias):
        self.asset = []
        self.cash = []
        self.price = []

        self.i_asset = initial_asset
        self.i_cash = initial_cash

        self.limit = limit
        self.r_bias = r_bias

    def reset(self):
        self.asset = [self.i_asset]
        self.cash = [self.i_cash]
        self.price = []

    def update_price(self, price):
        self.price.append(price)

    def update_portfolio(self, rate):
        c_asset = self.asset[-1]
        c_cash = self.cash[-1]
        c_price = self.price[-1]

        if rate >= 0:
            l_limit = self.limit['buy']['min'] 
            u_limit = self.limit['buy']['max']

            amount = rate * c_cash
            amount = np.clip(amount, l_limit, u_limit)

            order = o.buy(amount, c_price, c_cash)

        else:
            l_limit = self.limit['sell']['min']
            u_limit = self.limit['sell']['max']

            amount = np.abs(rate) * c_asset
            amount = np.clip(amount, l_limit, u_limit)

            order = o.sell(amount, c_price, c_asset)
            
        asset_change, cash_change = order.execute()
        total_a = c_asset + asset_change
        total_c = c_cash + cash_change
        
        self.asset.append(total_a)
        self.cash.append(total_c)

    def get_asset(self):
        return self.asset[-1]

    def get_cash(self):
        return self.cash[-1]

    def get_reward(self):
        p = self.price
        a = self.asset
        roc = (p[-1] - p[-2]) / p[-2]
        a_change = a[-1] - a[-2]
        reward = roc * np.log(1+a_change) * self.r_bias
        return reward

    def get_limit(self):
        l = self.limit
        lim = np.concatenate([list(x.values()) for x in l.values()])
        return list(lim)

def make_manager(initial_cash, initial_asset, limit, r_bias):
    limit = _config_limit(limit)
    return Manager(initial_asset, initial_cash, limit, r_bias)

def _config_limit(limit):
    """
    Return default no limit if not specified
    """
    def_max = {'max': 10000}
    def_min = {'min': 0}
    lim = {
            'buy': {**def_max, **def_min},
            'sell': {**def_max, **def_min}
            }
    limit = lim if limit == None else limit
    for order_type in limit:
        for bound in limit[order_type]:
            lim[order_type][bound] = limit[order_type][bound]

    return lim
