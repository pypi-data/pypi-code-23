from ftw.builder import builder_registry
from ftw.builder.dexterity import DexterityBuilder
from ftw.simplelayout.tests import builders


class EventFolderBuilder(DexterityBuilder):
    portal_type = 'ftw.events.EventFolder'

builder_registry.register('event folder', EventFolderBuilder)


class EventPageBuilder(DexterityBuilder):
    portal_type = 'ftw.events.EventPage'

    def __init__(self, *args, **kwargs):
        super(EventPageBuilder, self).__init__(*args, **kwargs)
        # ftw.builders auto-discovery does not work for recurrence:
        self.having(recurrence='')
        # using greenwich, since the test-site / browser is set up with it:
        self.having(timezone='Etc/Greenwich')

    def starting(self, date):
        return self.having(start=date)

    def ending(self, date):
        return self.having(end=date)

builder_registry.register('event page', EventPageBuilder)


class EventListingBlockBuilder(DexterityBuilder):
    portal_type = 'ftw.events.EventListingBlock'

builder_registry.register('event listing block', EventListingBlockBuilder)
