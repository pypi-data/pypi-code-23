# -*- coding: utf-8 -*-
from jquery.pyproxy.plone import jquery, JQueryProxy
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from zest.emailhider.interfaces import IMailable
from zope.component import getMultiAdapter
from zope.component import getUtility
import logging

logger = logging.getLogger('zest.emailhider')


class EmailHider(BrowserView):

    def UID(self):
        mailable = IMailable(self.context, None)
        if mailable is None:
            return
        return mailable.UID()

    def email(self):
        mailable = IMailable(self.context, None)
        if mailable is None:
            return
        return mailable.email


class JqEmailHider(BrowserView):
    """jQuery view for revealing the email address of an object.

    The object is given by a uid.

    Objects should have a simple adapter to the IMailable interface,
    so we can ask this adapter for an 'email' attribute.

    Special case: when the uid contains 'email' or 'address' it is
    clearly no real uid.  In that case we do nothing with the
    IMailable interface but we try to get a property with this 'uid'
    from the property sheet of the portal.  Main use case is of course
    the 'email_from_address', but you can add other addresses as
    well, like 'info_email'.
    """

    @jquery
    def reveal_email(self):
        # single uid
        uids = self.request.form.get('uid', None)
        if not uids:
            # With multiple uids the name looks a bit weird.
            uids = self.request.form.get('uid[]', None)
            if not uids:
                # Nothing to do.  Strange.
                # Well, happens when a bot finds this url interesting.
                logger.warning('No uids found in request.')
                # Return an answer anyway, otherwise you get errors in the
                # javascript console.
                return JQueryProxy()
        if isinstance(uids, basestring):
            uids = [uids]
        jq = JQueryProxy()
        for uid in uids:
            jq = self.handle_single_email(uid, jq)
        return jq

    def handle_single_email(self, uid, jq):
        email = None
        if 'email' in uid or 'address' in uid:
            # This is definitely not a real uid.  Try to get it from
            # the registry or as a portal property.  Best example:
            # email_from_address.
            registry = getUtility(IRegistry)
            # Mostly Plone 5 and higher, although you can add
            # plone.email_from_address or plone.some_email in the
            # registry yourself on earlier Plone versions.
            email = registry.get('plone.' + uid, '')
            if email:
                logger.debug("From registry: plone.%s=%s", uid, email)
            else:
                # Backwards compatibility for Plone 4.
                portal_state = getMultiAdapter((self.context, self.request),
                                               name=u'plone_portal_state')
                portal = portal_state.portal()
                email = portal.getProperty(uid)
                if email:
                    logger.debug("From portal property: %s=%s", uid, email)
                else:
                    logger.warn("No registry entry plone.%s or portal "
                                "property %s.", uid, uid)
        else:
            email = self.find_email_for_object_by_uid(uid)

        if email:
            email_link = u'<a href="mailto:%s">%s</a>' % (email, email)
        else:
            logger.debug("No email found for uid %s", uid)
            # No sense in leaving the default text of 'Activate
            # JavaScript to see this address.'
            # We could add a <!-- comment --> but jQuery ignores this.
            email_link = u''

        jq('.email-uid-%s' % uid).replaceWith(email_link)
        return jq

    def find_email_for_object_by_uid(self, uid):
        # Get catalog only once per request.
        catalog = getattr(self, '_uid_catalog', None)
        if catalog is None:
            catalog = getToolByName(self.context, 'uid_catalog')
            self._uid_catalog = catalog
        # Find object by uid
        brains = catalog(UID=uid)
        if len(brains) != 1:
            logger.warn("No brains for uid %s", uid)
            return
        target = brains[0].getObject()
        mailable = IMailable(target, None)
        if mailable is None:
            logger.warn("Uid %s not mailable.", uid)
            return
        return mailable.email
