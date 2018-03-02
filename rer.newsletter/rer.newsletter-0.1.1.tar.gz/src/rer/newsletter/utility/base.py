# -*- coding: utf-8 -*-
from datetime import datetime
from datetime import timedelta
from persistent.dict import PersistentDict
from plone import api
from rer.newsletter import _
from rer.newsletter import logger
from rer.newsletter.utility.channel import ALREADY_ACTIVE
from rer.newsletter.utility.channel import ALREADY_SUBSCRIBED
from rer.newsletter.utility.channel import IChannelUtility
from rer.newsletter.utility.channel import INEXISTENT_EMAIL
from rer.newsletter.utility.channel import INVALID_CHANNEL
from rer.newsletter.utility.channel import INVALID_EMAIL
from rer.newsletter.utility.channel import INVALID_SECRET
from rer.newsletter.utility.channel import MAIL_NOT_PRESENT
from rer.newsletter.utility.channel import OK
from zope.annotation.interfaces import IAnnotations
from zope.interface import implementer
from zope.interface import Invalid

import json
import re
import uuid


KEY = 'rer.newsletter.subscribers'


def mailValidation(mail):
    # valido la mail
    match = re.match(
        '^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]' +
        '+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$',
        mail
    )
    if match is None:
        raise Invalid(
            _(
                u'generic_problem_email_validation',
                default=u'Una o piu delle mail inserite non sono valide'
            )
        )
    return True


# da fixare la validazione
def uuidValidation(uuid_string):
    try:
        uuid.UUID(uuid_string, version=4)
    except ValueError:
        return False
    return True


def isCreationDateExpired(creation_date):
    # settare una data di scadenza di configurazione
    cd_datetime = datetime.strptime(creation_date, '%d/%m/%Y %H:%M:%S')
    t = datetime.today() - cd_datetime
    if t < timedelta(days=2):
        return True
    return False


