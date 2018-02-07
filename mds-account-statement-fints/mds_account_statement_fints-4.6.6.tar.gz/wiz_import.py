# -*- coding: utf-8 -*-
# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.model import ModelView, ModelSQL, fields
from trytond.wizard import Wizard, StateTransition, StateView, Button, StateAction
from trytond.transaction import Transaction
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval, Len, Or, And
from datetime import date, timedelta
from decimal import Decimal
from fints.client import FinTS3PinTanClient
from fints.models import SEPAAccount
import mt940.models, json, hashlib
from sql.functions import Position, Lower, Substring
from sqlextension import Replace


__all__ = ['ImportByFinTSWizard', 'SelectAccounts', 'EnterImportData','CheckImportResult']
__metaclass__ = PoolMeta


WIZSTATE_SUCCESS = 'success'
WIZSTATE_ERROR = 'error'
WIZSTATE_ACCNOTFOUND = 'accnotfound'
WIZSTATE_NO_LINES_RECEIVED = 'nolinesrec'
WIZSTATE_NO_NEW_LINES_RECEIVED = 'nonewlines'
sel_resultstate = [
        (WIZSTATE_SUCCESS, u'Successful'),
        (WIZSTATE_ERROR, u'Error'),
        (WIZSTATE_ACCNOTFOUND, u'Account not found'),
        (WIZSTATE_NO_LINES_RECEIVED, u'Successful: but no bank statement lines received from the bank.'),
        (WIZSTATE_NO_NEW_LINES_RECEIVED, u'Successful: No bank statement created. Only already known lines were received.')
    ]


class CheckImportResult(ModelView):
    'Check import result'
    __name__ = 'account_statement_fints.wiz_import.checkresult'
    
    accountnum = fields.Many2One(model_name='bank.account.number', 
                    string=u'Bank Account Number', readonly=True)
    accountnumbers = fields.One2Many(model_name='bank.account.number', 
                    field=None, string=u'Numbers', 
                    states={'invisible': True})
    resultstate = fields.Selection(string=u'Result', selection=sel_resultstate,
                    readonly=True)
    bankname = fields.Char(string=u'Bank', readonly=True)
    balance_val = fields.Numeric(string=u'Balance amount', readonly=True,
                    help=u'Account balance transmitted by your bank',
                    digits=(16, Eval('currency_digits', 2)))
    balance_date = fields.Date(string=u'Balance date', readonly=True,
                    help=u'Date of the account balance')
    nolines = fields.Integer(string=u'Number of lines', readonly=True,
                    help=u'Number of received lines in the bank statement')
    newlines = fields.Integer(string=u'New lines', readonly=True,
                    help=u'Number of new lines in the bank statement')
    doubleline = fields.Integer(string=u'Double lines', readonly=True,
                    help=u'Number of double lines in the bank statement')
    banknew = fields.Integer(string=u'New banks', readonly=True,
                    help=u'Number of new created banks.')
    bankaccnew = fields.Integer(string=u'New banks accounts', readonly=True,
                    help=u'Number of new created bank accounts.')
    infotxt = fields.Text(string=U'Info', readonly=True,
                    states={'invisible': Len(Eval('infotxt', '')) == 0})
    currency_digits = fields.Function(fields.Integer('Currency Digits', 
                    states={'invisible': True}), 'on_change_with_currency_digits')
    statements = fields.One2Many(model_name='account.statement', field=None, 
                    string=u'New statements', states={'invisible': True}, readonly=True)
    lastitem = fields.Boolean(string=u'last item', readonly=True, states={'invisible': True})

    @fields.depends('journal')
    def on_change_with_currency_digits(self, name=None):
        if self.journal:
            return self.journal.currency.digits
        return 2

# end CheckImportResult


