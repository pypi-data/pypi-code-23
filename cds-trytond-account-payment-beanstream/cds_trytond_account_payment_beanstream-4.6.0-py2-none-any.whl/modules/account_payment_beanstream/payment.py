# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
import uuid
import logging

from beanstream import billing as beanstream_billing
from beanstream import gateway as beanstream_gateway

from trytond.model import ModelSQL, ModelView, Workflow, fields
from trytond.pool import PoolMeta, Pool
from trytond.pyson import Eval
from trytond.transaction import Transaction
from trytond.wizard import Wizard, StateView, StateAction, Button

__all__ = ['Account', 'Journal', 'Payment', 'Group', 'Customer']
logger = logging.getLogger(__name__)

_STATES = {
    'readonly': Eval('state') != 'draft',
    }
_DEPENDS = ['state']

_CARDTYPES = [
             (None, ''),
             ('VI', 'Visa'),
             ('PV', 'Visa Debit'),
             ('MC', 'MasterCard'),
             ('AM', 'American Express'),
             ('NN', 'Discover'),
             ('DI', 'Diners'),
             ('JB', 'JCB'),
             ('IO', 'INTERAC Online'),
             ('ET', 'Direct Debit/Direct Payments/ACH'),
             ]

class Account(ModelSQL, ModelView):
    "Beanstream Account"
    __name__ = 'account.payment.beanstream.account'

    name = fields.Char("Name", required=True)
    merchant_id = fields.Char("Merchant ID", required=True)
    order_api_passcode = fields.Char("Order API Passcode", required=True)
    profile_api_passcode = fields.Char("Profile API Passcode")
    reporting_api_passcode = fields.Char("Reporting API Passcode")
    recurring_api_passcode = fields.Char("Recurring Payment API Passcode")
    require_billing_address = fields.Boolean("Billing Address Required")
    require_cvd = fields.Boolean("CVD Code Required")


class Journal:
    __metaclass__ = PoolMeta
    __name__ = 'account.payment.journal'

    beanstream_account = fields.Many2One(
        'account.payment.beanstream.account', "Account", ondelete='RESTRICT',
        states={
            'required': Eval('process_method') == 'beanstream',
            'invisible': Eval('process_method') != 'beanstream',
            },
        depends=['process_method'])

    @classmethod
    def __setup__(cls):
        super(Journal, cls).__setup__()
        beanstream_method = ('beanstream', 'Beanstream Payment Fields')
        if beanstream_method not in cls.process_method.selection:
            cls.process_method.selection.append(beanstream_method)


class Payment:
    __metaclass__ = PoolMeta
    __name__ = 'account.payment'

    beanstream_token = fields.Char("Beanstream Token", readonly=True)
    beanstream_ccname = fields.Char("Cardholder's Name")
    beanstream_cardtype = fields.Selection(_CARDTYPES, 'Card Type',
                          readonly=True)
    beanstream_cardtype_text = fields.Function(
                               fields.Char("Card Type Text"),
                               'get_beanstream_cardtype_text')
    beanstream_transid =  fields.Char("Beanstream Trans. ID", readonly=True)
    beanstream_authcode = fields.Char("Authorization Code", readonly=True)
    beanstream_ccmessage = fields.Char("Message to Cardholder",
                           readonly=True)
    beanstream_response = fields.Text("Beanstream Response Data",
                          readonly=True)

    @classmethod
    def __setup__(cls):
        super(Payment, cls).__setup__()

    @fields.depends('beanstream_cardtype')
    def get_beanstream_cardtype_text(self, name=None):
        return dict(_CARDTYPES)[self.beanstream_cardtype]


class Group:
    __metaclass__ = PoolMeta
    __name__ = 'account.payment.group'

    @classmethod
    def __setup__(cls):
        super(Group, cls).__setup__()
        cls._error_messages.update({
                'no_beanstream_token': ('So beanstream token '
                    'for payment "%(payment)s".'),
                })

    def process_beanstream(self):
        pool = Pool()
        Payment = pool.get('account.payment')
        to_process = list(self.payments)
        # TODO: Handle payment profiles?
        for payment in list(to_process):
            if not payment.beanstream_ccname:
                payment.beanstream_ccname = payment.party.name
            if not payment.beanstream_token:
                to_process.remove(payment)
        Payment.save(self.payments)
        self.payments = to_process

    def charge_beanstream(self):
        pool = Pool()
        Payment = pool.get('account.payment')
        Sale = pool.get('sale.sale')
        account = self.journal.beanstream_account
        good_payments = []
        bad_payments = []
        gw = beanstream_gateway.Beanstream(
            require_billing_address=account.require_billing_address,
            require_cvd=account.require_cvd)
        gw.configure(
            account.merchant_id,
            payment_passcode=account.order_api_passcode,
            payment_profile_passcode=account.profile_api_passcode,
            recurring_billing_passcode=account.recurring_api_passcode,
            reporting_passcode=account.reporting_api_passcode) 
          
        for payment in self.payments:
            addr = beanstream_billing.Address(
                   payment.party.name,
                   payment.party.email,
                   phone=payment.party.phone)
            if isinstance(payment.origin, Sale):
                inv_addr = payment.origin.invoice_address
                addr.address1 = inv_addr.street
                addr.address2 = inv_addr.name
                addr.city = inv_addr.city
                addr.province = inv_addr.subdivision.code[-2:]
                addr.postal_code = inv_addr.zip
                addr.country = inv_addr.country.code
            txn = gw.purchase_with_token(payment.amount,
                payment.beanstream_token)
            txn.set_cardholder_name(payment.beanstream_ccname)
            txn.set_billing_address(addr)
            resp = txn.commit()
            payment.beanstream_response = resp.get_whole_response()
            resp_obj = eval(resp.get_whole_response())
            try:
                payment.beanstream_ccmessage = resp.get_cardholder_message()
            except KeyError as e:
                payment.beanstream_ccmessage = "ERR: " + e.message
            payment.beanstream_cardtype = resp_obj.get('cardType', [None])[0]
            payment.beanstream_transid = resp_obj.get('trnId', [None])[0]
            if resp.approved():
                payment.beanstream_authcode = resp_obj.get('authCode', [None])[0]
                good_payments.append(payment)
            else:
                bad_payments.append(payment)

        Payment.save(self.payments)
        if good_payments:
            Payment.succeed(good_payments)
        if bad_payments:
            Payment.fail(bad_payments)

class Customer(ModelSQL, ModelView):
    "Beanstream Customer"
    __name__ = 'account.payment.beanstream.customer'
    _history = True
    party = fields.Many2One('party.party', "Party", required=True, select=True)
    beanstream_token = fields.Char("Beanstream Token", readonly=True)
    beanstream_account = fields.Many2One(
        'account.payment.beanstream.account', "Account", required=True)
    beanstream_customerid = fields.Char("Beanstream Customer ID", required=True)
    beanstream_ccname = fields.Char("Cardholder's Name")
    active = fields.Boolean("Active")

    @classmethod
    def default_active(cls):
        return True

