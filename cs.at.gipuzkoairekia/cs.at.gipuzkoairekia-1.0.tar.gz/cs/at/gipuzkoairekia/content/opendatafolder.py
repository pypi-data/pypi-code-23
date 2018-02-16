# -*- coding: utf-8 -*-
from cs.at.gipuzkoairekia.config import PROJECTNAME
from cs.at.gipuzkoairekia.interfaces import IOpenDataFolder
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata
from zope.interface import implementer


try:
    from Products.LinguaPlone import atapi
except ImportError:
    from Products.Archetypes import atapi


OpenDataFolderSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((
    # -*- Your Archetypes field definitions here ... -*-

))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

OpenDataFolderSchema['title'].storage = atapi.AnnotationStorage()
OpenDataFolderSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(OpenDataFolderSchema, moveDiscussion=False)


@implementer(IOpenDataFolder)
class OpenDataFolder(base.ATCTContent):
    """Content-type for sections"""

    meta_type = 'OpenDataFolder'
    schema = OpenDataFolderSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    # -*- Your ATSchema to Python Property Bridges Here ... -*-


atapi.registerType(OpenDataFolder, PROJECTNAME)
