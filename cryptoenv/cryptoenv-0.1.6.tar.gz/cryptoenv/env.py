import cryptoenv.components.manager as m
import cryptoenv.components.dataset as d
import numpy as np

import tensorforce.environments as e

class CryptoTradingEnv(e.environment.Environment):
    def __init__(self, 
                 df=None,
                 data_path=None,
                 initial_cash=1,
                 initial_asset=0,
                 chunk=0.001,
                 r_bias=1,
                 preprocessing_fn='default'):

        self.chunk = chunk
        self.manager = m.make_manager(initial_cash, initial_asset, chunk, r_bias)
        self.initial_cash = initial_cash
        self.initial_asset = initial_asset
        self.done = False

        # intitialzing dataset
        if data_path != None:
            self.raw_d, self.preprocessed_d = d.make_dataset(data_path, preprocessing_fn)
        elif df != None:
            self.raw_d = df
            self.preprocessed = d._preprocess(df, 'default')
        else:
            raise ValueError('[ERROR] Either path or df must be specified')

        self.r_iter, self.p_iter = self.raw_d.iterrows(), self.preprocessed_d.iterrows()

    def reset(self):
        self.r_iter = self.raw_d.iterrows()
        self.p_iter = self.preprocessed_d.iterrows()
        d.skip(self.r_iter, 11) # the first 50 row of preprocessed is dropped, use this to sync the t with preprocessed

        intitial_price = next(self.r_iter)[1]['close']

        self.manager.reset()
        self.manager.update_price(intitial_price)
        self.done = False

        p_data = next(self.p_iter)[1]

        state = [self.manager.get_state(), list(p_data)]
        state = np.concatenate(state, 0)
        return state

    def execute(self, actions=[0]):
        """
        action: rate of buy/change, sell if value are negative, buy otherwise. range: [-1 1] (continous)
        """
        actions = int(np.expand_dims(np.squeeze(actions), 0)[0] * 1000)
        if not self.done:
            self.manager.update_portfolio(actions)
            i, r_data = next(self.r_iter)
            p_data = next(self.p_iter)[1].as_matrix()

            close = r_data['close']
            self.manager.update_price(close)

            state = [self.manager.get_state(), list(p_data)]
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
        return dict(type='float', shape=15)

    def __str__(self):
        return 'Crypto Env'
