# -*- coding: utf-8 -*-
from plone import api
from Products.CMFPlone.resources import add_bundle_on_request
from Products.Five.browser import BrowserView
from zope.annotation.interfaces import IAnnotations

import json


KEY = 'rer.newsletter.message.details'


class ChannelHistory(BrowserView):

    def __init__(self, context, request):
        self.context = context
        self.request = request

        add_bundle_on_request(self.request, 'message_datatables')

    def getMessageSentDetails(self):

        if self.context.portal_type == 'Channel':
            messageList = api.content.find(
                context=self.context,
                portal_type='Message'
            )

        activeMessageList = []
        if messageList:
            for message in messageList:
                obj = message.getObject()
                annotations = IAnnotations(obj)
                if KEY in annotations.keys():
                    count = 0
                    for k, v in annotations[KEY].iteritems():
                        au = v['num_active_subscribers']
                        sd = v['send_date']

                        element = {}
                        element['id'] = count
                        element['uid'] = obj.title + str(count)
                        element['message'] = obj.title
                        element['active_users'] = au
                        element['send_date'] = sd
                        count += 1
                        activeMessageList.append(element)

        return json.dumps(activeMessageList)

    def deleteMessageFromHistory(self):
        message_history = self.request.get('message_history')

        # recupero tutti i messaggi del canale
        messages = api.content.find(
            context=self.context,
            portal_type='Message',
        )
        for message in messages:
            obj = message.getObject()
            annotations = IAnnotations(obj)
            if KEY in annotations.keys():
                annotations = annotations[KEY]
                for k in annotations.keys():
                    if message_history == k:
                        del annotations[k]
                        break
        response = {}
        response['ok'] = True
        return json.dumps(response)
