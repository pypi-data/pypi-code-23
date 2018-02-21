from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.views.generic.base import RedirectView, View

from ideal.client import IdealClient, TransactionStatus
from ideal.exceptions import IdealException

# from tests.proj.myapp.views import PaymentSuccess, PaymentFailed, IdealCallbackView
    # url(r'^ideal-callback/', IdealCallbackView.as_view()),
    # url(r'^payment-sucess/', PaymentSuccess.as_view()),
    # url(r'^payment-failed/', PaymentFailed.as_view()),

class IdealCallbackView(RedirectView):
    permanent = False

    def get_redirect_url(self, **kwargs):
        """
        Simplistic view to handle the callback. You probably want to update your database with the transaction
        status as well, or sent a confirmation email, etc.
        """
        client = IdealClient()

        try:
            response = client.get_transaction_status(self.request.GET.get('trxid'))
            if response.status == TransactionStatus.SUCCESS:
                # Redirect to some view with a success message.
                return reverse('payment-success')
        except IdealException, e:
            # Do something with the error message.
            error_message = e.message

        # Redirect to some view with a failure message.
        return reverse('payment-failed')


class PaymentSuccess(View):
    def get(self, request, *args, **kwargs):
        """
        Simple HTML message indicating a succesful payment.
        """
        return HttpResponse(content=b'<html><h1>Success</h1></html>!')


class PaymentFailed(View):
    def get(self, request, *args, **kwargs):
        """
        Simple HTML message indicating a failed payment.
        """
        return HttpResponse(content=b'<html><h1>Failed</h1></html>!')
