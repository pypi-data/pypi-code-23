import json
import textwrap
from collections import OrderedDict

from django.contrib import messages
from django.template.loader import get_template
from django.utils.translation import ugettext_lazy as _
from i18nfield.fields import I18nFormField, I18nTextarea
from i18nfield.strings import LazyI18nString

from pretix.base.payment import BasePaymentProvider

from .frontend import MABEL_USER_TYPE_KEY, UserType


class CollegeBill(BasePaymentProvider):
    identifier = 'collegebill'
    verbose_name = _('College Bill')

    @property
    def settings_form_fields(self):
        form_field = I18nFormField(
            label=_('College Bill Information'),
            widget=I18nTextarea,
            help_text=_('Include everything that your customers need to know about paying by college bill. '
                        'For example, make it clear that this option should only be selected by current students '
                        'of the college - other CRSIDs will be rejected by the accounts office, and their payment will fail.'),
            widget_kwargs={'attrs': {
                'rows': '2',
                'placeholder': _(
                    'After completing your purchase, we will contact the college bursary, to ask that '
                    'the value of your tickets be added to your college bill at the end of term.'
                )
            }}
        )
        return OrderedDict(
            list(super().settings_form_fields.items()) +
            [('college_bill_details', form_field)]
        )

    def payment_form_render(self, request) -> str:
        template = get_template('pretix_mabel/checkout_payment_form.html')
        ctx = {
            'request': request,
            'event': self.event,
            'details': self.settings.get('college_bill_details', as_type=LazyI18nString),
        }
        return template.render(ctx)

    def checkout_prepare(self, request, total):
        return True

    def payment_is_allowed(self, request):
        print("Checking if allowed")
        print(request)
        return True

    def payment_is_valid_session(self, request):
        user_type = UserType[request.session.get(MABEL_USER_TYPE_KEY)]
        if not user_type == UserType.COLLEGE_STUDENT:
            messages.error(request, _(
                "Only current students may pay for tickets via their college bill."))
            return False
        return True

    def checkout_confirm_render(self, request):
        return self.payment_form_render(request)

    def order_pending_mail_render(self, order) -> str:
        template = get_template('pretix_mabel/order_pending.txt')
        ctx = {
            'event': self.event,
            'order': order,
            'details': textwrap.indent(str(self.settings.get('college_bill_details', as_type=LazyI18nString)), '    '),
        }
        return template.render(ctx)

    def order_pending_render(self, request, order) -> str:
        template = get_template('pretix_mabel/pending.html')
        ctx = {
            'event': self.event,
            'order': order,
            'details': self.settings.get('college_bill_details', as_type=LazyI18nString),
        }
        return template.render(ctx)

    def order_control_render(self, request, order) -> str:
        if order.payment_info:
            payment_info = json.loads(order.payment_info)
        else:
            payment_info = None
        template = get_template('pretix_mabel/control.html')
        ctx = {'request': request, 'event': self.event,
               'payment_info': payment_info, 'order': order}
        return template.render(ctx)


class Cheque(BasePaymentProvider):
    identifier = 'cheque'
    verbose_name = _('Cheque')

    @property
    def settings_form_fields(self):
        form_field = I18nFormField(
            label=_('Cheque Payment Instructions'),
            widget=I18nTextarea,
            help_text=_(
                'Include everything that your customers need to know about paying by cheque. Where the cheque should be sent, how it should be marked up, etc...'),
            widget_kwargs={'attrs': {
                'rows': '2',
                'placeholder': _(
                    'Cheques should be made payable to Super Event Committee, and posted to: ...'
                )
            }}
        )
        return OrderedDict(
            list(super().settings_form_fields.items()) +
            [('cheque_details', form_field)]
        )

    def payment_form_render(self, request) -> str:
        template = get_template('pretix_mabel/checkout_payment_form.html')
        ctx = {
            'request': request,
            'event': self.event,
            'details': self.settings.get('cheque_details', as_type=LazyI18nString),
        }
        return template.render(ctx)

    def checkout_prepare(self, request, total):
        return True

    def payment_is_allowed(self, request):
        return True

    def payment_is_valid_session(self, request):
        return True

    def checkout_confirm_render(self, request):
        return self.payment_form_render(request)

    def order_pending_mail_render(self, order) -> str:
        template = get_template('pretix_mabel/order_pending_cheque.txt')
        ctx = {
            'event': self.event,
            'order': order,
            'details': textwrap.indent(str(self.settings.get('cheque_details', as_type=LazyI18nString)), '    '),
        }
        return template.render(ctx)

    def order_pending_render(self, request, order) -> str:
        template = get_template('pretix_mabel/pending_cheque.html')
        ctx = {
            'event': self.event,
            'order': order,
            'details': self.settings.get('cheque_details', as_type=LazyI18nString),
        }
        return template.render(ctx)

    def order_control_render(self, request, order) -> str:
        if order.payment_info:
            payment_info = json.loads(order.payment_info)
        else:
            payment_info = None
        template = get_template('pretix_mabel/control_cheque.html')
        ctx = {'request': request, 'event': self.event,
               'payment_info': payment_info, 'order': order}
        return template.render(ctx)
