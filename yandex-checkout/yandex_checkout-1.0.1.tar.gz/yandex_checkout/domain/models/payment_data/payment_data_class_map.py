from yandex_checkout.domain.common.data_context import DataContext
from yandex_checkout.domain.common.payment_method_type import PaymentMethodType
from yandex_checkout.domain.models.payment_data.request.payment_data_alfabank import \
    PaymentDataAlfabank as RequestPaymentDataAlfabank
from yandex_checkout.domain.models.payment_data.request.payment_data_applepay import \
    PaymentDataApplepay as RequestPaymentDataApplepay
from yandex_checkout.domain.models.payment_data.request.payment_data_cash import \
    PaymentDataCash as RequestPaymentDataCash
from yandex_checkout.domain.models.payment_data.request.payment_data_bank_card import \
    PaymentDataBankCard as RequestPaymentDataBankCard
from yandex_checkout.domain.models.payment_data.request.payment_data_mobile_balance import \
    PaymentDataMobileBalance as RequestPaymentDataMobileBalance
from yandex_checkout.domain.models.payment_data.request.payment_data_sberbank import \
    PaymentDataSberbank as RequestPaymentDataSberbank
from yandex_checkout.domain.models.payment_data.request.payment_data_qiwi import \
    PaymentDataQiwi as RequestPaymentDataQiwi
from yandex_checkout.domain.models.payment_data.request.payment_data_webmoney import \
    PaymentDataWebmoney as RequestPaymentDataWebmoney
from yandex_checkout.domain.models.payment_data.request.payment_data_yandex_wallet import \
    PaymentDataYandexWallet as RequestPaymentDataYandexWallet

from yandex_checkout.domain.models.payment_data.response.payment_data_alfabank import \
    PaymentDataAlfabank as ResponsePaymentDataAlfabank
from yandex_checkout.domain.models.payment_data.response.payment_data_applepay import \
    PaymentDataApplepay as ResponsePaymentDataApplepay
from yandex_checkout.domain.models.payment_data.response.payment_data_cash import \
    PaymentDataCash as ResponsePaymentDataCash
from yandex_checkout.domain.models.payment_data.response.payment_data_bank_card import \
    PaymentDataBankCard as ResponsePaymentDataBankCard
from yandex_checkout.domain.models.payment_data.response.payment_data_mobile_balance import \
    PaymentDataMobileBalance as ResponsePaymentDataMobileBalance
from yandex_checkout.domain.models.payment_data.response.payment_data_sberbank import \
    PaymentDataSberbank as ResponsePaymentDataSberbank
from yandex_checkout.domain.models.payment_data.response.payment_data_qiwi import \
    PaymentDataQiwi as ResponsePaymentDataQiwi
from yandex_checkout.domain.models.payment_data.response.payment_data_webmoney import \
    PaymentDataWebmoney as ResponsePaymentDataWebmoney
from yandex_checkout.domain.models.payment_data.response.payment_data_yandex_wallet import \
    PaymentDataYandexWallet as ResponsePaymentDataYandexWallet


class PaymentDataClassMap(DataContext):
    def __init__(self):
        super(PaymentDataClassMap, self).__init__(('request', 'response'))

    @property
    def request(self):
        return {
            PaymentMethodType.ALFABANK: RequestPaymentDataAlfabank,
            PaymentMethodType.BANK_CARD: RequestPaymentDataBankCard,
            PaymentMethodType.CASH: RequestPaymentDataCash,
            PaymentMethodType.MOBILE_BALANCE: RequestPaymentDataMobileBalance,
            PaymentMethodType.SBERBANK: RequestPaymentDataSberbank,
            PaymentMethodType.YANDEX_MONEY: RequestPaymentDataYandexWallet,
            PaymentMethodType.QIWI: RequestPaymentDataQiwi,
            PaymentMethodType.WEBMONEY: RequestPaymentDataWebmoney,
            PaymentMethodType.APPLEPAY: RequestPaymentDataApplepay
        }

    @property
    def response(self):
        return {
            PaymentMethodType.ALFABANK: ResponsePaymentDataAlfabank,
            PaymentMethodType.BANK_CARD: ResponsePaymentDataBankCard,
            PaymentMethodType.CASH: ResponsePaymentDataCash,
            PaymentMethodType.MOBILE_BALANCE: ResponsePaymentDataMobileBalance,
            PaymentMethodType.SBERBANK: ResponsePaymentDataSberbank,
            PaymentMethodType.YANDEX_MONEY: ResponsePaymentDataYandexWallet,
            PaymentMethodType.QIWI: ResponsePaymentDataQiwi,
            PaymentMethodType.WEBMONEY: ResponsePaymentDataWebmoney,
            PaymentMethodType.APPLEPAY: ResponsePaymentDataApplepay
        }
