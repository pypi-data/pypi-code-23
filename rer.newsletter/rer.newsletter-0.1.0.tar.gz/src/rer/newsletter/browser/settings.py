# -*- coding: utf-8 -*-
from plone import schema
from plone.app.registry.browser import controlpanel
from rer.newsletter import _
from zope.interface import Interface


def checkExpiredTimeToken(value):
    if value > 0:
        return True


class ISettingsSchema(Interface):
    """ Schema for channel settings"""

    source_link = schema.TextLine(
        title=_(u'source_link', default=u'Link sorgente'),
        description=_(
            u'description_source_link',
            default=u'Indirizzo da sostituire'
        ),
        default=u'applicazioni.regione.emilia-romagna.it',
        required=False,
    )

    destination_link = schema.TextLine(
        title=_(u'destination_link', default=u'Link di destinazione'),
        description=_(
            u'description_destination_link',
            default=u'Indirizzo da sostituire'
        ),
        required=False,
    )

    expired_time_token = schema.Int(
        title=_(u'expired_time_token', default=u'Validità del token in ore'),
        required=False,
        default=48,
        # constraint=checkExpiredTimeToken,
    )


class ChannelSettings(controlpanel.RegistryEditForm):
    schema = ISettingsSchema
    id = 'ChannelSettings'
    label = _(u'channel_setting', default=u'Channel Settings')

    def updateFields(self):
        super(ChannelSettings, self).updateFields()

    def updateWidgets(self):
        super(ChannelSettings, self).updateWidgets()


class ChannelSettingsControlPanel(controlpanel.ControlPanelFormWrapper):

    form = ChannelSettings
