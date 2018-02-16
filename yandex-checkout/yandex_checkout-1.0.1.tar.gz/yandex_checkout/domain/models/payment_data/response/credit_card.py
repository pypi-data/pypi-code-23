import re

from yandex_checkout.domain.common.base_object import BaseObject
from yandex_checkout.domain.models.payment_data.card_type import CardType


class CreditCard(BaseObject):
    __last4 = None

    __expiry_year = None

    __expiry_month = None

    __card_type = None

    @property
    def last4(self):
        return self.__last4

    @last4.setter
    def last4(self, value):
        cast_value = str(value)
        if re.match('^[0-9]{4}$', cast_value):
            self.__last4 = cast_value
        else:
            raise ValueError('Invalid last4 value')

    @property
    def expiry_year(self):
        return self.__expiry_year

    @expiry_year.setter
    def expiry_year(self, value):
        cast_value = str(value)
        if re.match('^\d\d\d\d$', cast_value) and 2000 < int(cast_value) < 2200:
            self.__expiry_year = cast_value
        else:
            raise ValueError('Invalid card expiry year value')

    @property
    def expiry_month(self):
        return self.__expiry_month

    @expiry_month.setter
    def expiry_month(self, value):
        cast_value = str(value)
        if re.match('^\d\d$', cast_value) and 0 < int(cast_value) <= 12:
            self.__expiry_month = cast_value
        else:
            raise ValueError('Invalid card expiry month value')

    @property
    def card_type(self):
        return self.__card_type

    @card_type.setter
    def card_type(self, value):
        print(value)
        if value in CardType.__dict__.values():
            self.__card_type = value
        else:
            raise ValueError('Invalid card_type value')
