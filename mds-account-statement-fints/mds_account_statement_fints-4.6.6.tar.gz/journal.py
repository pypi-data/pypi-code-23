# -*- coding: utf-8 -*-
# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.model import ModelView, ModelSQL, fields
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval

__all__ = ['Journal']
__metaclass__ = PoolMeta


class Journal(ModelSQL, ModelView):
    'Statement Journal'
    __name__ = 'account.statement.journal'

    fints_createbankaccounts = fields.Boolean(string=u'Create bank accounts',
        help=u'When importing online, new bank accounts are created automatically for the parties.')
    fints_bankcategory = fields.Many2One(model_name='party.category', 
                string=u'Category bank party', ondelete='SET NULL',
                help=u'the specified category is assigned to the party of the newly created bank',
                states={
                    'invisible': ~Eval('fints_createbankaccounts', False),
                }, depends=['fints_createbankaccounts'])
    fints_payercategory = fields.Many2One(model_name='party.category', 
                string=u'Category payer party', ondelete='SET NULL',
                help=u'The specified category is assigned to the payer/payee.')

    @classmethod
    def default_fints_createbankaccounts(cls):
        return True
        
# end Journal
