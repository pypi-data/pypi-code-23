# -*- coding: utf-8 -*-
#
# Copyright (C) 2012 Dirk Stöcker <trac@dstoecker.de>
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution. The terms
# are also available at http://trac.edgewall.com/license.html.
#
# This software consists of voluntary contributions made by many
# individuals. For the exact contribution history, see the revision
# history and logs, available at http://projects.edgewall.com/trac/.

from genshi.filters.transform import Transformer
from trac.config import IntOption, Option
from trac.core import Component, implements
from trac.util.html import tag
from trac.util.text import javascript_quote, shorten_line
from trac.web.api import ITemplateStreamFilter

from tracspamfilter.api import IFilterStrategy, N_


class TrapFieldFilterStrategy(Component):
    """Spam filter using a hidden trap field.
    """
    implements(IFilterStrategy, ITemplateStreamFilter)

    karma_points = IntOption('spam-filter', 'trap_karma', '10',
        """By how many points a trap reject impacts the overall karma of
        a submission.""", doc_domain='tracspamfilter')

    name = Option('spam-filter', 'trap_name', 'sfp_email',
        """Name of the invisible trap field, should contain some reference
        to e-mail for better results.""", doc_domain='tracspamfilter')

    name_hidden = Option('spam-filter', 'trap_name_hidden', 'sfph_mail',
        """Name of the hidden trap field, should contain some reference
        to e-mail for better results.""", doc_domain='tracspamfilter')

    name_register = Option('spam-filter', 'trap_name_register', 'spf_homepage',
        """Name of the register trap field, should contain some reference
        to web/homepage for better results.""", doc_domain='tracspamfilter')

    # IFilterStrategy implementation

    def is_external(self):
        return False

    def get_trap(self, req):
        i = req.args.getfirst(self.name)
        h = req.args.getfirst(self.name_hidden)
        if i and h and i != h:
            return i + "\n" + h
        elif h:
            return h
        return i

    def test(self, req, author, content, ip):
        i = req.args.getfirst(self.name)
        h = req.args.getfirst(self.name_hidden)
        r = self.getlink(req)

        if i and h:
            i = shorten_line(javascript_quote(i), 50)
            h = shorten_line(javascript_quote(h), 50)
            return -abs(self.karma_points), \
                   N_("Both trap fields says this is spam (%s, %s)"), i, h
        elif i:
            i = shorten_line(javascript_quote(i), 50)
            return -abs(self.karma_points), \
                   N_("Invisible trap field says this is spam (%s)"), i
        elif h:
            h = shorten_line(javascript_quote(h), 50)
            return -abs(self.karma_points), \
                   N_("Hidden trap field says this is spam (%s)"), h
        elif r:
            r = shorten_line(javascript_quote(r), 50)
            return -abs(self.karma_points), \
                   N_("Register trap field starts with HTTP URL (%s)"), r

    def getlink(self, req):
        r = req.args.getfirst(self.name_register)
        if not (r and (r.startswith('http://') or r.startswith('https://'))):
            return None
        return r

    def train(self, req, author, content, ip, spam=True):
        return 0

    # ITemplateStreamFilter interface
    def filter_stream(self, req, method, filename, stream, data):
        if self.karma_points > 0:
            # Insert the hidden field right before the submit buttons
            trap = tag.div(style='display:none;')(
                    tag.input(type='text', name=self.name, value=''),
                    tag.input(type='hidden', name=self.name_hidden, value=''))
            stream = stream | \
                     Transformer('//div[@class="buttons"]').before(trap)
        return stream
