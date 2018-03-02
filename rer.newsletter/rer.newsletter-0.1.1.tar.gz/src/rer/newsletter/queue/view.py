# -*- coding: utf-8 -*-
from datetime import datetime
from persistent.dict import PersistentDict
from plone import api
from plone.protect.interfaces import IDisableCSRFProtection
from Products.Five.browser import BrowserView
from rer.newsletter import logger
from rer.newsletter.content.channel import Channel
from rer.newsletter.content.message import Message
from rer.newsletter.utility.channel import IChannelUtility
from rer.newsletter.utility.channel import OK
from rer.newsletter.utility.channel import UNHANDLED
from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility
from zope.interface import alsoProvides


KEY = 'rer.newsletter.message.details'


class ProcessQueue(BrowserView):

    def _sendNotification(self, status, channel, message):
        """ send notification to user when asynch call is finished """
        portal = api.portal.get()
        if channel.sender_email:
            message_template = None
            if status == OK:
                message_template = message.restrictedTraverse(
                    '@@{0}'.format('asynch_send_success')
                )
            else:
                message_template = message.restrictedTraverse(
                    '@@{0}'.format('asynch_send_fail')
                )
            parameters = {
                'header': channel.header.output if channel.header else u'',
                'footer': channel.footer.output if channel.footer else u'',
                'style': channel.css_style if channel.css_style else u'',
                'portal_name': portal.title,
                'channel_name': channel.title,
                'message_title': message.title,
            }
            mail_text = message_template(**parameters)
            mail_text = portal.portal_transforms.convertTo(
                'text/mail', mail_text)

            response_email = None
            if channel.response_email:
                response_email = channel.response_email

            mail_host = api.portal.get_tool(name='MailHost')
            mail_host.send(
                mail_text.getData(),
                mto=channel.sender_email,
                mfrom=response_email,
                subject='Risultato invio asincrono di {0}'.format(
                    message.title),
                charset='utf-8',
                msg_type='text/html'
            )
        else:
            logger.exception(
                'Non è stato impostato l\'indirizzo del mittente',
            )

    def _getChannel(self):
        channel = None
        for obj in self.aq_chain:
            if isinstance(obj, Channel):
                channel = obj
                break
        else:
            if not channel:
                return
        return channel

    def _getMessage(self):
        message = None
        for obj in self.aq_chain:
            if isinstance(obj, Message):
                message = obj
                break
        else:
            if not message:
                return
        return message

    def __call__(self):
        """ asynchronous call """
        # la disabilito perchè in questa vista ci possono arrivare soltanto i
        # processi asincroni di collective.taskqueue
        alsoProvides(self.request, IDisableCSRFProtection)

        status = UNHANDLED
        api_channel = getUtility(IChannelUtility)
        channel = self._getChannel()
        message = self._getMessage()

        if channel:
            unsubscribe_footer_template = message.restrictedTraverse(
                '@@unsubscribe_channel_template'
            )
            parameters = {
                'portal_name': api.portal.get().title,
                'unsubscribe_link': channel.absolute_url()
                + '/@@unsubscribe',
            }
            unsubscribe_footer_text = unsubscribe_footer_template(**parameters)
            api_channel.sendMessage(
                channel.id_channel, message, unsubscribe_footer_text
            )

            # i dettagli sull'invio del messaggio per lo storico
            annotations = IAnnotations(message)
            if KEY not in annotations.keys():
                annotations[KEY] = PersistentDict({})

            annotations = annotations[KEY]
            now = datetime.today().strftime('%d/%m/%Y %H:%M:%S')
            active_users, status = api_channel.getNumActiveSubscribers(
                channel.id_channel
            )

            if status != OK:
                logger.exception(
                    'Problemi con la richiesta: {0}'.format(
                        self.request.get('HTTP_X_TASK_ID')),
                )
                # riporto indietro lo stato del messaggio nel caso sia 'sent'
                # if api.content.get_state(obj=message) == 'sent':
                #     api.content.transition(obj=message, transition='resend')
            else:
                annotations[message.title + str(len(annotations.keys()))] = {
                    'num_active_subscribers': active_users,
                    'send_date': now,
                }
            self._sendNotification(
                status=status,
                channel=channel,
                message=message,
            )
