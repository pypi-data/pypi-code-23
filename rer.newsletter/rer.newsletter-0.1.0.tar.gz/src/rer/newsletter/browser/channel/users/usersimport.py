# -*- coding: utf-8 -*-
from plone import api
from plone.namedfile.field import NamedBlobFile
from rer.newsletter import _
from rer.newsletter.utility.channel import IChannelUtility
from rer.newsletter.utility.channel import OK
from rer.newsletter.utility.channel import UNHANDLED
from z3c.form import button
from z3c.form import field
from z3c.form import form
from zope import schema
from zope.component import getUtility
from zope.interface import Interface

import csv
import re
import StringIO


def check_separator(value):
    match = re.match('^,|^;', value)
    if match:
        return True
    else:
        return False


class IUsersImport(Interface):

    userListFile = NamedBlobFile(
        title=_(u'title_users_list_file', default=u'Users List File'),
        description=_(u'description_file', default=u'File must be a CSV'),
        required=True,
    )

    # se questo e ceccato allora i dati non vengono inseriti
    emptyList = schema.Bool(
        title=_(u'title_empty_list', default=u'Empties users list'),
        description=_(u'description_empty_list',
                      default=u'Empties channel users list'),
        required=False
    )

    # se e ceccato sia questo dato che 'emptyList'
    # allora do precedenza a emptyList
    removeSubscribers = schema.Bool(
        title=_(u'title_remove_subscribers',
                default=u'Remove subscribers of the list'),
        description=_(
            u'description_remove_subscribers',
            default=u'Remove users of CSV from channel'
        ),
        required=False
    )

    headerLine = schema.Bool(
        title=_(u'title_header_line',
                default=u'Header Line'),
        description=_(u'description_header_line',
                      default=_(u'if CSV File contains a header line')),
        required=False
    )

    separator = schema.TextLine(
        title=_(u'title_separator',
                default=u'CSV separator'),
        description=_(u'description_separator',
                      default=_(u'Separator of CSV file')),
        default=u';',
        required=True,
        constraint=check_separator,
    )


def _mailValidation(mail):
    # valido la mail
    match = re.match(
        '^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+'
        '(\.[a-z0-9-]+)*(\.[a-z]{2,4})$',
        mail
    )
    if match is None:
        return False
    return True


class UsersImport(form.Form):

    ignoreContext = True
    fields = field.Fields(IUsersImport)

    def processCSV(self, data, headerline, separator):
        io = StringIO.StringIO(data)

        reader = csv.reader(
            io,
            delimiter=separator.encode('ascii', 'ignore'),
            dialect='excel',
            quotechar='\''
        )

        index = 0
        if headerline:
            header = reader.next()

            # leggo solo la colonna della email
            index = None
            for i in range(0, len(header)):
                if header[i].decode('utf-8-sig') == 'email':
                    index = i
            if index is None:
                api.portal.show_message(
                    message=u'Il CSV non ha la colonna email oppure il '
                    'separatore potrebbe non essere corretto',
                    request=self.request,
                    type=u'error'
                )

        if index is not None:
            usersList = []
            line_number = 0
            for row in reader:
                line_number += 1
                mail = row[index].decode('utf-8-sig')
                if _mailValidation(mail):
                    usersList.append(row[index].decode('utf-8-sig'))

            return usersList

    @button.buttonAndHandler(_(u'charge_userimport', default=u'Import'))
    def handleSave(self, action):
        status = UNHANDLED
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        # prendo la connessione con il server mailman
        api_channel = getUtility(IChannelUtility)

        # devo svuotare la lista di utenti del channel
        if data['emptyList']:
            status = api_channel.emptyChannelUsersList(
                self.context.id_channel
            )

        csv_file = data['userListFile'].data
        # esporto la lista di utenti dal file
        usersList = self.processCSV(
            csv_file,
            data['headerLine'],
            data['separator']
        )

        # controllo se devo eliminare l'intera lista di utenti
        # invece di importarla
        if data['removeSubscribers'] and not data['emptyList']:
            # chiamo l'api per rimuovere l'intera lista di utenti
            if usersList:
                status = api_channel.deleteUserList(
                    self.context.id_channel,
                    usersList,
                )

        else:
            if usersList:
                # mi connetto con le api di mailman
                status = api_channel.importUsersList(
                    self.context.id_channel,
                    usersList,
                )

        if status == OK:
            status = _(
                u'generic_subscribe_message_success',
                default=u'User Subscribed'
            )
            api.portal.show_message(
                message=status,
                request=self.request,
                type=u'info'
            )
