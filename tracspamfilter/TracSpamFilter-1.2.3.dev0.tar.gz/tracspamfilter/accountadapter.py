# -*- coding: utf-8 -*-
#
# Copyright (C) 2006 Edgewall Software
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution. The terms
# are also available at http://trac.edgewall.com/license.html.
#
# This software consists of voluntary contributions made by many
# individuals. For the exact contribution history, see the revision
# history and logs, available at http://projects.edgewall.com/trac/.

from acct_mgr.register import IAccountRegistrationInspector
from trac.core import Component, implements
from trac.util.html import tag
from trac.util.translation import cleandoc_

from tracspamfilter.api import _
from tracspamfilter.filters.trapfield import TrapFieldFilterStrategy
from tracspamfilter.filtersystem import FilterSystem
try:
    from tracspamfilter.filters.registration import RegistrationFilterStrategy
except ImportError:
    RegistrationFilterStrategy = None


class RegistrationFilterAdapter(Component):
    """Interface of spamfilter to account manager plugin to check new account
    registrations for spam."""

    _domain = 'tracspamfilter'
    _description = cleandoc_(
    """Interface of spamfilter to account manager plugin to check new account
    registrations for spam.

    It provides an additional 'Details' input field to get more information
    for calculating the probability of a spam registration attempt.
    Knowledge gained from inspecting registration attempts is shared with all
    other spam filter adapters for this system.
    """)
    implements(IAccountRegistrationInspector)

    # IAccountRegistrationInspector methods

    def render_registration_fields(self, req, data):
        insert = tag.div(tag.label(_("Details:"), tag.input(type="text",
                     name=TrapFieldFilterStrategy(self.env).name_register, size=60, class_="textwidget")))

        if RegistrationFilterStrategy:
            return RegistrationFilterStrategy(self.env).render_registration_fields(req, data, dict(optional=insert))
        else:
            return dict(optional=insert), data

    def validate_registration(self, req):
        # Add the author/reporter name
        if req.authname and req.authname != 'anonymous':
            author = req.authname
        else:
            author = req.args.get('username', req.authname)
        email = req.args.get('email')
        if email:
            author += " <%s>" % email

        changes = []
        sentinel = req.args.get('sentinel')
        if sentinel:
            changes += [(None, sentinel)]
        name = req.args.get('name')
        if name:
            changes += [(None, name)]
        comment = req.args.get(TrapFieldFilterStrategy(self.env).name_register)
        if comment:
            changes += [(None, comment)]

        FilterSystem(self.env).test(req, author, changes)
        return []
