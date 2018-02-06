from ftw.upgrade import UpgradeStep
from plone.app.event.dx.behaviors import IEventLocation


class RemoveEventLocationBehavior(UpgradeStep):
    """Remove event location behavior.
    """

    def __call__(self):
        for obj in self.objects({'portal_type': 'ftw.events.EventPage'},
                                'Migration location'):
            obj.location_title = IEventLocation(obj).location

        self.install_upgrade_profile()
