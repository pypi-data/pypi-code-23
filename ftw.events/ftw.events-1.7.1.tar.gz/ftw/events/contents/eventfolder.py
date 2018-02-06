from ftw.events import _
from ftw.events.interfaces import IEventFolder
from plone import api
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.content import Container
from plone.directives import form
from zope.component.hooks import getSite
from zope.i18n import translate
from zope.interface import alsoProvides
from zope.interface import implements


class IEventFolderSchema(form.Schema):
    pass

alsoProvides(IEventFolderSchema, IFormFieldProvider)


class EventFolder(Container):
    implements(IEventFolder)


def create_event_listing_block(event_folder, event=None):
    """
    This methods creates an event listing block inside the given event folder
    and is used as a handler for a subscriber listening on the creation
    of event folders.
    """
    api.content.create(
        container=event_folder,
        type='ftw.events.EventListingBlock',
        title=translate(
            _(u'title_default_eventlisting_block', u'Events'),
            context=getSite().REQUEST,
        ),
        current_context=True,
        subjects=[],
        show_title=False,
        filter_by_path=[],
    )
