# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
from trytond.pool import Pool
from .bank import Bank, BankAccountNumber, BankAccount
from .wiz_checkaccess import CheckBankAccessWizard, EnterPINView, CheckResult
from .wiz_import import ImportByFinTSWizard, SelectAccounts, EnterImportData, CheckImportResult
from .statement import Statement, AccountStatementLine
from .journal import Journal
from .fix_mt940 import *


def register():
    Pool.register(
        Journal,
        Bank,
        BankAccount,
        BankAccountNumber,
        EnterPINView,
        CheckResult,
        SelectAccounts,
        EnterImportData,
        CheckImportResult,
        Statement,
        AccountStatementLine,
        module='account_statement_fints', type_='model')
    Pool.register(
        CheckBankAccessWizard,
        ImportByFinTSWizard,
        module='account_statement_fints', type_='wizard')

