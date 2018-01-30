class Order(object):
    def __init__(self, amount, price):
        self.amount = amount
        self.price = price

    def execute(self):
        """
        return the amount asset and cash changed
        """
        raise NotImplementedError

class Buy(Order):
    """
    buy amount is in cash (e.g: 0.1 btc).
    """
    def execute(self):
        cash_used = self.amount
        asset_bought = cash_used * self.price
        return asset_bought, -cash_used

class Sell(Order):
    """
    sell amount is in asset (e.g: 0.1 eth).
    """
    def execute(self):
        asset_sold = self.amount
        cash_gained = asset_sold / self.price
        return -asset_sold, cash_gained

def buy(amount, price):
    return Buy(amount, price)

def sell(amount, price):
    return Sell(amount, price)
