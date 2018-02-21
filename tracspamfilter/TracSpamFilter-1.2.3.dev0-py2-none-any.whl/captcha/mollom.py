# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 Edgewall Software
# Copyright (C) 2015 Dirk Stöcker <trac@dstoecker.de>
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution. The terms
# are also available at http://trac.edgewall.com/license.html.
#
# This software consists of voluntary contributions made by many
# individuals. For the exact contribution history, see the revision
# history and logs, available at http://projects.edgewall.com/trac/.
#
# Author: Dirk Stöcker <trac@dstoecker.de>

import urllib2
from xml.etree import ElementTree

from trac.core import Component, implements
from trac.util.html import html

from tracspamfilter.captcha import ICaptchaMethod
from tracspamfilter.filters.mollom import MollomFilterStrategy


class MollomCaptcha(Component):
    """An image captcha server by http://www.mollom.com/"""

    implements(ICaptchaMethod)

    def __init__(self):
        self.mollom = MollomFilterStrategy(self.env)

    def generate_captcha(self, req):
        resp, content = self.mollom._call('captcha', {'type': 'image'})
        tree = ElementTree.fromstring(content)
        req.session['captcha_mollom_id'] = tree.find('./captcha/id').text
        url = tree.find('./captcha/url').text
        return '', html.img(src=url, alt='captcha')

    def verify_captcha(self, req):
        mollom_id = req.session.get('captcha_mollom_id')
        solution = req.args.get('captcha_response', '')
        try:
            resp, content = self.mollom._call('captcha/%s' % mollom_id,
                                              {'solution': solution})
        except Exception, e:
            self.log.warning("Exception in Mollom captcha handling (%s)", e)
            return False
        else:
            tree = ElementTree.fromstring(content)
            del req.session['captcha_mollom_id']
            if tree.find('./captcha/solved').text == '1':
                return True
            else:
                self.log.warning("Mollom captcha returned error: %s",
                                 tree.find('./message'))
        return False

    def is_usable(self, req):
        try:
            return self.mollom.verify_key(req)
        except urllib2.URLError:
            return False
