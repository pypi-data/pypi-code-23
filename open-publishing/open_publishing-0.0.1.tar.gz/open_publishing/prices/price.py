from open_publishing.currency import CurrencyValue
               
class Price(CurrencyValue):
    pass


def _convert_to_price(value):
    return Price.create(value)
