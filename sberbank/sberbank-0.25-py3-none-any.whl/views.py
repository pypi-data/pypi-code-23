import hmac
from hashlib import sha256
from uuid import UUID

from django.http import HttpResponse, HttpResponseBadRequest

from django.conf import settings
from sberbank.exceptions import PaymentNotFoundException
from sberbank.models import Payment, BankLog, Status, LogType


def callback(request):
    data = {
        'amount': request.GET.get('amount'),
        'bank_id': request.GET.get('mdOrder'),
        'payment_id': str(UUID(request.GET.get('orderNumber'))),
        'checksum': request.GET.get('checksum'),
        'operation': request.GET.get('operation'),
        'status': request.GET.get('status'),
    }

    try:
        payment = Payment.objects.get(bank_id=data.get('bank_id'))
    except Payment.DoesNotExist:
        raise PaymentNotFoundException()

    log = BankLog(
        request_type=LogType.CALLBACK,
        bank_id=payment.bank_id,
        payment_id=payment.uid,
        response_json=data)

    log.save()

    check_str = 'amount;{};mdOrder;{};operation;{};orderNumber;{};status;{};' \
        .format(
            data.get('amount'),
            data.get('bank_id'),
            data.get('operation'),
            data.get('payment_id'),
            data.get('status'))

    checksum = hmac.new(settings.SBERBANK_HASH_KEY.encode(), check_str.encode(),
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
