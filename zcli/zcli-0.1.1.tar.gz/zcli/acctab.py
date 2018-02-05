from decimal import Decimal


class AccumulatorTable (dict):
    def __getitem__(self, key):
        return self.get(key)

    def get(self, key, default=Decimal(0)):
        return dict.get(self, key, default)
