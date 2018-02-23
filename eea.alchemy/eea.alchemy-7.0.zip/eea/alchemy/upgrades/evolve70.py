""" Evolve to version 5.0
"""
import logging
from zope.component import queryAdapter
from zope.component.hooks import getSite
from Products.CMFCore.utils import getToolByName
from eea.alchemy.controlpanel.interfaces import IAlchemySettings
logger = logging.getLogger('eea.alchemy')

def upgrade(context):
    """ Remove Alchemy API support
    """
    site = getSite()
    ptool = getToolByName(site, 'portal_properties')
    atool = getattr(ptool, 'alchemyapi', None)
    if atool:
        ptool.manage_delObjects(ids=['alchemyapi'])

    settings = queryAdapter(site, IAlchemySettings)
    if getattr(settings, 'token', None):
        delattr(settings, 'token')
