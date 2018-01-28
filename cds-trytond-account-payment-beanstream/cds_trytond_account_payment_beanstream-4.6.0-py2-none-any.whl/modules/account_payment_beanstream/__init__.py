# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.pool import Pool

from . import payment
from . import party

__all__ = ['register']

def register():
    Pool.register(
        payment.Account,
        payment.Journal,
        payment.Payment,
        payment.Group,
        payment.Customer,
        party.Party,
        module='account_payment_beanstream', type_='model')
