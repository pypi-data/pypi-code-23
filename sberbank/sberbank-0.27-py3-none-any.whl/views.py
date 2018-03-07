import hmac
from collections import OrderedDict
from hashlib import sha256

from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest

from sberbank.exceptions import PaymentNotFoundException
from sberbank.models import Payment, BankLog, Status, LogType


def callback(request):
    data = OrderedDict(sorted(request.GET.items(), key=lambda x: x[0]))

    try:
        payment = Payment.objects.get(bank_id=data.get('mdOrder'))
    except Payment.DoesNotExist:
        raise PaymentNotFoundException()

    log = BankLog(
        request_type=LogType.CALLBACK,
        bank_id=payment.bank_id,
        payment_id=payment.uid,
        response_json=data)

    log.save()

    check_str = ''

    for key, value in data.items():
        if key != 'checksum':
            check_str += f'{key};{value};'

    checksum = hmac.new(settings.SBERBANK_HASH_KEY.encode(),
                        check_str.encode(),
                        sha256).hexdigest().upper()

    if checksum != data.get('checksum'):
        payment.status = Status.FAILED
        payment.save()
        return HttpResponseBadRequest('Checksum check failed')

    if int(data.get('status')) == 1:
        payment.status = Status.SUCCEEDED
    elif int(data.get('status')) == 0:
        payment.status = Status.FAILED

    payment.save()

    return HttpResponse(status=200)
