from Products.CMFCore.utils import getToolByName


def default_profile_installed(portal):
    set_calendar_types(portal)
    reindex_indexes(portal)


def set_calendar_types(context):
    """
    Mark `ftw.events.EventPage` as an calendar type in portal_calendar.
    """
    portal_calendar = getToolByName(context, 'portal_calendar')
    types = list(portal_calendar.calendar_types)
    types.append('ftw.events.EventPage')
    portal_calendar.calendar_types = tuple(types)


def reindex_indexes(portal):
    """
    `plone.app.events` replaces the start and end index by a
    RecurringDateIndex (before DateIndex) but it omits to reindex
    the new index. This causes the loss of the start and end index
    data of every content. So we need to take care of reindexing
    the indexes.
    """
    catalog = getToolByName(portal, 'portal_catalog')
    catalog.reindexIndex('start', None)
    catalog.reindexIndex('end', None)
