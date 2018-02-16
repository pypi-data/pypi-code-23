from yandex_checkout.domain.common.base_object import BaseObject
from yandex_checkout.domain.models.amount import Amount


class ReceiptItem(BaseObject):
    """
    Class representing receipt item data wrapper object

    Used in Receipt
    """
    __description = None

    __quantity = None

    __amount = None

    __vat_code = None

    @property
    def description(self):
        return self.__description

    @description.setter
    def description(self, value):
        self.__description = str(value)

    @property
    def quantity(self):
        return self.__quantity

    @quantity.setter
    def quantity(self, value):
        self.__quantity = float(value)

    @property
    def amount(self):
        return self.__amount

    @amount.setter
    def amount(self, value):
        if isinstance(value, dict):
            self.__amount = Amount(value)
        elif isinstance(value, Amount):
            self.__amount = value
        else:
            raise TypeError('Invalid amount value type')

    @property
    def vat_code(self):
        return self.__vat_code

    @vat_code.setter
    def vat_code(self, value):
        self.__vat_code = int(value)