class EnterImportData(ModelView):
    'Enter data for import'
    __name__ = 'account_statement_fints.wiz_import.enterdata'

    accountnumbers = fields.One2Many(model_name='bank.account.number', 
                    field=None, string=u'Accounts numbers', 
                    states={'invisible': True})
    accountnum = fields.Many2One(model_name='bank.account.number', 
                    string=u'Bank Account Number', readonly=True)
    bankname = fields.Char(string=u'Bank', readonly=True)
    fintspin = fields.Char(string=u'PIN', required=True)
    datestart = fields.Date(string=u'Start date', required=True, 
                    help=u'Start date for retrieving the bank statement. Automatically set to last end date minus 2 days.')
    dateend = fields.Date(string=u'End date', required=True, readonly = True,
                    help=u"End date for retrieving the bank statement. Automatically set to 'Today'.")
    journal = fields.Many2One(model_name='account.statement.journal', 
                    required=True, string=u'Journal',
                    help=u'Bank statement journal for the current bank account.',
                    domain=[
                        ('company', '=', Eval('context', {}).get('company', -1)),
                        ('bank_account', '=', Eval('accountnum')),
                    ])
    last_date = fields.Date(string=u'last statement', readonly=True)
    last_balance = fields.Numeric(string=u'last balance', readonly=True,
                    digits=(16, Eval('currency_digits', 2)))
    currency_digits = fields.Function(fields.Integer('Currency Digits', 
                    states={'invisible': True}), 'on_change_with_currency_digits')
    skipknownlines = fields.Boolean(string=u'Skip known bank statement lines', 
                    help=u'The import will recognize bank statement lines that have already been saved and will not save them again.')
    linkinvoice = fields.Boolean(string=u'Link invoices to bank statement lines', 
                    help=u'The import will connect unpaid invoices with matching bank statement lines.')
    statements = fields.One2Many(model_name='account.statement', field=None, readonly=True,
                    string=u'New statements', states={'invisible': True})

    @fields.depends('journal')
    def on_change_with_currency_digits(self, name=None):
        if self.journal:
            return self.journal.currency.digits
        return 2

# end EnterImportData


class SelectAccounts(ModelView):
    'Select Accounts'
    __name__ = 'account_statement_fints.wiz_import.selaccounts'

    accountnumbers = fields.One2Many(model_name='bank.account.number', 
                    field=None, string=u'Accounts numbers',
                    domain=[
                        ('fints_ena', '=', True),
                        ('account.owners', '=', Eval('context', {}).get('company', -1))
                    ])

# end SelectAccounts


