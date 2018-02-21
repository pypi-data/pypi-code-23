# -*- coding: utf-8 -*-
#
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

import json
import urllib
import urllib2

from trac.config import Option
from trac.core import Component, implements
from trac.util.html import tag
from trac.web.chrome import add_script

from tracspamfilter.api import _, user_agent
from tracspamfilter.captcha.api import ICaptchaMethod


class Recaptcha2Captcha(Component):
    """reCAPTCHA2 implementation"""

    implements(ICaptchaMethod)

    # use same values as reCAPTCHA1
    private_key = Option('spam-filter', 'captcha_recaptcha_private_key', '',
    """Private key for reCaptcha usage.""", doc_domain="tracspamfilter")

    public_key = Option('spam-filter', 'captcha_recaptcha_public_key', '',
        """Public key for reCaptcha usage.""", doc_domain="tracspamfilter")

    def generate_captcha(self, req):
        add_script(req, 'https://www.google.com/recaptcha/api.js')

        return None, tag(
            tag.div(class_='g-recaptcha', data_sitekey=self.public_key),
            tag.input(type='submit', value=_("Submit"))
        )

    def encode_if_necessary(self, s):
        if isinstance(s, unicode):
            return s.encode('utf-8')
        return s

    def verify_key(self, private_key, public_key):
        if private_key is None or public_key is None:
            return False
        # FIXME - Not yet implemented
        return True

    def verify_captcha(self, req):
        recaptcha_response_field = req.args.get('g-recaptcha-response')
        remoteip = req.remote_addr
        try:
            params = urllib.urlencode({
                'secret': self.encode_if_necessary(self.private_key),
                'remoteip': self.encode_if_necessary(remoteip),
                'response': self.encode_if_necessary(recaptcha_response_field),
            })
            request = urllib2.Request(
                url='https://www.google.com/recaptcha/api/siteverify',
                data=params,
                headers={
                    'Content-type': 'application/x-www-form-urlencoded',
                    'User-agent': user_agent
                }
            )

            response = urllib2.urlopen(request)
            return_values = json.loads(response.read())
            response.close()
        except Exception, e:
            self.log.warning("Exception in reCAPTCHA handling (%s)", e)
        else:
            if return_values['success'] is True:
                return True
            else:
                self.log.warning("reCAPTCHA returned error: %s",
                                 return_values['error-codes'])
        return False

    def is_usable(self, req):
        return self.public_key and self.private_key
