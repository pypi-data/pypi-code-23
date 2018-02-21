# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2016 Edgewall Software
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

from trac.admin import IAdminPanelProvider
from trac.core import Component, ExtensionPoint, implements
from trac.util.html import tag
from trac.util.translation import tag_
from trac.web.chrome import add_stylesheet, add_warning

from tracspamfilter.api import _
from tracspamfilter.captcha import ICaptchaMethod
from tracspamfilter.captcha.expression import ExpressionCaptcha
from tracspamfilter.captcha.keycaptcha import KeycaptchaCaptcha
from tracspamfilter.captcha.recaptcha2 import Recaptcha2Captcha

try:
    from tracspamfilter.captcha.image import ImageCaptcha
except ImportError:  # PIL not installed
    ImageCaptcha = None


class CaptchaAdminPageProvider(Component):
    """Web administration panel for configuring the Captcha handling."""

    implements(IAdminPanelProvider)

    handlers = ExtensionPoint(ICaptchaMethod)

    def __init__(self):
        self.recaptcha_enabled = \
            self.env.is_enabled(Recaptcha2Captcha)
        self.keycaptcha_enabled =\
            self.env.is_enabled(KeycaptchaCaptcha)
        self.expressioncaptcha_enabled = \
            self.env.is_enabled(ExpressionCaptcha)
        self.imagecaptcha_enabled = \
            ImageCaptcha and self.env.is_enabled(ImageCaptcha)

    # IAdminPanelProvider methods

    def get_admin_panels(self, req):
        any_captchas_enabled = \
            any((self.recaptcha_enabled, self.keycaptcha_enabled,
                 self.expressioncaptcha_enabled, self.imagecaptcha_enabled))
        if 'SPAM_CONFIG' in req.perm and any_captchas_enabled:
            yield 'spamfilter', _("Spam Filtering"), 'captcha', _("Captcha")

    def render_admin_panel(self, req, cat, page, path_info):
        req.perm.require('SPAM_CONFIG')

        spam_config = self.config['spam-filter']
        data = {}

        if req.method == 'POST':
            if 'cancel' in req.args:
                req.redirect(req.href.admin(cat, page))

            captcha_enabled = 'captcha_enabled' in req.args
            captcha = req.args.get('captcha')

            captcha_karma_lifetime = req.args.as_int('captcha_karma_lifetime')
            if captcha_karma_lifetime is None:
                captcha_karma_lifetime = \
                    spam_config.get('captcha_karma_lifetime')
                add_warning(req,
                            tag_("Invalid value for %(key)s",
                                 key=tag.tt('captcha_karma_lifetime')))

            recaptcha_private_key = recaptcha_public_key = None
            if self.recaptcha_enabled:
                recaptcha_private_key = req.args.get('recaptcha_private_key')
                recaptcha_public_key = req.args.get('recaptcha_public_key')
                recaptcha = Recaptcha2Captcha(self.env)
                verified_key = recaptcha.verify_key(recaptcha_private_key,
                                                    recaptcha_public_key)
                if recaptcha_private_key and not verified_key:
                    data['recaptcha_error'] = _("The keys are invalid")
                    data['error'] = 1

            keycaptcha_private_key = keycaptcha_user_id = None
            if self.keycaptcha_enabled:
                keycaptcha_private_key = req.args.get('keycaptcha_private_key')
                keycaptcha_user_id = req.args.get('keycaptcha_user_id')
                keycaptcha = KeycaptchaCaptcha(self.env)
                verified_key = keycaptcha.verify_key(keycaptcha_private_key,
                                                     keycaptcha_user_id)
                if keycaptcha_private_key and not verified_key:
                    data['keycaptcha_error'] = \
                        _("The key or user id are invalid")
                    data['error'] = 1

            expressioncaptcha_ceiling = expressioncaptcha_terms = None
            if self.expressioncaptcha_enabled:
                expressioncaptcha_ceiling = \
                    req.args.as_int('expressioncaptcha_ceiling')
                if expressioncaptcha_ceiling is None:
                    expressioncaptcha_ceiling = \
                        spam_config.get('captcha_expression_ceiling')
                    add_warning(req,
                                tag_("Invalid value for %(key)s",
                                     key=tag.tt('captcha_expression_ceiling')))

                expressioncaptcha_terms = \
                    req.args.as_int('expressioncaptcha_terms')
                if expressioncaptcha_terms is None:
                    expressioncaptcha_terms = \
                        spam_config.get('captcha_expression_terms')
                    add_warning(req,
                                tag_("Invalid value for %(key)s",
                                     key=tag.tt('captcha_expression_terms')))

            imagecaptcha_alphabet = imagecaptcha_fonts = \
                imagecaptcha_letters = imagecaptcha_font_size = None
            if self.imagecaptcha_enabled:
                imagecaptcha_alphabet = req.args.get('imagecaptcha_alphabet')
                imagecaptcha_fonts = req.args.get('imagecaptcha_fonts')
                imagecaptcha_letters = req.args.as_int('imagecaptcha_letters')
                if imagecaptcha_letters is None:
                    imagecaptcha_letters = \
                        spam_config.get('captcha_image_letters')
                    add_warning(req,
                                tag_("Invalid value for %(key)s",
                                     key=tag.tt('captcha_image_letters')))

                imagecaptcha_font_size = \
                    req.args.as_int('imagecaptcha_font_size')
                if imagecaptcha_font_size is None:
                    imagecaptcha_font_size = \
                        spam_config.get('captcha_image_font_size')
                    add_warning(req,
                                tag_("Invalid value for %(key)s",
                                     key=tag.tt('captcha_image_font_size')))

            if 'error' not in data or not data['error']:
                spam_config.set('captcha', captcha)
                if captcha_enabled:
                    spam_config.set('reject_handler', 'CaptchaSystem')
                else:
                    spam_config.set('reject_handler', 'FilterSystem')

                spam_config.set('captcha_karma_lifetime',
                                captcha_karma_lifetime)

                if self.recaptcha_enabled:
                    spam_config.set('captcha_recaptcha_private_key',
                                    recaptcha_private_key)
                    spam_config.set('captcha_recaptcha_public_key',
                                    recaptcha_public_key)

                if self.keycaptcha_enabled:
                    spam_config.set('captcha_keycaptcha_private_key',
                                    keycaptcha_private_key)
                    spam_config.set('captcha_keycaptcha_user_id',
                                    keycaptcha_user_id)

                if self.expressioncaptcha_enabled:
                    spam_config.set('captcha_expression_ceiling',
                                    expressioncaptcha_ceiling)
                    spam_config.set('captcha_expression_terms',
                                    expressioncaptcha_terms)

                if self.imagecaptcha_enabled:
                    spam_config.set('captcha_image_alphabet',
                                    imagecaptcha_alphabet)
                    spam_config.set('captcha_image_letters',
                                    imagecaptcha_letters)
                    spam_config.set('captcha_image_font_size',
                                    imagecaptcha_font_size)
                    spam_config.set('captcha_image_fonts',
                                    imagecaptcha_fonts)

                self.config.save()
                req.redirect(req.href.admin(cat, page))

        else:
            captcha = spam_config.get('captcha')
            reject_handler = spam_config.get('reject_handler')
            captcha_enabled = reject_handler == 'CaptchaSystem'
            captcha_karma_lifetime = spam_config.get('captcha_karma_lifetime')

            recaptcha_private_key = \
                spam_config.get('captcha_recaptcha_private_key')
            recaptcha_public_key = \
                spam_config.get('captcha_recaptcha_public_key')

            keycaptcha_private_key = \
                spam_config.get('captcha_keycaptcha_private_key')
            keycaptcha_user_id = \
                spam_config.get('captcha_keycaptcha_user_id')

            expressioncaptcha_ceiling = \
                spam_config.get('captcha_expression_ceiling')
            expressioncaptcha_terms = \
                spam_config.get('captcha_expression_terms')

            imagecaptcha_alphabet = \
                spam_config.get('captcha_image_alphabet')
            imagecaptcha_letters = \
                spam_config.get('captcha_image_letters')
            imagecaptcha_font_size = \
                spam_config.get('captcha_image_font_size')
            imagecaptcha_fonts = \
                spam_config.get('captcha_image_fonts')

        captcha_types = sorted(h.__class__.__name__ for h in self.handlers)

        data.update({
            'captcha': captcha,
            'captcha_types': captcha_types,
            'captcha_enabled': captcha_enabled,
            'captcha_karma_lifetime': captcha_karma_lifetime,
            'recaptcha_enabled': self.recaptcha_enabled,
            'recaptcha_private_key': recaptcha_private_key,
            'recaptcha_public_key': recaptcha_public_key,
            'keycaptcha_enabled': self.keycaptcha_enabled,
            'keycaptcha_private_key': keycaptcha_private_key,
            'keycaptcha_user_id': keycaptcha_user_id,
            'expressioncaptcha_enabled': self.expressioncaptcha_enabled,
            'expressioncaptcha_ceiling': expressioncaptcha_ceiling,
            'expressioncaptcha_terms': expressioncaptcha_terms,
            'imagecaptcha_enabled': self.imagecaptcha_enabled,
            'imagecaptcha_alphabet': imagecaptcha_alphabet,
            'imagecaptcha_letters': imagecaptcha_letters,
            'imagecaptcha_font_size': imagecaptcha_font_size,
            'imagecaptcha_fonts': imagecaptcha_fonts
        })

        add_stylesheet(req, 'spamfilter/admin.css')
        return 'admin_captcha.html', data
