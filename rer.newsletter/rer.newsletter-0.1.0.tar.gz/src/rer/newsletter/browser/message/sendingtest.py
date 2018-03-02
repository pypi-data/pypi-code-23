# -*- coding: utf-8 -*-
# from rer.newsletter import logger
from plone import api
from plone import schema
from plone.z3cform.layout import wrap_form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from rer.newsletter import _
from rer.newsletter.content.channel import Channel
from smtplib import SMTPRecipientsRefused
from z3c.form import button
from z3c.form import field
from z3c.form import form
from zope.interface import Interface

import re


class IMessageSendingTest(Interface):
    """define field for sending test of message"""

    email = schema.Email(
        title=_(u'Email', default='Email'),
        description=_(
            u'email_sendingtest_description',
            default=u'Email to send the test message'
        ),
        required=True,
    )


class MessageSendingTest(form.Form):

    ignoreContext = True
    fields = field.Fields(IMessageSendingTest)

    @button.buttonAndHandler(_('send_sendingtest', default='Send'))
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        try:

            # prendo l'email dai parametri
            emails = []
            email = data['email']
            emails = re.compile('[,|;]').split(email)

            ns_obj = None
            for obj in self.context.aq_chain:
                if isinstance(obj, Channel):
                    ns_obj = obj
                    break
            else:
                if not ns_obj:
                    # non riesco a recuperare le info di un channel
                    return
            message_obj = self.context

            unsubscribe_footer_template = self.context.restrictedTraverse(
                '@@unsubscribe_channel_template'
            )
            parameters = {
                'portal_name': api.portal.get().title,
                'unsubscribe_link': ns_obj.absolute_url()
                + '/@@unsubscribe',
            }
            unsubscribe_footer_text = unsubscribe_footer_template(**parameters)

            body = u''
            body += ns_obj.header.output if ns_obj.header else u''
            body += u'<style>{css}</style>'.format(
                css=ns_obj.css_style or u''
            )
            body += message_obj.text.output if message_obj.text else u''
            body += ns_obj.footer.output if ns_obj.footer else u''
            body += unsubscribe_footer_text if unsubscribe_footer_text else u''

            # passo la mail per il transform
            portal = api.portal.get()
            body = portal.portal_transforms.convertTo('text/mail', body)

            response_email = None
            if ns_obj.response_email:
                response_email = ns_obj.response_email
            else:
                response_email = u'noreply@rer.it'

            # per mandare la mail non passo per l'utility
            # in ogni caso questa mail viene mandata da plone
            mailHost = api.portal.get_tool(name='MailHost')
            for email in emails:
                mailHost.send(
                    body.getData(),
                    mto=email.strip(),
                    mfrom=response_email,
                    subject='Messaggio di prova',
                    charset='utf-8',
                    msg_type='text/html',
                    immediate=True
                )

        except SMTPRecipientsRefused:
            self.errors = u'problemi con l\'invio del messaggio'

        # da sistemare la gestione degli errori
        if 'errors' in self.__dict__.keys():
            api.portal.show_message(
                message=self.errors,
                request=self.request,
                type=u'error'
            )
        else:
            api.portal.show_message(
                message=u'Messaggio inviato correttamente!',
                request=self.request,
                type=u'info'
            )


message_sending_test = wrap_form(
    MessageSendingTest,
    index=ViewPageTemplateFile('templates/sendingtest.pt')
)
