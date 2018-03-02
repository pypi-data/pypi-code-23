# -*- coding: utf-8 -*-
from mailmanclient import Client
from mailmanclient import MailmanConnectionError
from mailmanclient._client import HTTPError
from rer.newsletter import logger
from rer.newsletter.utility.channel import ALREADY_SUBSCRIBED
from rer.newsletter.utility.channel import IChannelUtility
from rer.newsletter.utility.channel import OK
from rer.newsletter.utility.channel import SUBSCRIBED
from zope.interface import implementer

import json


# move to p.a.registry or zope.conf
# Please note that port ‘9001’ is used above, since mailman’s test server
# runs on port 9001. In production Mailman’s REST API usually listens
# on port 8001.
API_ENDPOINT = 'http://localhost:9001/3.1'
API_USERNAME = 'restadmin'
API_PASSWORD = 'restpass'


@implementer(IChannelUtility)
class MailmanHandler(object):
    """utility class to comunicate with mailman server"""

    def _api(self):
        try:
            return Client(API_ENDPOINT, API_USERNAME, API_PASSWORD)
        except MailmanConnectionError:
            logger.error('Could not connect to Mailman API %s', API_ENDPOINT)
            # raise
            return None

    def lists(self):
        client = self._api()
        return client.lists

    def subscribe(self, channel, mail, name=None):
        client = self._api()
        if not client:
            logger.warning('raise exception')
            logger.warning('fake %s %s subscription', channel, mail)
            return SUBSCRIBED
        _list = client.get_list(channel)
        try:
            _data = _list.subscribe(
                mail,
                name or mail,
                pre_verified=False,
                pre_approved=False
            )
            logger.info('DEBUG: %s', _data)
            # {u'token_owner': u'subscriber',
            #   u'http_etag': u''2f1dfffd552b1a6a0514ad416d4e426d8c927d44'',
            #   u'token': u'0000000000000000000000000000000000000001'}
        except HTTPError as exc:
            if exc.code == 409:
                logger.info('DEBUG: %s', exc)
                return ALREADY_SUBSCRIBED
        return SUBSCRIBED

    def unsubscribe(self, channel, mail):
        logger.info('DEBUG: unsubscribe %s %s', channel, mail)
        return True

    def sendMessage(self, channel, message):
        logger.info('DEBUG: sendMessage %s %s', channel, message)
        return True

    def addChannel(self, channel):
        logger.info('DEBUG: addChannel %s', channel)
        return True

    def importUsersList(self, usersList, channel):
        logger.info('DEBUG: import userslist %s in %s', usersList, channel)
        return True

    def emptyChannelUsersList(self, channel):
        # vedere logica per eliminazione dell'intera lista di utenti di una nl
        logger.info('DEBUG: emptyChannelUsersList %s', channel)
        return True

    def deleteUser(self, mail, channel):
        logger.info(
            'DEBUG: delete user %s from channel %s',
            mail,
            channel
        )
        return True

    def exportUsersList(self, channel):
        logger.info('DEBUG: export users of channel: %s', channel)
        response = []

        element = {}
        element['id'] = 1
        element['Emails'] = 'filippo.campi@redturtle.it'
        response.append(element)

        element = {}
        element['id'] = 2
        element['Emails'] = 'giacomo.monari@redturtle.it'
        response.append(element)

        return json.dumps(response), OK

    def deleteUserList(self, usersList, channel):
        logger.info('delete userslist %s from %s',
                    usersList, channel)
        return True
