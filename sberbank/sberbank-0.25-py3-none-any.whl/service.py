import os
from decimal import Decimal, DecimalException

import requests

from django.conf import settings

from sberbank.exceptions import NetworkException, ProcessingException, \
    PaymentNotFoundException
from sberbank.models import Payment, BankLog, Status, LogType


class BankService:
    __default_session_timeout = 1200
    __default_currency_code = 810
    __default_page_view = 'DESKTOP'
    __default_gateway_address = 'https://3dsec.sberbank.ru/payment/rest'

    def __init__(self, merchant_id):
        if os.environ.get('ENVIRONMENT', None) == 'production':
            self.__default_gateway_address = \
                'https://securepayments.sberbank.ru/payment/rest'
        else:
            self.__default_gateway_address = \
                'https://3dsec.sberbank.ru/payment/rest'
        self._get_credentials(merchant_id)

    def _get_credentials(self, merchant_id):
        settings_merchant_key = "MERCHANTS"

        merchants = getattr(settings, settings_merchant_key, None)
        if merchants is None:
            raise KeyError(
                "Key %s not found in settings.py" % settings_merchant_key)

        self.merchant = merchants.get(merchant_id, None)
        if self.merchant is None:
            raise KeyError(
                "Merchant key %s not found in %s" % (
                    merchant_id, settings_merchant_key))

        for field_name in ["username", "password"]:
            if self.merchant.get(field_name, None) is None:
                raise KeyError(
                    "Field '%s' not found in %s->%s" % (
                        field_name, settings_merchant_key, merchant_id))

    def pay(self, amount, success_url=None, **kwargs):
        session_timeout = self.merchant.get(
            'session_timeout', self.__default_session_timeout)
        currency = self.merchant.get('currency', self.__default_currency_code)

        page_view = kwargs.get(
            'page_view',
            self.merchant.get('page_view', self.__default_page_view))
        fail_url = kwargs.get('fail_url', self.merchant.get('fail_url'))

        success_url = success_url or self.merchant.get('success_url')

        if success_url is None:
            raise ValueError("Success_url is not set")

        try:
            amount = Decimal(str(amount))
        except (ValueError, DecimalException):
            raise TypeError(
                "Wrong amount type, passed {} ({}) instead of decimal"
                .format(amount, type(amount)))

        payment = Payment(amount=amount, details={
            'username': self.merchant.get("username"),
            'currency': currency,
            'success_url': success_url,
            'fail_url': fail_url,
            'session_timeout': session_timeout,
            'page_view': page_view
        })
        payment.save()

        data = {
            'userName': self.merchant.get("username"),
            'password': self.merchant.get("password"),
            'orderNumber': payment.uid.hex,
            'amount': int(amount * 100),
            'returnUrl': success_url,
            'failUrl': fail_url,
            'sessionTimeoutSecs': session_timeout,
            'pageView': page_view
        }

        try:
            response = requests.post(
                '{}/register.do'.format(self.__default_gateway_address),
                data=data)
        except (requests.ConnectTimeout,
                requests.ConnectionError,
                requests.HTTPError):

            payment.status = Status.FAILED
            payment.save()
            raise NetworkException(payment.uid)

        if response.status_code != 200:
            payment.status = Status.FAILED
            payment.save()
            log = BankLog(
                request_type=LogType.CREATE,
                bank_id=payment.bank_id,
                payment_id=payment.uid,
                response_text=response.text)
            log.save()
            raise ProcessingException(payment.uid)

        try:
            response = response.json()
        except (ValueError, UnicodeDecodeError):
            payment.status = Status.FAILED
            payment.save()
            log = BankLog(
                request_type=LogType.CREATE,
                bank_id=payment.bank_id,
                payment_id=payment.uid,
                response_text=response.text)
            log.save()
            raise ProcessingException(payment.uid)

        if response.get('errorCode') and response.get('errorCode') != 200:
            payment.error_code = response.get('errorCode')
            payment.error_message = response.get('errorMessage')
            payment.status = Status.FAILED
            payment.save()
            log = BankLog(
                request_type=LogType.CREATE,
                bank_id=payment.bank_id,
                payment_id=payment.uid,
                response_json=response)
            log.save()
            raise ProcessingException(payment.uid)

        payment.bank_id = response.get('orderId')
        payment.status = Status.PENDING
        payment.details['redirect_url'] = response.get('formUrl')
        payment.save()
        log = BankLog(
            request_type=LogType.CREATE,
            bank_id=payment.bank_id,
            payment_id=payment.uid,
            response_json=response)
        log.save()

        return {
            'payment_bank_id': payment.bank_id,
            'payment_id': payment.uid,
            'redirect_url': payment.details.get("redirect_url")
        }

    def get_status(self, payment_id):
        try:
            payment = Payment.objects.get(pk=payment_id)
        except Payment.DoesNotExist:
            raise PaymentNotFoundException()

        if payment.status == Status.PENDING:
            data = {
                'userName': self.merchant.get('username'),
                'password': self.merchant.get('password'),
                'orderId': payment.bank_id,
            }
            try:
                response = requests.post(
                    '{}/getOrderStatus.do'
                    .format(self.__default_gateway_address), data)
            except (requests.ConnectTimeout,
                    requests.ConnectionError,
                    requests.HTTPError):

                payment.status = Status.FAILED
                payment.save()
                raise NetworkException(payment.uid)

            try:
                response = response.json()
            except (ValueError, UnicodeDecodeError):
                payment.status = Status.FAILED
                payment.save()
                log = BankLog(
                    request_type=LogType.CHECK_STATUS,
                    bank_id=payment.bank_id,
                    payment_id=payment.uid,
                    response_text=response.text)
                log.save()
                raise ProcessingException(payment.uid)

            log = BankLog(
                request_type=LogType.CHECK_STATUS,
                bank_id=payment.bank_id,
                payment_id=payment.uid,
                response_json=response)
            log.save()

            if response.get('OrderStatus') == 2:
                payment.status = Status.SUCCEEDED
                payment.save()

        return {
            'status': Status(payment.status),
            'amount': payment.amount,
            'created': payment.created,
            'updated': payment.updated
        }
