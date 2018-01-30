import re

from open_publishing.core import SimpleField
from open_publishing.core.enums import Currency

class CurrencyValue(object):
    def __init__(self,
                 amount,
                 currency):
        self._amount = amount
        self._currency = currency

    @property
    def amount(self):
        return self._amount

    @property
    def currency(self):
        return self._currency

    def __str__(self):
        return "{amount:.2f} {currency}".format(amount=self._amount,
                                                currency=self._currency)
        
    def to_gjp(self):
        return {'value': int(round(self._amount * 100)),
                'currency': self._currency.identifier}

    @classmethod
    def from_gjp(cls, gjp):
        amount = int(gjp['value']) / 100.0
        currency = Currency.from_id(gjp["currency"])
        return cls(amount, currency)

    @classmethod
    def create(cls, value):
        if isinstance(value, str):
            m = re.match("^\s*(?P<amount>[0-9]*[\.]?[0-9]*)\s*(?P<currency>[a-zA-Z]+)$", value)
            if m is None:
                raise ValueError("expected price in format '12.34 EUR|USD', got {0}".format(value))
            amount = float(m.group("amount"))
            currency_code = m.group("currency")
            currency = Currency.find(currency_code)
            if currency is None:
                raise ValueError('Unsupported currency: {0}'.format(currency_code))
            return cls(amount, currency)
        elif isinstance(value, tuple) and isinstance(value[0], float) and value[1] in Currency:
            return cls(*value)
        elif isinstance(value, CurrencyValue):
            return value
        else :
            raise ValueError("Expected instance of str, tuple or CurrencyValue, got {0}".format(value))

class CurrencyValueField(SimpleField):
    def __init__(self,
                 database_object,
                 aspect,
                 field_locator,
                 nullable = False):
        super(CurrencyValueField, self).__init__(database_object=database_object,
                                                 aspect=aspect,
                                                 field_locator=field_locator,
                                                 nullable=nullable)

    def _parse_value(self,
                     value):
        if value == self._serialized_null and self._nullable:
            return value
        else:
            return CurrencyValue.from_gjp(value)

    def _value_validation(self,
                          value):
        return CurrencyValue.create(value)
    
    def _serialize_value(self,
                         value):
        if value is None and self._nullable:
            return value
        else:
            return value.to_gjp()
