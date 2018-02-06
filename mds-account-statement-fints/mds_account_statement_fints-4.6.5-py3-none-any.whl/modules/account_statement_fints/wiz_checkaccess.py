# -*- coding: utf-8 -*-
# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.model import ModelView, ModelSQL, fields
from trytond.wizard import Wizard, StateTransition, StateView, Button, StateAction
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval, Len
from trytond.transaction import Transaction
from urllib.parse import urlparse
from fints.client import FinTS3PinTanClient
from fints.models import SEPAAccount


__all__ = ['CheckBankAccessWizard', 'EnterPINView', 'CheckResult']
__metaclass__ = PoolMeta


CONNCHECK_SUCCESS = 'success'
CONNCHECK_ERROR = 'error'
sel_resultstate = [
        (CONNCHECK_SUCCESS, u'Successful'),
        (CONNCHECK_ERROR, u'Error'),
    ]

class EnterPINView(ModelView):
    'Enter PIN'
    __name__ = 'account_statement_fints.wiz_checkbankaccess.enterpin'

    accountnum = fields.Many2One(model_name='bank.account.number', 
                    string=u'Bank Account Number', readonly=True)
    fintspin = fields.Char(string=u'PIN', required=True)
    bankname = fields.Char(string=u'Bank', readonly=True)
    accountnumbers = fields.One2Many(model_name='bank.account.number', 
                    field=None, string=u'Numbers', 
                    states={'invisible': True})

# ende EnterPINView


class CheckResult(ModelView):
    'Check Result'
    __name__ = 'account_statement_fints.wiz_checkbankaccess.checkresult'
    
    accountnum = fields.Many2One(model_name='bank.account.number', 
                    string=u'Bank Account Number', readonly=True)
    accountnumbers = fields.One2Many(model_name='bank.account.number', 
                    field=None, string=u'Numbers', 
                    states={'invisible': True})
    resultstate = fields.Selection(string=u'Result', selection=sel_resultstate,
                    readonly=True)
    infotxt = fields.Text(string=U'Info', readonly=True)
    bankname = fields.Char(string=u'Bank', readonly=True)
    
# end CheckResult


