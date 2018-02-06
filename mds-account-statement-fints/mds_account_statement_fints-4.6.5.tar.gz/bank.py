# -*- coding: utf-8 -*-
# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.model import ModelView, ModelSQL, fields, Unique
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval
from trytond.transaction import Transaction


__all__ = ['Bank', 'BankAccountNumber', 'BankAccount']
__metaclass__ = PoolMeta
 

class Bank(ModelSQL, ModelView):
    'Bank'
    __name__ = 'bank'

    fintsblz = fields.Char(string=u'Bank code', size=10,
                    help=u"Bank code of your bank (not the BIC)")
    fintsurl = fields.Char(string=u'FinTS-URL', 
                    help=u"URL for accessing the FinTS interface of your bank")

    @classmethod
    def default_fintsurl(cls):
        return ''

# end Bank


class BankAccount(ModelSQL, ModelView):
    'Bank Account'
    __name__ = 'bank.account'

    owners_text = fields.Function(fields.Char('Owners', readonly=True), 
                    'on_change_with_owners_text')

    @fields.depends('owners')
    def on_change_with_owners_text(self, name=None):
        """ get owner as text
        """
        t1 = '-/-'
        if len(self.owners) > 0:
            t1 = self.owners[0].rec_name
        if len(self.owners) > 1:
            t1 += ', ...'
        return t1

    @fields.depends('owners', 'numbers')
    def on_change_owners(self):
        """ disable online access on account numbers if company is 
            not in owner list
        """
        context = Transaction().context
        company = context.get('company', -1)

        fnd1 = False
        if company != -1:
            for i in self.owners:
                if i.id == company:
                    fnd1 = True
                    break

        if (fnd1 == False) and self.numbers:
            for i in self.numbers:
                i.fints_ena = False
                i.fints_login = None
                i.fints_pin = None
                i.fints_name = None

# end BankAccount


class BankAccountNumber(ModelSQL, ModelView):
    'Bank Account Number'
    __name__ = 'bank.account.number'

    fints_ena = fields.Boolean(string=u'Enable online access',
            states={
                'invisible': ~Eval('context', {}).get('company', -1).in_(Eval('fints_company', [])),
            })
    fints_login = fields.Char(string=u'FinTS-Login', 
            help=u'Login name to access your bank account.',
            states={
                'required': Eval('fints_ena', False) == True,
                'invisible': Eval('fints_ena', False) == False,
                    }, depends=['fints_ena'])
    fints_pin = fields.Char(string=u'FinTS-PIN', 
            help=u'Your PIN to the login name, leave blank if you want to be asked on every access.',
            states={
                'invisible': Eval('fints_ena', False) == False,
            }, depends=['fints_ena'])
    fints_company = fields.Function(fields.One2Many('party.party', None,
            'Owner', states={'invisible': True}), 'on_change_with_fints_company')
    fints_name = fields.Char(string=u'Statement name', 
            help=u'Name to be used for bank statements',
            states={
                'required': Eval('fints_ena', False) == True,
                'invisible': Eval('fints_ena', False) == False,
            }, depends=['fints_ena'])

    @classmethod
    def __setup__(cls):
        super(BankAccountNumber, cls).__setup__()
        tab_accnm = cls.__table__()
        cls._sql_constraints.extend([
            ('uniq_name', 
            Unique(tab_accnm, tab_accnm.fints_name), 
            u'This name is already in use.'),
            ])

    @fields.depends('account')
    def on_change_with_fints_company(self, name=None):
        """ get owner
        """
        return [x.id for x in self.account.owners]

# end BankAccountNumber
