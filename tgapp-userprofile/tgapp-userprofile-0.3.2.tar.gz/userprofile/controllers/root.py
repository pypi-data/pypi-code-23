# -*- coding: utf-8 -*-
"""Main Controller"""
from datetime import datetime

from resetpassword.lib import generate_token
from tg import TGController, expose, flash, require, predicates, \
    request, redirect, config, override_template, abort
from tg.i18n import ugettext as _, lazy_ugettext as l_
from tg.predicates import not_anonymous
from tg.util import Bunch
from tgext.pluggable import plug_url
from tw2.core import ValidationError

from userprofile import model
from userprofile.lib import create_user_form, get_user_data, get_profile_css, \
                            update_user_data, send_email


class RootController(TGController):
    @expose('userprofile.templates.index')
    @require(predicates.not_anonymous())
    def index(self):
        user = request.identity['user']
        user_data, user_avatar = get_user_data(user)
        user_displayname = user_data.pop('display_name', (None, 'Unknown'))
        user_partial = config['_pluggable_userprofile_config'].get('user_partial')
        return dict(user=user.profile_data,
                    user_data=user_data,
                    user_avatar=user_avatar,
                    user_displayname=user_displayname,
                    profile_css=get_profile_css(config),
                    user_partial=user_partial)

    @expose('userprofile.templates.edit')
    @require(predicates.not_anonymous())
    def edit(self):
        user = request.identity['user']
        user_data, user_avatar = get_user_data(user)
        user_data = Bunch(((fieldid, info[1]) for fieldid, info in user_data.items()))
        return dict(user=user, profile_css=get_profile_css(config),
                    user_avatar=user_avatar,
                    form=create_user_form(user))

    @expose()
    @require(predicates.not_anonymous())
    def save(self, **kw):
        kw.pop('nothing')
        flash_message = _('Profile successfully updated')
        user = request.identity['user']

        # validate the form
        try:
            form = create_user_form(user)
            kw = form.validate(kw)
        except ValidationError:
            override_template(self.save, 'kajiki:userprofile.templates.edit')
            user_data, user_avatar = get_user_data(user)
            return dict(user={},
                        profile_css=get_profile_css(config),
                        user_avatar=user_avatar,
                        form=form)

        # get the profile_save function that may be custom
        profile_save = getattr(user, 'save_profile', None)
        if not profile_save:
            profile_save = update_user_data

        # do not change the password if the user did't set it

        if 'password' in kw:
            if not kw.get('password'):  # keep old email
                kw.pop('password')
                kw.pop('verify_password')
            else:  # set new email
                kw.pop('verify_password')

        # we don't want to save the email until it is confirmed
        new_email = kw['email_address']
        kw['email_address'] = user.email_address
        profile_save(user, kw)

        if new_email != user.email_address:
            # save this new email in the db
            dictionary = {
                'email_address': new_email,
                'activation_code':
                    model.ProfileActivation.generate_activation_code(new_email),
            }
            activation = model.provider.create(model.ProfileActivation, dictionary)

            # ok, send the email please
            userprofile_config = config.get('_pluggable_userprofile_config')
            mail_body = userprofile_config.get(
                'mail_body',
                _('Please click on this link to confermate your email address')
                + '\n\n' + activation.activation_link,
            )
            email_data = {'sender': config['userprofile.email_sender'],
                          'subject': userprofile_config.get(
                              'mail_subject', _('Please confirm your email')),
                          'body': mail_body,
                          'rich': userprofile_config.get('mail_rich', '')}
            send_email(new_email, **email_data)
            flash_message += '.\n' + _('Confirm your email please')

        flash(flash_message)
        return redirect(plug_url('userprofile', '/'))

    @expose()
    def activate(self, activation_code, **kw):
        activation = model.ProfileActivation.by_code(activation_code) or abort(404)
        user = model.User.find({'email_address': activation.email_address}).first()
        user.email_address = activation.email_address
        activation.activated = datetime.utcnow()
        flash(_('email correctely updated'))
        return redirect(plug_url('userprofile', '/'))

    @expose()
    @require(not_anonymous(msg=l_("User must be authenticated")))
    def reset_password(self, redirect_to='/'):
        user = request.identity['user']
        token = generate_token(user, redirect_to=redirect_to)
        return redirect(plug_url('resetpassword', '/change_password/', params=dict(data=token)))
