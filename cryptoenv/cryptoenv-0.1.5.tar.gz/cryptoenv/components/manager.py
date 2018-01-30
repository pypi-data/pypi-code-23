import cryptoenv.components.order as o
import numpy as np

class Manager(object):
    def __init__(self, 
                 initial_asset,
                 initial_cash,
                 chunk,
                 r_bias):
        self.asset = []
        self.cash = []
        self.price = []
        self.chunk = chunk

        self.i_asset = initial_asset
        self.i_cash = initial_cash

        self.r_bias = r_bias

    def reset(self):
        self.asset = [self.i_asset]
        self.cash = [self.i_cash]
        self.price = []

    def update_price(self, price):
        self.price.append(price)

    def update_portfolio(self, amount):
        c_asset = self.asset[-1]
        c_cash = self.cash[-1]
        c_price = self.price[-1]

        if amount >= 0:
            amount = amount * self.chunk
            amount = np.clip(amount, None, c_cash)
            order = o.buy(amount, c_price)
        else:
            amount = np.abs(amount) * self.chunk # in asset
            amount = np.clip(amount, None, c_asset)
            order = o.sell(amount, c_price)
            
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
        c = self.cash

        t_cash_1 = c[-2] + (a[-2] / p[-2])
        t_cash_0 = c[-1] + (a[-1] / p[-1])
        reward = np.log(t_cash_0 / t_cash_1)
        return reward

    def get_state(self):
        c_cash = self.get_cash()
        c_asset = self.get_asset()
        return [c_cash, c_asset, self.chunk]

def make_manager(initial_cash, initial_asset, chunk, r_bias):
    return Manager(initial_asset, initial_cash, chunk, r_bias)
