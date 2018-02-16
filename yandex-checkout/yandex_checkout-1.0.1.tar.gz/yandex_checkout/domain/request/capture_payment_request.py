from yandex_checkout.domain.common.request_object import RequestObject
from yandex_checkout.domain.models.amount import Amount
from yandex_checkout.domain.models.receipt import Receipt


class CapturePaymentRequest(RequestObject):
    __amount = None

    __receipt = None

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
    def receipt(self):
        return self.__receipt

    @receipt.setter
    def receipt(self, value):
        if isinstance(value, dict):
            self.__receipt = Receipt(value)
        elif isinstance(value, Receipt):
            self.__receipt = value
        else:
            raise TypeError('Invalid receipt value type')

    def validate(self):
        if self.amount:
            value = self.amount.value
            if not value or value <= 0.0:
                self.__set_validation_error('Invalid amount value: ' + str(value))
        if self.receipt is not None and self.receipt.has_items:
            email = self.receipt.email
            phone = self.receipt.phone
            if not email and not phone:
                self.__set_validation_error('Both email and phone values are empty in receipt')

            if not self.receipt.tax_system_code and any(not item.vat_code for item in self.receipt.items):
                self.__set_validation_error('Item vat_id and receipt tax_system_id not specified')

    def __set_validation_error(self, message):
        raise ValueError(message)
