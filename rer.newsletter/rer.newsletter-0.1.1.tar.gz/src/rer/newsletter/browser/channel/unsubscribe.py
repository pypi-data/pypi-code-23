# -*- coding: utf-8 -*-

from plone import api
from plone import schema
from plone.protect.authenticator import createToken
from plone.z3cform.layout import wrap_form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from rer.newsletter import _
from rer.newsletter import logger
from rer.newsletter.utility.channel import IChannelUtility
from rer.newsletter.utility.channel import OK
from rer.newsletter.utility.channel import UNHANDLED
from z3c.form import button
from z3c.form import field
from z3c.form import form
from zope.component import getUtility
from zope.interface import Interface


class IUnsubscribeForm(Interface):
    """ define field for channel unsubscription """
    email = schema.Email(
        title=_(u'unsubscribe_email_title', default=u'Unsubscription Email'),
        description=_(
            u'unsubscribe_email_description',
            default=u''
        ),
        required=True,
    )


class UnsubscribeForm(form.Form):

    ignoreContext = True
    fields = field.Fields(IUnsubscribeForm)

    def isVisible(self):
        if self.context.is_subscribable:
            return True
        else:
            return False

    def getChannelPrivacyPolicy(self):
        return False

    def updateWidgets(self):
        super(UnsubscribeForm, self).updateWidgets()
        if self.request.get('email', None):
            self.widgets['email'].value = self.request.get('email')

    @button.buttonAndHandler(_(u'unsubscribe_button', default='Unsubscribe'))
    def handleSave(self, action):
        status = UNHANDLED
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        if self.context.portal_type == 'Channel':
            channel = self.context.id_channel
        email = data.get('email', None)

        api_channel = getUtility(IChannelUtility)
        status, secret = api_channel.unsubscribe(channel, email)

        if status == OK:

            # creo il token CSRF
            token = createToken()

            # mando mail di conferma
            url = self.context.absolute_url()
            url += '/confirmaction?secret=' + secret
            url += '&_authenticator=' + token
            url += '&action=unsubscribe'

            mail_template = self.context.restrictedTraverse(
                '@@deleteuser_template'
            )

            parameters = {
                'header': self.context.header,
                'footer': self.context.footer,
                'style': self.context.css_style,
                'activationUrl': url
            }

            mail_text = mail_template(**parameters)

            portal = api.portal.get()
            mail_text = portal.portal_transforms.convertTo(
                'text/mail', mail_text)

            response_email = None
            if self.context.response_email:
                response_email = self.context.response_email
            else:
                response_email = u'noreply@rer.it'

            mailHost = api.portal.get_tool(name='MailHost')
            mailHost.send(
                mail_text.getData(),
                mto=email,
                mfrom=response_email,
                subject='Conferma la cancellazione dalla newsletter ' +
                self.context.title + ' del portale ' + api.portal.get().title,
                charset='utf-8',
                msg_type='text/html',
                immediate=True
            )

            api.portal.show_message(
                message=_(
                    u'user_unsubscribe_success',
                    default=u'Info Riceverai una e-mail per confermare'
                    ' la cancellazione dalla newsletter'
                ),
                request=self.request,
                type=u'info'
            )
        else:
            logger.exception(
                'unhandled error unsubscribe user'
            )
            api.portal.show_message(
                message=u'Problems...{0}'.format(status),
                request=self.request,
                type=u'error'
            )


unsubscribe_view = wrap_form(
    UnsubscribeForm,
    index=ViewPageTemplateFile('templates/unsubscribechannel.pt')
)