@implementer(IChannelUtility)
class BaseHandler(object):
    """ utility class to send channel email with mailer of plone """

    def _storage(self, channel):
        obj = self._api(channel)
        if obj:
            annotations = IAnnotations(obj)
            if KEY not in annotations.keys():
                annotations[KEY] = PersistentDict({})
            return annotations[KEY], obj

    def _api(self, channel):
        """ return Channel and initialize annotations """
        nl = api.content.find(
            portal_type='Channel',
            id_channel=channel
        )

        el = None
        for n in nl:
            if n.getObject().id_channel == channel:
                el = n
                break

        if not el:
            return None
        obj = el.getObject()
        return obj

    def addChannel(self, channel):
        logger.info('DEBUG: add channel {0}'.format(channel))
        return OK

    def activateUser(self, channel, secret):
        logger.info('DEBUG: active user in %s', channel)
        annotations, channel_obj = self._storage(channel)
        if annotations is None:
            return INVALID_CHANNEL, None

        # valido il secret
        if not uuidValidation(secret):
            return INVALID_SECRET, None

        # attivo l'utente
        count = 0
        element_id = None
        for user in annotations:
            if annotations[user]['token'] == secret:
                if annotations[user]['is_active']:
                    return ALREADY_ACTIVE, user
                else:
                    element_id = user
                    break
            count += 1

        if element_id is not None:
            # riscrivo l'utente mettendolo a attivo
            annotations[element_id] = {
                'email': element_id,
                'is_active': True,
                'token': annotations[element_id]['token'],
                'creation_date': annotations[element_id]['creation_date'],
            }

            return OK, element_id
        else:
            return INVALID_SECRET, element_id

    def importUsersList(self, channel, usersList):
        logger.info('DEBUG: import userslist in %s', channel)
        annotations, channel_obj = self._storage(channel)
        if annotations is None:
            return INVALID_CHANNEL

        for user in usersList:
            match = re.match(
                '^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]' +
                '+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$',
                user
            )
            if match is not None:
                annotations[user] = {
                    'email': user,
                    'is_active': True,
                    'token': unicode(uuid.uuid4()),
                    'creation_date': datetime.today().strftime(
                        '%d/%m/%Y %H:%M:%S'
                    ),
                }
            else:
                logger.info('INVALID_EMAIL: %s', user)

        return OK

    def exportUsersList(self, channel):
        logger.info('DEBUG: export users of a channel: %s', channel)
        response = []
        annotations, channel_obj = self._storage(channel)
        if annotations is None:
            return None, INVALID_CHANNEL

        c = 0
        for user in annotations.keys():
            element = {}
            element['id'] = c
            element['email'] = annotations[user]['email']
            element['is_active'] = annotations[user]['is_active']
            element['creation_date'] = annotations[user]['creation_date']
            response.append(element)
            c += 1

        return json.dumps(response), OK

    def deleteUser(self, channel, mail=None, secret=None):
        logger.info('delete user %s from channel %s',
                    mail, channel)
        annotations, channel_obj = self._storage(channel)
        if annotations is None:
            return INVALID_CHANNEL, None

        if secret is not None:
            # cancello l'utente con il secret (AnonimousUser)

            # valido il secret
            if not uuidValidation(secret):
                return INVALID_SECRET, None

            for user in annotations:
                if annotations[user]['token'] == unicode(secret):
                    cd = annotations[user]['creation_date']
                    if isCreationDateExpired(cd):
                        del annotations[user]
                        return OK, user
                    else:
                        return INVALID_SECRET, user

            return MAIL_NOT_PRESENT, None

        else:
            # cancello l'utente con la mail (Admin)
            if mail in annotations.keys():
                del annotations[mail]
                return OK
            else:
                return MAIL_NOT_PRESENT

    def deleteUserList(self, channel, usersList):
        # manca il modo di far capire se una mail non e presente nella lista
        logger.info('delete userslist from %s', channel)
        annotations, channel_obj = self._storage(channel)
        if annotations is None:
            return INVALID_CHANNEL

        for user in usersList:
            if user in annotations.keys():
                del annotations[user]

        return OK

    def emptyChannelUsersList(self, channel):
        logger.info('DEBUG: emptyChannelUsersList %s', channel)
        annotations, channel_obj = self._storage(channel)
        if annotations is None:
            return INVALID_CHANNEL

        annotations.clear()

        return OK

    def unsubscribe(self, channel, user):
        logger.info('DEBUG: unsubscribe %s %s', channel, user)
        annotations, channel_obj = self._storage(channel)
        if annotations is None:
            return INVALID_CHANNEL, None

        secret = unicode(uuid.uuid4())
        if user in annotations.keys():
            annotations[user] = {
                'email': user,
                'is_active': annotations[user]['is_active'],
                'token': secret,
                'creation_date': datetime.today().strftime(
                    '%d/%m/%Y %H:%M:%S'
                ),
            }
        else:
            return INEXISTENT_EMAIL, None

        return OK, secret

    def addUser(self, channel, mail):
        logger.info('DEBUG: add user: %s %s', channel, mail)
        annotations, channel_obj = self._storage(channel)
        if annotations is None:
            return INVALID_CHANNEL

        if not mailValidation(mail):
            return INVALID_EMAIL

        # controllo che la mail non sia gia presente e attiva nel db
        for user in annotations.keys():
            if (
                (
                    mail == annotations[user]['email'] and
                    annotations[user]['is_active']
                ) or
                (
                    mail == annotations[user]['email'] and
                    not annotations[user]['is_active'] and
                    isCreationDateExpired(annotations[user]['creation_date'])
                )
            ):
                return ALREADY_SUBSCRIBED
        else:
            annotations[mail] = {
                'email': mail,
                'is_active': True,
                'token': unicode(uuid.uuid4()),
                'creation_date': datetime.today().strftime(
                    '%d/%m/%Y %H:%M:%S'
                ),
            }

        return OK

    def subscribe(self, channel, mail):
        logger.info('DEBUG: subscribe %s %s', channel, mail)
        annotations, channel_obj = self._storage(channel)
        if annotations is None:
            return INVALID_CHANNEL, None

        if not mailValidation(mail):
            return INVALID_EMAIL, None

        uuid_activation = unicode(uuid.uuid4())
        for user in annotations.keys():
            if (
                (
                    mail == annotations[user]['email'] and
                    annotations[user]['is_active']
                ) or
                (
                    mail == annotations[user]['email'] and
                    not annotations[user]['is_active'] and
                    isCreationDateExpired(annotations[user]['creation_date'])
                )
            ):
                return ALREADY_SUBSCRIBED, None
        else:
            annotations[mail] = {
                'email': mail,
                'is_active': False,
                'token': uuid_activation,
                'creation_date': datetime.today().strftime(
                    '%d/%m/%Y %H:%M:%S'
                ),
            }

        return OK, uuid_activation

    def _getMessage(self, channel, message, unsubscribe_footer):
        logger.debug('getMessage %s %s', channel, message.title)

        body = u''
        body += channel.header.output if channel.header else u''
        body += u'<style>{css}</style>'.format(css=channel.css_style or u'')
        body += message.text.output if message.text else u''
        body += channel.footer.output if channel.footer else u''
        body += unsubscribe_footer if unsubscribe_footer else u''

        # passo la mail per il transform
        portal = api.portal.get()
        body = portal.portal_transforms.convertTo('text/mail', body)

        return body

    def sendMessage(self, channel, message, unsubscribe_footer=None):
        logger.debug('sendMessage %s %s', channel, message.title)
        nl = self._api(channel)
        annotations, channel_obj = self._storage(channel)
        if annotations is None:
            return INVALID_CHANNEL

        # costruisco il messaggio
        body = self._getMessage(nl, message, unsubscribe_footer)

        nl_subject = ' - ' + nl.subject_email if nl.subject_email else u''
        subject = message.title + nl_subject

        # invio la mail ad ogni utente
        mail_host = api.portal.get_tool(name='MailHost')
        for user in annotations.keys():
            if annotations[user]['is_active']:
                mail_host.send(
                    body.getData(),
                    mto=annotations[user]['email'],
                    mfrom=nl.sender_email,
                    subject=subject,
                    charset='utf-8',
                    msg_type='text/html'
                )

        return OK

    def getNumActiveSubscribers(self, channel):
        logger.debug('Get number of active subscribers from %s', channel)
        annotations, channel_obj = self._storage(channel)
        if annotations is None:
            return None, INVALID_CHANNEL

        count = 0
        for user in annotations.keys():
            if annotations[user]['is_active']:
                count += 1

        return count, OK
