from yandex_checkout.domain.common.request_object import RequestObject
from yandex_checkout.domain.models.amount import Amount
from yandex_checkout.domain.models.confirmation.confirmation import Confirmation
from yandex_checkout.domain.models.confirmation.confirmation_factory import ConfirmationFactory
from yandex_checkout.domain.models.payment_data.payment_data import PaymentData
from yandex_checkout.domain.models.payment_data.payment_data_factory import PaymentDataFactory
from yandex_checkout.domain.models.receipt import Receipt
from yandex_checkout.domain.models.recipient import Recipient


class PaymentRequest(RequestObject):
    __recipient = None

    __amount = None

    __receipt = None

    __payment_token = None

    __payment_method_id = None

    __payment_method_data = None

    __confirmation = None

    __save_payment_method = None

    __capture = None

    __client_ip = None

    __metadata = None

    @property
    def recipient(self):
        return self.__recipient

    @recipient.setter
    def recipient(self, value):
        if isinstance(value, dict):
            self.__recipient = Recipient(value)
        elif isinstance(value, Recipient):
            self.__recipient = value
        else:
            raise TypeError('Invalid recipient value type')

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

    @property
    def payment_token(self):
        return self.__payment_token

    @payment_token.setter
    def payment_token(self, value):
        cast_value = str(value)
        if cast_value:
            self.__payment_token = cast_value
        else:
            raise ValueError('Invalid payment_token value')

    @property
    def payment_method_id(self):
        return self.__payment_method_id

    @payment_method_id.setter
    def payment_method_id(self, value):
        cast_value = str(value)
        if cast_value:
            self.__payment_method_id = cast_value

    @property
    def payment_method_data(self):
        return self.__payment_method_data

    @payment_method_data.setter
    def payment_method_data(self, value):
        if isinstance(value, dict):
            self.__payment_method_data = PaymentDataFactory().create(value, self.context())
        elif isinstance(value, PaymentData):
            self.__payment_method_data = value
        else:
            raise TypeError('Invalid payment_method_data type')

    @property
    def confirmation(self):
        return self.__confirmation

    @confirmation.setter
    def confirmation(self, value):
        if isinstance(value, dict):
            self.__confirmation = ConfirmationFactory().create(value, self.context())
        elif isinstance(value, Confirmation):
            self.__confirmation = value
        else:
            raise TypeError('Invalid confirmation type')

    @property
    def save_payment_method(self):
        return self.__save_payment_method

    @save_payment_method.setter
    def save_payment_method(self, value):
        self.__save_payment_method = bool(value)

    @property
    def capture(self):
        return self.__capture

    @capture.setter
    def capture(self, value):
        self.__capture = bool(value)

    @property
    def client_ip(self):
        return self.__client_ip

    @client_ip.setter
    def client_ip(self, value):
        self.__client_ip = str(value)

    @property
    def metadata(self):
        return self.__metadata

    @metadata.setter
    def metadata(self, value):
        if type(value) is dict:
            self.__metadata = value

    def validate(self):
        amount = self.amount
        if amount is None:
            self.__set_validation_error('Payment amount not specified')

        if amount.value <= 0.0:
            self.__set_validation_error('Invalid payment amount value: ' + str(amount.value))

        if self.receipt is not None and self.receipt.has_items:
            email = self.receipt.email
            phone = self.receipt.phone
            if not email and not phone:
                self.__set_validation_error('Both email and phone values are empty in receipt')

            if self.receipt.tax_system_code is None:
                for item in self.receipt.items:
                    if item.vat_code is None:
                        self.__set_validation_error('Item vat_code and receipt tax_system_id not specified')

        if self.payment_token:
            if self.payment_method_id:
                self.__set_validation_error('Both payment_token and payment_method_id values are specified')

            if self.payment_method_data:
                self.__set_validation_error('Both payment_token and payment_data values are specified')

        elif self.payment_method_id:
            if self.payment_method_data:
                self.__set_validation_error('Both payment_method_id and payment_data values are specified')

    def __set_validation_error(self, message):
        raise ValueError(message)
