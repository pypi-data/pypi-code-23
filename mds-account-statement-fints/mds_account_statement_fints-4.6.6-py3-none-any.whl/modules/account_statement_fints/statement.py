# -*- coding: utf-8 -*-
# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.model import Workflow, ModelView, ModelSQL, fields, Unique
from trytond.pool import Pool, PoolMeta
from trytond.modules.account_statement.statement import _STATES, _DEPENDS
import hashlib, logging
from trytond.transaction import Transaction

__all__ = ['Statement','AccountStatementLine']
__metaclass__ = PoolMeta

logger = logging.getLogger(__name__)


class Statement(Workflow, ModelSQL, ModelView):
    'Account Statement'
    __name__ = 'account.statement'

    start_date = fields.Date(string=u'Start Date', states=_STATES, depends=_DEPENDS, 
                    help=u'final opening balance provided by your bank')
    end_date = fields.Date(string=u'End Date', states=_STATES, depends=_DEPENDS,
                    help=u'final closing balance provided by your bank')

# Statement


class AccountStatementLine(ModelSQL, ModelView):
    'Account Statement Line'
    __name__ = 'account.statement.line'

    fints_data = fields.Text(string=u'SEPA-Data', readonly=True)
    fints_hash = fields.Char(string=u'Hash', readonly=True, select=True)

    @classmethod
    def __register__(cls, module_name):
        super(AccountStatementLine, cls).__register__(module_name)
        cls.migrate_fints_hash()

    @classmethod
    def migrate_fints_hash(cls):
        """ add hash for fints_data
            migration 4.6.0 --> 4.6.1
        """
        AccStmLine = Pool().get('account.statement.line')
        cursor = Transaction().connection.cursor()
        tab_accstmline = AccStmLine.__table__()

        qu1 = tab_accstmline.select(tab_accstmline.id, 
                tab_accstmline.fints_data,
                where=(tab_accstmline.fints_data != '') &
                    (tab_accstmline.fints_data != None) &
                    (tab_accstmline.fints_hash == None)
            )
        cursor.execute(*qu1)
        l1 = cursor.fetchall()
        
        if len(l1) > 0:
            logger.info(u'migrate_fints_hash: %d items to update' % len(l1))

        for i in l1:
            (id1, data1) = i
            
            qu2 = tab_accstmline.update(
                    columns=[tab_accstmline.fints_hash],
                    values=[hashlib.sha224(data1.encode()).hexdigest()],
                    where=(tab_accstmline.id == id1)
                )
            cursor.execute(*qu2)

# end AccountStatementLine
