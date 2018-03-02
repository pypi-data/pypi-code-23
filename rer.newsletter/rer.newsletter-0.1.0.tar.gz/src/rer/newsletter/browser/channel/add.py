# -*- coding: utf-8 -*-
from plone import api
from plone.dexterity.browser import add
from rer.newsletter import _
from rer.newsletter import logger
from rer.newsletter.utility.channel import IChannelUtility
from rer.newsletter.utility.channel import OK
from rer.newsletter.utility.channel import UNHANDLED
from z3c.form import button
from zope.component import getUtility


class AddForm(add.DefaultAddForm):

    # button handler
    @button.buttonAndHandler(u'Salva', name='save')
    def handleAdd(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        # validazione dei campi della form
        status = UNHANDLED
        obj = self.createAndAdd(data)
        if obj:
            self._finishedAdd = True

            # chiamo l'utility per la creazione anche il channel
            api_channel = getUtility(IChannelUtility)
            status = api_channel.addChannel(obj.id_channel)

            if status == OK:
                api.portal.show_message(
                    message=_(u'add_channel', default='Channel Created'),
                    request=self.request,
                    type=u'info'
                )

        if not obj or status != OK:
            logger.exception(
                _(u'generic_problem_add_channel',
                    default=u'Unhandled problem with add of channel.')
            )
            status = u'Problems...{status}'.format(status=status)
            api.portal.show_message(
                message=status,
                request=self.request,
                type=u'error'
            )


class AddView(add.DefaultAddView):
    form = AddForm
