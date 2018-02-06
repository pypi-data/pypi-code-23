from uuid import UUID

from django.http import HttpResponse

from sberbank.models import Payment, BankLog, Status, LogType
from sberbank.exceptions import ProcessingException, PaymentNotFoundException


def callback(request):
    data = {
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

    log = BankLog(request_type=LogType.CALLBACK, bank_id=payment.bank_id, payment_id=payment.uid, response_json=data)
    log.save()

    if int(data.get('status')) == 1:
        payment.status = Status.SUCCEEDED
    elif int(data.get('status')) == 0:
        payment.status = Status.FAILED

    payment.save()

    return HttpResponse(status=200)
