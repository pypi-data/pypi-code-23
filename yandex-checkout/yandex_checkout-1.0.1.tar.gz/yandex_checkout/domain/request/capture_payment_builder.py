from yandex_checkout.domain.request.capture_payment_request import CapturePaymentRequest


class CapturePaymentBuilder(object):
    def __init__(self):
        self.__request = CapturePaymentRequest()

    def set_amount(self, value):
        self.__request.amount = value
        return self

    def set_receipt(self, value):
        self.__request.receipt = value
        return self

    def build(self):
        return self.__request
