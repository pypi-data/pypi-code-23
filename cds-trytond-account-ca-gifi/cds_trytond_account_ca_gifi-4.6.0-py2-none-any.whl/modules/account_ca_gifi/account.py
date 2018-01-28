# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
from sql.operators import Concat
from sql.functions import Position

from trytond.pool import Pool, PoolMeta
from trytond.transaction import Transaction

__all__ = ['AccountTemplate']


class AccountTemplate:
    __metaclass__ = PoolMeta
    __name__ = 'account.account.template'

    @classmethod
    def __register__(cls, module_name):
        pool = Pool()
        ModelData = pool.get('ir.model.data')
        cursor = Transaction().connection.cursor()
        model_data = ModelData.__table__()

        # FOR FUTURE VERSIONS: translation of the account chart
        # put any migrations here (to add French later for example)

        super(AccountTemplate, cls).__register__(module_name)
