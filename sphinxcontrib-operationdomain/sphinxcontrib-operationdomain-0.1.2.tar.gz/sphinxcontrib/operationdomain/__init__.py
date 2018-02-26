# -*- coding: utf-8 -*-
"""
    sphinxcontrib.operationdomain
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This package is a namespace package that contains all extensions
    distributed in the ``sphinx-contrib`` distribution.

    :copyright: Copyright 2007-2018 by the Sphinx team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

__import__('pkg_resources').declare_namespace(__name__)

from sphinxcontrib.operationdomain.core import OperationDomain

def setup(app):
    app.add_domain(OperationDomain)