class CheckBankAccessWizard(Wizard):
    'check online access'
    __name__ = 'account_statement_fints.wiz_checkbankaccess'

    start_state = 'selaccounts'
    
    selaccounts = StateTransition()
    enterpin = StateView(
            model_name='account_statement_fints.wiz_checkbankaccess.enterpin', \
            view='account_statement_fints.wiz_checkbankaccess_enterpin_form', \
            buttons=[Button(string=u'Cancel', state='end', icon='tryton-cancel'), 
                     Button(string=u'Test connection', default=True,
                            state='testconnection', icon='tryton-go-next')
                    ]
            )
    testconnection = StateTransition()
    checkresult = StateView(model_name='account_statement_fints.wiz_checkbankaccess.checkresult', \
            view='account_statement_fints.wiz_checkbankaccess_checkresult_form', \
            buttons=[
                    Button(string=u'next connection', state='selnext', icon='tryton-go-next',
                        states={
                            'invisible': Len(Eval('accountnumbers')) < 2,
                        }),
                    Button(string=u'Close', state='end', icon='tryton-close')
                ]
            )
    selnext = StateTransition()
    
    @classmethod
    def __setup__(cls):
        super(CheckBankAccessWizard, cls).__setup__()
        cls._error_messages.update({
                'checkaccess_wrongmodel': (u"FinTS: The access-check must be done from an account number."),
                'checkaccess_noaccounts': (u"FinTS: no account numbers available for testing."),
                'checkaccess_nourl': (u"FinTS: The FinTS URL for the bank '%s' is not set. Please complete this setting."),
            })

    def transition_selaccounts(self):
        """ select accounts to check
            Test if we have to ask for the PIN
        """
        context = Transaction().context
        if context['active_model'] != 'bank.account':
            self.raise_user_error('checkaccess_wrongmodel')
        
        # search for account numbers with online access
        AccountNumber = Pool().get('bank.account.number')
        accountnum_lst = AccountNumber.search([
                    ('account.id', 'in', context['active_ids']), 
                    ('fints_ena', '=', True)
                ])

        if len(accountnum_lst) == 0:
            self.raise_user_error('checkaccess_noaccounts')
        else :
            # use first account, ask for PIN if needed
            self.enterpin.accountnumbers = accountnum_lst
            self.enterpin.accountnum = accountnum_lst[0]
            return self.switch_enterpin(accountnum_lst[0])
    
    def switch_enterpin(self, accnum):
        """ switch between 'enterpin' and 'textconnection'
        """
        self.check_logindata(accnum)
        if self.has_pin(accnum) == False:
            return 'enterpin'
        else :
            self.enterpin.fintspin = accnum.fints_pin
            return 'testconnection'

    def transition_selnext(self):
        """ step: select next connection to test
        """
        self.enterpin.accountnumbers = self.checkresult.accountnumbers
        if self.checkresult.accountnum != self.checkresult.accountnumbers[-1]:
            p1 = self.checkresult.accountnumbers.index(self.checkresult.accountnum)
            if (p1 + 1) < len(self.checkresult.accountnumbers):
                self.enterpin.accountnum = self.checkresult.accountnumbers[p1 + 1]
                return self.switch_enterpin(self.enterpin.accountnum)
            else :
                return 'end'
        else :
            return 'end'

    def transition_testconnection(self):
        """ step: enterpin/start --> test connection --> show result
        """
        # account to check is: self.enterpin.accountnum
        accnm = self.enterpin.accountnum
        f = FinTS3PinTanClient(
                accnm.account.bank.fintsblz,    # bank code
                accnm.fints_login,              # username
                self.enterpin.fintspin,         # pin
                accnm.account.bank.fintsurl     # url
                )
        try :
            l1 = f.get_sepa_accounts()
            self.checkresult.resultstate = CONNCHECK_SUCCESS
            self.checkresult.infotxt = u'found bank accounts:\n'
            cnt1 = 1
            for i in l1:
                if not isinstance(i, type(SEPAAccount(1,2,3,4,5))):
                    raise ValueError(u'wrong result: %s' % str(i))
                self.checkresult.infotxt += u'---- SEPA-Account - No. %d ---\n' % cnt1
                cnt1 += 1
                self.checkresult.infotxt += u'IBAN: %s\nBIC: %s\nAccount-No: %s\nBLZ: %s\n' % \
                    (i.iban, i.bic, i.accountnumber, i.blz)
        except Exception as err:
            self.checkresult.resultstate = CONNCHECK_ERROR
            self.checkresult.infotxt = "Exception: {0}".format(err)
            self.checkresult.infotxt += u'\n\nPlease check URL, login data and bank code.'

        del f
        self.checkresult.accountnum = self.enterpin.accountnum
        self.checkresult.accountnumbers = self.enterpin.accountnumbers
        return 'checkresult'

    def default_checkresult(self, fields):
        """ setup form
        """
        r1 = {}
        r1['accountnum'] = self.checkresult.accountnum.id
        r1['resultstate'] = self.checkresult.resultstate
        r1['accountnumbers'] = [x.id for x in self.checkresult.accountnumbers]
        r1['bankname'] = self.checkresult.accountnum.account.bank.party.rec_name
        r1['infotxt'] = self.checkresult.infotxt
        return r1

    def default_enterpin(self, fields):
        """ setup form
        """
        r1 = {}
        r1['accountnum'] = self.enterpin.accountnum.id
        r1['accountnumbers'] = [x.id for x in self.enterpin.accountnumbers]
        r1['bankname'] = self.enterpin.accountnum.account.bank.party.rec_name
        r1['fintspin'] = ''
        return r1
        
    def check_logindata(self, accnum):
        """ check if the account number has url and loginname
        """
        # bank
        if isinstance(accnum.account.bank.fintsurl, type(None)):
            self.raise_user_error('checkaccess_nourl', (accnum.account.bank.party.rec_name))
        url_o = urlparse(accnum.account.bank.fintsurl)
        if (len(url_o.scheme) == 0) or (len(url_o.netloc) == 0):
            self.raise_user_error('checkaccess_nourl', (accnum.account.bank.party.rec_name))

    def has_pin(self, accnum):
        """ result: True if PIN exists
        """
        if isinstance(accnum.fints_pin, type('')):
            if len(accnum.fints_pin) > 0:
                return True
        return False
        
# end CheckBankAccessWizard
