# -*- coding: utf-8 -*-
from ..settings import ISettingsSchema
from datetime import datetime
from datetime import timedelta
from persistent.dict import PersistentDict
from plone import api
from plone.protect.interfaces import IDisableCSRFProtection
from Products.Five.browser import BrowserView
from rer.newsletter import logger
from rer.newsletter.utility.base import KEY
from zope.annotation.interfaces import IAnnotations
from zope.interface import alsoProvides


class DeleteExpiredUsersView(BrowserView):
    """ Delete expired users from channels """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def update_annotations(self, channel):
        expired_date = datetime.now()
        expired_time_token = api.portal.get_registry_record(
            'expired_time_token', ISettingsSchema)

        annotations = IAnnotations(channel.getObject())
        valid_users_dict = PersistentDict({})
        if KEY in annotations:
            for val in annotations[KEY].keys():
                creation_date = datetime.strptime(
                    annotations[KEY][val]['creation_date'],
                    '%d/%m/%Y %H:%M:%S')
                if expired_date < creation_date \
                        + timedelta(hours=expired_time_token) or \
                        annotations[KEY][val]['is_active']:
                    valid_users_dict[val] = annotations[KEY][val]
            annotations[KEY] = valid_users_dict

    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        logger.info(u'START:Remove expired user from channels')
        channels_brain = api.content.find(
            context=api.portal.get(),
            portal_type='Channel'
        )
        map(lambda x: self.update_annotations(x), channels_brain)
        logger.info(u'DONE:Remove expired user from channels')
        return True