class ImportByFinTSWizard(Wizard):
    'import by FinTS'
    __name__ = 'account_statement_fints.wiz_import'

    start_state = 'selaccount'

    selaccount = StateView(
            model_name='account_statement_fints.wiz_import.selaccounts', \
            view='account_statement_fints.wiz_import_selaccounts_form', \
            buttons=[Button(string=u'Cancel', state='end', icon='tryton-cancel'), 
                     Button(string=u'Start import', default=True,
                            state='importstart', icon='tryton-go-next')
                    ]
            )
    importstart = StateTransition()
    enterdata = StateView(
            model_name='account_statement_fints.wiz_import.enterdata', \
            view='account_statement_fints.wiz_import_enterdata_form', \
            buttons=[Button(string=u'Cancel', state='end', icon='tryton-cancel'), 
                     Button(string=u'Import statement', default=True,
                            state='importstatement', icon='tryton-go-next')
                    ]
            )
    importstatement = StateTransition()
    checkresult = StateView(
            model_name='account_statement_fints.wiz_import.checkresult', \
            view='account_statement_fints.wiz_import_checkresult_form', \
            buttons=[
                    Button(string=u'show bank statements', state='shownewstatements', 
                        icon='tryton-open',
                        states={
                            'invisible': ~And(
                                    Eval('lastitem', False), 
                                    Len(Eval('statements')) > 0
                                ),
                        }),
                    Button(string=u'next statement', state='selnext', icon='tryton-go-next',
                        states={
                            'invisible': Or(
                                    Len(Eval('accountnumbers')) < 2,
                                    Eval('lastitem', False),
                                ),
                        }),
                    Button(string=u'Close', state='end', icon='tryton-close')
                ]
            )
    selnext = StateTransition()
    shownewstatements = StateAction('account_statement.act_statement_form')

    def do_shownewstatements(self, action):
        data = {'res_id': list(map(int, self.checkresult.statements))}
        if len(self.checkresult.statements) == 1:
            action['views'].reverse()
        return action, data

    def transition_selnext(self):
        """ step: select next connection to test
        """
        self.enterdata.accountnumbers = self.checkresult.accountnumbers
        self.enterdata.statements = self.checkresult.statements
        if self.checkresult.accountnum != self.checkresult.accountnumbers[-1]:
            p1 = self.checkresult.accountnumbers.index(self.checkresult.accountnum)
            if (p1 + 1) < len(self.checkresult.accountnumbers):
                self.enterdata.accountnum = self.checkresult.accountnumbers[p1 + 1]
                return 'enterdata'
            else :
                return 'end'
        else :
            return 'end'

    def transition_importstatement(self):
        """ load the statement
        """
        accnm = self.enterdata.accountnum
        f = FinTS3PinTanClient(
                accnm.account.bank.fintsblz,    # bank code
                accnm.fints_login,              # username
                self.enterdata.fintspin,        # pin
                accnm.account.bank.fintsurl     # url
                )
        
        self.checkresult.infotxt = ''
        self.checkresult.balance_val = None
        self.checkresult.balance_date = None
        self.checkresult.nolines = None
        self.checkresult.newlines = None
        self.checkresult.doubleline = None
        self.checkresult.resultstate = None
        self.checkresult.banknew = None
        self.checkresult.bankaccnew = None
        
        try :
            # get list of bank accounts
            l1 = f.get_sepa_accounts()

            # select bank account
            fnd1 = False
            for i in l1:
                if not isinstance(i, type(SEPAAccount(1,2,3,4,5))):
                    raise ValueError(u'wrong result: %s' % str(i))
                if i.iban == accnm.number_compact:
                    # load statements and balance from bank
                    fnd1 = True
                    statlst = f.get_statement(i, self.enterdata.datestart, self.enterdata.dateend)
                    self.checkresult.nolines = len(statlst)

                    # balance
                    bal1 = f.get_balance(i)
                    self.checkresult.balance_val = bal1.amount.amount
                    self.checkresult.balance_date = bal1.date

                    # create statement
                    if len(statlst) > 0:
                        n1 = self.save_statement(
                                statlst, 
                                accnm,
                                self.enterdata.journal, 
                                self.enterdata.datestart,
                                self.enterdata.dateend,
                                bal1.amount.amount
                            )
                        if n1 == 0:
                            self.checkresult.resultstate = WIZSTATE_NO_NEW_LINES_RECEIVED
                        else :
                            self.checkresult.resultstate = WIZSTATE_SUCCESS
                    else :
                        self.checkresult.resultstate = WIZSTATE_NO_LINES_RECEIVED

                    break
            if fnd1 == False:
                self.checkresult.resultstate = WIZSTATE_ACCNOTFOUND
        except Exception as err:
            Transaction().rollback()
            self.checkresult.resultstate = WIZSTATE_ERROR
            self.checkresult.infotxt = str(err)
            self.checkresult.infotxt += u'\n\nPlease check URL, login data and bank code.'

        del f
        self.checkresult.accountnum = self.enterdata.accountnum
        self.checkresult.accountnumbers = self.enterdata.accountnumbers
        self.checkresult.statements = self.enterdata.statements
        return 'checkresult'
        
    def transition_importstart(self):
        """ import statements of selected account
        """
        self.enterdata.accountnumbers = self.selaccount.accountnumbers
        self.enterdata.accountnum = self.selaccount.accountnumbers[0]
        self.enterdata.statements = []
        return 'enterdata'
    
    def default_enterdata(self, fields):
        """ setup form: 'enterdata'
        """
        context = Transaction().context
        pool = Pool()
        StatementJourn = pool.get('account.statement.journal')
        AccountStatement = pool.get('account.statement')
        
        r1 = {}
        r1['statements'] = [x.id for x in self.enterdata.statements]
        r1['accountnumbers'] = [x.id for x in self.enterdata.accountnumbers]
        r1['accountnum'] = self.enterdata.accountnum.id
        r1['bankname'] = self.enterdata.accountnum.account.bank.party.rec_name
        r1['fintspin'] = self.enterdata.accountnum.fints_pin
        r1['skipknownlines'] = True
        r1['linkinvoice'] = True
        
        # get journal for current bank
        journ_lst = StatementJourn.search([
                    ('company', '=', context.get('company', -1)),
                    ('bank_account', '=', self.enterdata.accountnum),
                ])
        if len(journ_lst) > 0:
            r1['journal'] = journ_lst[0].id

            # get date of last statement for this bank (same journal)
            statements = AccountStatement.search([
                    ('company', '=', context.get('company', -1)),
                    ('journal', '=', r1['journal']),
                ], order=[('date', 'DESC'), ('id', 'DESC')], limit=1)
            if len(statements) > 0:
                # set the start date before the last account statement 
                # to pick up any later arrived payments
                r1['datestart'] = statements[0].date - timedelta(days=1)
                r1['last_date'] = statements[0].date
                r1['last_balance'] = statements[0].end_balance
            else :
                r1['datestart'] = date.today() - timedelta(days=2)
        else :
            r1['datestart'] = date.today() - timedelta(days=2)
        r1['dateend'] = date.today()
        return r1

    def default_selaccount(self, fields):
        """ setup form 'selaccounts'
        """
        context = Transaction().context
        r1 = {}

        # get accountnumbers with online access
        AccountNumber = Pool().get('bank.account.number')
        accountnum_lst = AccountNumber.search([
                    ('fints_ena', '=', True),
                    ('account.owners', '=', context.get('company', -1)),
                ])
        r1['accountnumbers'] = [x.id for x in accountnum_lst]
        return r1

    def default_checkresult(self, fields):
        """ setup form
        """
        r1 = {}
        r1['statements'] = [x.id for x in self.checkresult.statements]
        r1['accountnum'] = self.checkresult.accountnum.id
        r1['accountnumbers'] = [x.id for x in self.checkresult.accountnumbers]
        r1['resultstate'] = self.checkresult.resultstate
        r1['bankname'] = self.checkresult.accountnum.account.bank.party.rec_name
        r1['balance_val'] = self.checkresult.balance_val
        r1['balance_date'] = self.checkresult.balance_date
        r1['nolines'] = self.checkresult.nolines
        r1['newlines'] = self.checkresult.newlines
        r1['doubleline'] = self.checkresult.doubleline
        r1['banknew'] = self.checkresult.banknew
        r1['bankaccnew'] = self.checkresult.bankaccnew
        r1['infotxt'] = self.checkresult.infotxt
        r1['lastitem'] = False
        if self.checkresult.accountnum == self.checkresult.accountnumbers[-1]:
            r1['lastitem'] = True
        return r1

    def save_statement(self, statement, accnm, journal, datestart, dateend, amount):
        """ create statement
            statement = statement lines
            accnm = bank account number
            journal = statement journal
            dateend = end date of statement
            amount = balance amount from bank
        """
        pool = Pool()
        AccountStatement = pool.get('account.statement')
        AccStatLines = pool.get('account.statement.line')
        Party = pool.get('party.party')
        Address = pool.get('party.address')
        Invoice = pool.get('account.invoice')
        tab_invoice = Invoice.__table__()
        cursor = Transaction().connection.cursor()
        
        self.checkresult.doubleline = 0
        self.checkresult.newlines = 0
        self.checkresult.banknew = 0
        self.checkresult.bankaccnew = 0
        recalc_start_balance = True
        st_obj = AccountStatement()
        
        # defaults
        d1 = AccountStatement.default_get(AccountStatement._fields.keys())
        for i in d1.keys():
            setattr(st_obj, i, d1[i])

        # create name
        statmt_lst = AccountStatement.search([
                ('company', '=', journal.company),
                ('journal', '=', journal),
            ], order=[('date', 'DESC'), ('id', 'DESC')])
        st_obj.name = '%d-%03d %s' % \
            (dateend.year, len(statmt_lst) + 1, accnm.fints_name)

        st_obj.company = journal.company
        st_obj.journal = journal
        st_obj.start_balance = None
        st_obj.on_change_journal()
        
        # start/end date
        st_obj.start_date = datestart
        st_obj.end_date = dateend

        if st_obj.start_balance:
            # start-balance was set by 'on_change_journal'
            recalc_start_balance = False
        else :
            # set to '0' to allow saving
            st_obj.start_balance = Decimal('0.0')

        st_obj.date = dateend
        # end-balance was provided by the bank
        st_obj.end_balance = amount
        st_obj.save()
        
        st_obj.lines = []
        cnt1 = 1
        for i in statement:
            
            stm_date = i.data.get('entry_date', i.data.get('date', None))
            stm_amount = i.data.get('amount').amount
            remote_name = i.data.get('applicant_name', None)
            if isinstance(remote_name, type(None)):
                remote_name = i.data.get('id', '-/-')
            stm_description = '%s: %s' % (
                    remote_name,
                    i.data.get('purpose', i.data.get('transaction_details', '-/-'))
                )
            if not isinstance(stm_description, type(None)):
                stm_description = stm_description.replace('\n', ' ')
            stm_data = self.get_fints_data(i.data)
            stm_hash = hashlib.sha224(stm_data.encode()).hexdigest()

            if self.enterdata.skipknownlines == True:
                # check if we already have this line
                dbl_line = AccStatLines.search([
                        ('statement.journal.id', '=', journal.id),
                        ('date', '=', stm_date),
                        ('amount', '=', stm_amount),
                        ('fints_hash', '=', stm_hash),
                    ])
                if len(dbl_line) > 0:
                    # skip this line
                    self.checkresult.doubleline += 1
                    continue

            stm_obj = AccStatLines()
            stm_obj.number = str(cnt1)
            cnt1 += 1
            stm_obj.date = stm_date
            stm_obj.amount = stm_amount
            stm_obj.description = stm_description
            stm_obj.fints_data = stm_data
            stm_obj.fints_hash = stm_hash

            # find invoice to set party/account/invoice automatically
            inv_lst = []
            if self.enterdata.linkinvoice == True:
                qu1 = tab_invoice.select(tab_invoice.id,
                        where=(tab_invoice.state == 'posted') & 
                            (tab_invoice.company == journal.company.id) &
                            (
                                # search for invoice-number somewhere in 'purpose', eg. '2017-0001'
                                # find it even if the payer wrote '20170001'
                                (Position(tab_invoice.number, Lower(i.data.get('purpose', ''))) != 0) |
                                (Position(Replace(tab_invoice.number, '-', ''), Lower(i.data.get('purpose', ''))) != 0)
                            )
                    )
                cursor.execute(*qu1)
                l1 = cursor.fetchall()
                if len(l1) > 0:
                    # double check: amount must match
                    inv_lst = Invoice.search([
                                    ('id', 'in', l1),
                                    ('total_amount', '=', stm_obj.amount), 
                                ])

            # ignore result if not exact match
            if len(inv_lst) == 1:
                stm_obj.invoice = inv_lst[0]
                stm_obj.on_change_invoice()     # connect: account + party
            else :
                # invoice not found/exact match
                # try to find a valid party: i.data.applicant_name == party.name
                # bank internal payments are without 'applicant_name'
                use_party = i.data.get('applicant_name', None)
                if isinstance(use_party, type(None)):
                    use_party = 'SEPA-party-noname'
                p_lst = Party.search([
                        ('name', '=', use_party),
                        ('active', '=', True)
                    ])
                if len(p_lst) == 0:
                    # create this party
                    p_obj = Party()
                    p_obj.name = use_party
                    p_obj.addresses = [Address()]
                    p_obj.save()
                    stm_obj.party = p_obj
                    stm_obj.on_change_party()
                elif len(p_lst) > 0:
                    # use first match
                    stm_obj.party = p_lst[0]
                    stm_obj.on_change_party()

                # assign category to payer/payee-party
                if not isinstance(journal.fints_payercategory, type(None)):
                    cat1 = list(stm_obj.party.categories)
                    if not journal.fints_payercategory in cat1:
                        cat1.append(journal.fints_payercategory)
                        stm_obj.party.categories = cat1
                        stm_obj.party.save()

            if journal.fints_createbankaccounts == True:
                # bank account for payer/payee
                self.create_bank_account(stm_obj.party, i.data, journal)
            
            st_lines = list(st_obj.lines)
            st_lines.append(stm_obj)
            st_obj.lines = st_lines
            self.checkresult.newlines += 1
        st_obj.on_change_lines()
        
        if recalc_start_balance == True:
            st_bal = st_obj.end_balance
            for i in st_obj.lines:
                st_bal += -i.amount
            st_obj.start_balance = st_bal

        st_obj.save()
        
        # delete statement if we have no new lines
        if len(st_obj.lines) == 0:
            AccountStatement.delete([st_obj])
            return 0
        else :
            # store new statement for list view
            l1 = list(self.enterdata.statements)
            l1.append(st_obj)
            self.enterdata.statements = l1
            
            return len(st_obj.lines)

    def create_bank_from_bic(self, bic, category):
        """ create bank + party from bic
            TODO: import bank-data from predefined table/online
        """
        pool = Pool()
        Address = pool.get('party.address')
        Party = pool.get('party.party')
        Bank = pool.get('bank')

        bank_party = Party()
        bank_party.name = 'Bank (BIC: %s)' % bic
        bank_party.addresses = [Address()]
        if not isinstance(category, type(None)):
            bank_party.categories = [category]
        bank_party.save()
        bank_obj = Bank()
        bank_obj.party = bank_party
        bank_obj.bic = bic
        bank_obj.save()
        return bank_obj
        
    def create_bank_account(self, party, fdata, journal):
        """ create bank account for party from SEPA-infos
        """
        pool = Pool()
        Bank = pool.get('bank')
        BankAccount = pool.get('bank.account')
        BankAccountNumber = pool.get('bank.account.number')
        ModelData = pool.get('ir.model.data')
        context = Transaction().context

        # we need to have permission 'bank administration'
        if not ModelData.get_id('bank', 'group_bank_admin') in context.get('groups', []):
            return
        
        iban = fdata.get('applicant_iban', '-')
        bic = fdata.get('applicant_bin', '-')

        if (iban != '-') and (iban != None):
            ban_lst = BankAccountNumber.search([
                    ('account.owners.id', '=', party.id),
                    ('number_compact', '=', iban)
                ])
            if len(ban_lst) == 0:
                
                bank_lst = Bank.search([('bic', '=', bic)])
                if len(bank_lst) > 0:
                    bank_obj = bank_lst[0]
                    
                    # assign category to bank-party
                    if not isinstance(journal.fints_bankcategory, type(None)):
                        cat1 = list(bank_obj.party.categories)
                        if not journal.fints_bankcategory in cat1:
                            cat1.append(journal.fints_bankcategory)
                            bank_obj.party.categories = cat1
                            bank_obj.party.save()
                else :
                    bank_obj = self.create_bank_from_bic(bic, journal.fints_bankcategory)
                    self.checkresult.banknew += 1

                bnum_obj = BankAccountNumber()
                bnum_obj.type = 'iban'
                bnum_obj.number = iban
                
                bacc_obj = BankAccount()
                bacc_obj.bank = bank_obj
                bacc_obj.owners = [party]
                bacc_obj.currency = journal.currency
                bacc_obj.active = True
                bacc_obj.numbers = [bnum_obj]
                bacc_obj.save()
                self.checkresult.bankaccnew += 1
        
    def get_fints_data(self, fdata):
        """ store data from bank
        """
        r1 = {}
        r1.update(fdata)
        for i in r1.keys():
            if isinstance(r1[i], type(date(2010, 1, 1))):
                r1[i] = r1[i].strftime('%Y-%m-%d')
            elif isinstance(r1[i], type(mt940.models.Amount('0.0', 'C', 'EUR'))):
                r1[i] = {'amount': '%.2f' % r1[i].amount, 'currency': r1[i].currency}
        return json.dumps(r1, sort_keys=True, indent=2, separators=(',', ': '))

    def end(self):
        return 'reload'

# end ImportByFinTSWizard
