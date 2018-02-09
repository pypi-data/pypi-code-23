# -*- coding: utf-8 -*-
# Default ENCODING = 'UTF-8'


from z3c.form import interfaces
from zope import schema
#from zope.interface import Interface
from zope.interface import alsoProvides
from plone.directives import form
from medialog.controlpanel.interfaces import IMedialogControlpanelSettingsProvider
from collective.z3cform.datagridfield import DataGridFieldFactory 
from collective.z3cform.datagridfield.registry import DictRow

from zope.i18nmessageid import MessageFactory

_ = MessageFactory('medialog.markdown')


class IButtonPair(form.Schema):
    name = schema.ASCIILine(
        title=_(u'name', 'Name'),
        required=False,
        default="Important"
    )

    icon = schema.ASCIILine(
        title=_(u'icon', 'Icon'),
        required=False,
        default="fa-exclamation" 
    )
    
    buttontext = schema.TextLine(
        title=_(u'buttontext', 'buttontext'),
        required=False,
        default=u"""!!! important "Important"\\n     \b"""
    )
 
 
class IMarkdownSettings(form.Schema):
    """Adds settings to medialog.controlpanel
    """

    form.fieldset(
        'markdown',
        label=_(u'Markdown settings'),
        fields=[
             'button_pairs',
             'live_preview',
        ],
    )

    live_preview = schema.Bool (
        title = _(u'Live preview', 'live preview'),
    )
    
    form.widget(button_pairs=DataGridFieldFactory)
    button_pairs = schema.List(
        title = _(u"button_pairs", 
            default=u"Ekstra buttons"),
        value_type=DictRow(schema=IButtonPair),
    )
    
        
alsoProvides(IMarkdownSettings, IMedialogControlpanelSettingsProvider)