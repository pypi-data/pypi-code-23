# -*- coding: utf-8 -*-
from archetypes.schemaextender.field import ExtensionField
from archetypes.schemaextender.interfaces import ISchemaExtender
from cs.at.gipuzkoairekia import _
from cs.at.gipuzkoairekia.interfaces import IGipuzkoaIrekiaFolder
from Products.Archetypes.interfaces import IFieldDefaultProvider
from zope.component import adapter
from zope.globalrequest import getRequest
from zope.interface import implementer


try:
    from Products.LinguaPlone import atapi
except ImportError:
    from Products.Archetypes import public as atapi


class MyStringField(ExtensionField, atapi.StringField):
    """A trivial field."""


@implementer(IFieldDefaultProvider)
@adapter(IGipuzkoaIrekiaFolder)
def default_language(context):
    request = getRequest()
    return request.get('LANGUAGE', 'eu')


@implementer(ISchemaExtender)
@adapter(IGipuzkoaIrekiaFolder)
class GipuzkoaIrekiaFolderExtender(object):

    fields = [
        MyStringField(
            'institution_code',
            widget=atapi.StringWidget(
                label=_(u'Institution code (Open-data portal)'),
                description=_(u'Enter here the code of the institution'),
            )
        ),
        MyStringField(
            'group_id',
            widget=atapi.StringWidget(
                label=_(u'Institution code (Transpareceny portal)'),
                description=_(u'Enter here the code of the institution'),
            )
        ),
        MyStringField(
            'gipuzkoairekia_language',
            vocabulary=atapi.DisplayList([
                ('eu', _(u'Euskara')),
                ('es', _(u'Espanol')),
                ('en', _(u'English')),
            ]),
            widget=atapi.SelectionWidget(
                type='radio',
                label=_(u'Language'),
                description=_(u'Select the language in which the '
                              u'contents will be shown'),
            )
        ),



    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields
