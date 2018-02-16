import re

from yandex_checkout.domain.common.base_object import BaseObject
from yandex_checkout.domain.models.receipt_item import ReceiptItem


class Receipt(BaseObject):
    """
    Class representing receipt data wrapper object
    """
    __items = None

    __tax_system_code = None

    __email = None

    __phone = None

    @property
    def items(self):
        return self.__items

    @items.setter
    def items(self, value):
        if isinstance(value, list):
            items = []
            for item in value:
                if isinstance(item, dict):
                    items.append(ReceiptItem(item))
                elif isinstance(item, ReceiptItem):
                    items.append(item)
                else:
                    raise TypeError('Invalid item type in receipt.items')

            self.__items = items
        else:
            raise TypeError('Invalid items value type in receipt')

    @property
    def tax_system_code(self):
        return self.__tax_system_code

    @tax_system_code.setter
    def tax_system_code(self, value):
        if isinstance(value, int):
            self.__tax_system_code = value
        else:
            raise TypeError('Invalid tax_system_code value type')

    @property
    def email(self):
        return self.__email

    @email.setter
    def email(self, value):
        self.__email = str(value)

    @property
    def phone(self):
        return self.__phone

    @phone.setter
    def phone(self, value):
        cast_value = str(value)
        if re.match('^[0-9]{4,15}$', cast_value):
            self.__phone = cast_value
        else:
            raise ValueError('Invalid phone value type')

    def has_items(self):
        return bool(self.items)
