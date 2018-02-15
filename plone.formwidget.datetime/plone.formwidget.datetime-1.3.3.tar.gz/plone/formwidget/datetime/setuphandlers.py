from zope.interface import implementer
from Products.CMFPlone.interfaces import INonInstallable


@implementer(INonInstallable)
class HiddenProfiles(object):

    def getNonInstallableProfiles(self):
        """Prevents profiles, which should not be user-installable from showing
        up in the profile list when creating a Plone site.

        plone.formwidget.datetime:default .. Without any forms actually using
        this packge, this it makes no sense. Packages, which use
        plone.formwidget.datetime, should install it's profile.

        """
        return [u'plone.formwidget.datetime:default']
