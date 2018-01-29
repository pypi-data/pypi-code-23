import cryptoenv.components.manager as m
import cryptoenv.components.dataset as d
import numpy as np

import tensorforce.environments as e

class CryptoTradingEnv(e.environment.Environment):
    def __init__(self, 
                 path,
                 initial_cash=1,
                 initial_asset=0,
                 limit=None,
                 r_bias=1,
                 preprocessing_fn='default'):

        self.limit = limit
        self.manager = m.make_manager(initial_cash, initial_asset, limit, r_bias)
        self.initial_cash = initial_cash
        self.initial_asset = initial_asset
        self.raw_d, self.preprocessed_d = d.make_dataset(path, preprocessing_fn)
        self.r_iter, self.p_iter = self.raw_d.iterrows(), self.preprocessed_d.iterrows()
        self.done = False

    def reset(self):
        self.r_iter = self.raw_d.iterrows()
        self.p_iter = self.preprocessed_d.iterrows()
        d.skip(self.r_iter, 49) # the first 50 row of preprocessed is dropped, use this to sync the t with preprocessed

        intitial_price = next(self.r_iter)[1]['close']

        self.manager.reset()
        self.manager.update_price(intitial_price)
        self.done = False

        p_data = next(self.p_iter)[1]

        c_cash = [self.manager.get_cash()]
        c_asset = [self.manager.get_asset()]
        limit = self.manager.get_limit()
        b_l_lim, s_l_lim = limit[1], limit[3]

        state = [c_cash, c_asset, [b_l_lim, s_l_lim], list(p_data)]
        state = np.concatenate(state, 0)
        return state

    def execute(self, actions=[0]):
        """
        action: rate of buy/change, sell if value are negative, buy otherwise. range: [-1 1] (continous)
        """
        actions = np.expand_dims(np.squeeze(actions), 0)[0]
        if not self.done:
            self.manager.update_portfolio(actions)
            i, r_data = next(self.r_iter)
            p_data = next(self.p_iter)[1].as_matrix()

            close = r_data['close']
            self.manager.update_price(close)

            c_cash = [self.manager.get_cash()]
            c_asset = [self.manager.get_asset()]
            limit = self.manager.get_limit()
            b_l_lim, s_l_lim = limit[1], limit[3]

            state = [c_cash, c_asset, [b_l_lim, s_l_lim], list(p_data)]
            state = np.concatenate(state, 0)
            reward = self.manager.get_reward()
            info = None

            self.done = (i == self.raw_d.shape[0]-1) # end of dataset
        else:
            state = None
            reward = None
            info = [self.manager.cash, self.manager.asset, self.manager.price]


        return state, self.done, reward

    @property
    def actions(self):
        return dict(type='float', min_value=-1, max_value=1, shape=1)

    @property
    def states(self):
        return dict(type='float', shape=154)

    def __str__(self):
        return 'Crypto Env'
