# -*- coding: utf-8 -*-
# from datetime import datetime
# from persistent.dict import PersistentDict
# from rer.newsletter.utility.channel import IChannelUtility
# from rer.newsletter.utility.channel import OK
# from smtplib import SMTPRecipientsRefused
# from zope.annotation.interfaces import IAnnotations
# from zope.component import getUtility
#
#
# # messaggi standard della form di dexterity
# # from Products.statusmessages.interfaces import IStatusMessage
# # from plone.dexterity.i18n import MessageFactory as dmf
# KEY = 'rer.newsletter.message.details'
#
#
# def changeMessageState(message, event):
#     if event.action == 'send':
#         try:
#             api_channel = getUtility(IChannelUtility)
#             api_channel.sendMessage(
#                 message.aq_parent.id_channel, message
#             )
#
#             # i dettagli sull'invio del messaggio per lo storico
#             annotations = IAnnotations(message)
#             if KEY not in annotations.keys():
#
#                 active_users, status = api_channel.getNumActiveSubscribers(
#                     message.aq_parent.id_channel
#                 )
#
#                 if status != OK:
#                     raise Exception(status)
#
#                 annotations[KEY] = PersistentDict({
#                     'num_active_subscribers': active_users,
#                     'send_date': datetime.today().strftime(
#                         '%d/%m/%Y %H:%M:%S'
#                     ),
#                 })
#
#         except SMTPRecipientsRefused:
#            raise SMTPRecipientsRefused(u"Problemi con l'invio del messaggio")
#         except Exception as inst:
#             message = api_channel.getErrorMessage(inst.args[0])
#             raise Exception(message)
