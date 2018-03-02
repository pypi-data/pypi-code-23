# -*- coding: utf-8 -*-
from plone import api
from plone import schema
from rer.newsletter import _
from rer.newsletter import logger
from rer.newsletter.utility.channel import IChannelUtility
from rer.newsletter.utility.channel import SUBSCRIBED
from rer.newsletter.utility.channel import UNHANDLED
from z3c.form import button
from z3c.form import field
from z3c.form import form
from zope.component import getUtility
from zope.interface import Interface


class IAddForm(Interface):
    """ define field for add user to a channel """
    email = schema.Email(
        title=_(u'add_user_admin', default=u'Add User'),
        description=_(
            u'add_user_admin_description',
            default=u'Insert email for add user to a Channel'
        ),
        required=True,
    )


class AddForm(form.Form):

    ignoreContext = True
    fields = field.Fields(IAddForm)

    @button.buttonAndHandler(_(u'add_user_admin_button', default=u'Add'))
    def handleSave(self, action):
        status = UNHANDLED
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        channel = self.context.id_channel
        mail = data['email']

        api_channel = getUtility(IChannelUtility)
        status = api_channel.addUser(channel, mail)

        if status == SUBSCRIBED:
            status = _(
                u'generic_add_message_success',
                default=u'User Added.'
            )
            api.portal.show_message(
                message=status,
                request=self.request,
                type=u'info'
            )
        else:
            logger.exception(
                'unhandled error add user'
            )
            api.portal.show_message(
                message=u'Problems...{0}'.format(status),
                request=self.request,
                type=u'error'
            )
