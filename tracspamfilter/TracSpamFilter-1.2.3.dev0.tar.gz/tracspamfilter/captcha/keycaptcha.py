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

import hashlib
import random
import urllib2

from trac.config import Option
from trac.core import Component, implements
from trac.util.html import tag

from tracspamfilter.api import user_agent
from tracspamfilter.captcha import ICaptchaMethod


class KeycaptchaCaptcha(Component):
    """KeyCaptcha implementation"""

    implements(ICaptchaMethod)

    private_key = Option('spam-filter', 'captcha_keycaptcha_private_key', '',
        """Private key for KeyCaptcha usage.""", doc_domain="tracspamfilter")

    user_id = Option('spam-filter', 'captcha_keycaptcha_user_id', '',
        """User id for KeyCaptcha usage.""", doc_domain="tracspamfilter")

    def generate_captcha(self, req):
        session_id = "%d-3.4.0.001" % random.randint(1, 10000000)
        sign1 = hashlib.md5(session_id + req.remote_addr +
                            self.private_key).hexdigest()
        sign2 = hashlib.md5(session_id + self.private_key).hexdigest()
        varblock = "var s_s_c_user_id = '%s';\n" % self.user_id
        varblock += "var s_s_c_session_id = '%s';\n" % session_id
        varblock += "var s_s_c_captcha_field_id = 'keycaptcha_response_field';\n"
        varblock += "var s_s_c_submit_button_id = 'keycaptcha_response_button';\n"
        varblock += "var s_s_c_web_server_sign = '%s';\n" % sign1
        varblock += "var s_s_c_web_server_sign2 = '%s';\n" % sign2
        varblock += "document.s_s_c_debugmode=1;\n"
        fragment = tag(tag.script(varblock, type='text/javascript'))

        fragment.append(
            tag.script(type='text/javascript',
                       src='http://backs.keycaptcha.com/swfs/cap.js')
        )

        fragment.append(
            tag.input(type='hidden', id='keycaptcha_response_field',
                      name='keycaptcha_response_field')
        )

        fragment.append(
            tag.input(type='submit', id='keycaptcha_response_button',
                      name='keycaptcha_response_button')
        )

        req.session['captcha_key_session'] = session_id

        return None, fragment

    def verify_key(self, private_key, user_id):
        if private_key is None or user_id is None:
            return False
        # FIXME - Not yet implemented
        return True

    def verify_captcha(self, req):
        session = None
        if 'captcha_key_session' in req.session:
            session = req.session['captcha_key_session']
            del req.session['captcha_key_session']

        response_field = req.args.get('keycaptcha_response_field')
        val = response_field.split('|')
        s = hashlib.md5('accept' + val[1] + self.private_key +
                        val[2]).hexdigest()
        self.log.debug("KeyCaptcha response: %s .. %s .. %s",
                       response_field, s, session)
        if s == val[0] and session == val[3]:
            try:
                request = urllib2.Request(
                    url=val[2],
                    headers={"User-agent": user_agent}
                )

                response = urllib2.urlopen(request)
                return_values = response.read()
                response.close()
            except Exception, e:
                self.log.warning("Exception in KeyCaptcha handling (%s)", e)
            else:
                self.log.debug("KeyCaptcha check result: %s", return_values)
                if return_values == '1':
                    return True
                self.log.warning("KeyCaptcha returned invalid check result: "
                                 "%s (%s)", return_values, response_field)
        else:
            self.log.warning("KeyCaptcha returned invalid data: "
                             "%s (%s,%s)", response_field, s, session)
        return False

    def is_usable(self, req):
        return self.private_key and self.user_id
