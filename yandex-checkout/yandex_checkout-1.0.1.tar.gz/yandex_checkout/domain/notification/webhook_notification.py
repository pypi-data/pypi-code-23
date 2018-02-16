from yandex_checkout.domain.common.base_object import BaseObject
from yandex_checkout.domain.response.payment_response import PaymentResponse


class WebhookNotification(BaseObject):
    __type = None

    __event = None

    __object = None

    @property
    def type(self):
        return self.__type

    @type.setter
    def type(self, value):
        self.__type = value

    @property
    def event(self):
        return self.__event

    @event.setter
    def event(self, value):
        self.__event = value

    @property
    def object(self):
        return self.__event

    @object.setter
    def object(self, value):
        if isinstance(value, dict) and value:
            self.__object = PaymentResponse(value)
        elif not value:
            raise ValueError('Parameter object is empty')
        else:
            raise TypeError('Invalid object type')

