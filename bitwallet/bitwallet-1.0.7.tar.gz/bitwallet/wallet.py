from collections import defaultdict


class Block(object):
    def __init__(self, q, price):
        self.q = q
        self.price = price

    def __repr__(self):
        return "Block({}, {})".format(self.q, self.price)


class Account(object):

    def __init__(self):
        self.q = 0
        self.blocks = []

    def add(self, q, price):
        assert q >= 0
        self.q += q
        self.blocks.append(Block(q, price))

    def remove(self, q):
        assert q <= self.q
        assert self.blocks
        block = self.blocks[0]
        assert q <= block.q

        self.blocks[0].q -= q
        assert self.blocks[0].q >= 0
        if self.blocks[0].q == 0:
            self.blocks.pop(0)
        self.q -= q

        empty = self.q == 0
        assert empty == (len(self.blocks) == 0)
        return empty


class AccountLite(object):

    def __init__(self):
        self.q = 0

    def add(self, q, price):
        assert q >= 0
        self.q += q

    def remove(self, q):
        assert q <= self.q
        self.q -= q
        return self.q == 0

    def __repr__(self):
        return "{}".format(self.q)


class Wallet(object):

    def __init__(self, auditable):
        self.auditable = auditable
        if auditable:
            self.wallet = defaultdict(Account)
        else:
            self.wallet = defaultdict(AccountLite)

    def buy(self, ticker, q, price):
        assert isinstance(q, int) or isinstance(q, long)
        assert self.is_price_valid(price)
        assert q > 0
        if q == 0:
            return
        self.wallet[ticker].add(q, price)

    def sell_all(self, ticker, price, audit=None):
        assert ticker in self.wallet
        assert self.is_price_valid(price)

        account = self.wallet[ticker]
        del self.wallet[ticker]

        if self.auditable and (audit is not None):
            for block in account.blocks:
                audit(block.q, block.price)

    def sell_to_target(self, ticker, q, price, audit=None):
        assert isinstance(q, int) or isinstance(q, long)
        assert self.is_price_valid(price)
        assert ticker in self.wallet
        assert q > 0

        account = self.wallet[ticker]

        if q > account.q:
            q = account.q

        pnl = 0
        while q:
            if self.auditable:
                assert account.blocks

                block = account.blocks[0]

                to_sell = min(q, block.q)
                assert to_sell <= account.q
                assert to_sell <= block.q

                if audit is not None:
                    audit(to_sell, block.price)

                pnl += to_sell * (price - block.price)
            else:
                to_sell = q

            q -= to_sell
            empty = account.remove(to_sell)
            if empty:
                assert account.q == 0
                del self.wallet[ticker]

        return pnl

    @property
    def tickers(self):
        return self.wallet.keys()

    def total_coin(self, ticker):
        return self.wallet[ticker].q if ticker in self.tickers else 0

    def total_coins(self):
        return {i: account.q for i, account in self.wallet.iteritems()}

    @staticmethod
    def is_price_valid(price):
        assert isinstance(price, int) or isinstance(price, long)
        return price > 0
