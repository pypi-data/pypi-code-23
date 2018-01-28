# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

try:
    from trytond.modules.account_ca_gifi.tests.test_account_ca_gifi import (
        suite
    )
except ImportError:
    from .test_account_ca_gifi import suite

__all__ = ['suite']
