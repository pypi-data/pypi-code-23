# -*- coding: utf-8 -*-
import unittest

from collective.polls.content.poll import Poll
from interlegis.portalmodelo.policy.config import DEFAULT_CONTENT, SITE_STRUCTURE
from interlegis.portalmodelo.policy.testing import INTEGRATION_TESTING
from plone import api


class PortalStructureTestCase(unittest.TestCase):
    """Ensure site structure is created, published and configured.
    """

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def test_default_content_was_deleted(self):
        default_content = list(DEFAULT_CONTENT)
        # front-page was recreated as a collective.cover page
        default_content.remove('front-page')
        for item in default_content:
            self.assertNotIn(
                item, self.portal, u'{0} not removed'.format(item))

    def test_new_portal_structure_was_created(self):
        for item in SITE_STRUCTURE:
            id = item['id']
            self.assertIn(id, self.portal, u'{0} not created'.format(id))
            if '_children' in item:
                for child in item['_children']:
                    _id = child['id']
                    self.assertIn(
                        _id,
                        self.portal[id],
                        u'{0}/{1} not created'.format(id, _id)
                    )

    def test_content_was_published(self):

        def check_published(root, item):
            if item['type'] in ['Image', 'File']:
                return
            obj = root[item['id']]
            if '_transition' in item and item['_transition'] is None:
                # is private
                self.assertEqual(api.content.get_state(obj), 'private')
            else:
                # is published or equivalent
                if isinstance(obj, Poll):
                    self.assertEqual(api.content.get_state(obj), 'open')
                else:
                    self.assertEqual(api.content.get_state(obj), 'published')
            if '_children' in item:
                for child in item['_children']:
                    check_published(obj, child)

        for item in SITE_STRUCTURE:
            check_published(self.portal, item)

    def test_content_constraints(self):
        for item in SITE_STRUCTURE:
            if '_addable_types' in item:
                id = item['id']
                obj = self.portal[id]
                path = obj.absolute_url_path()
                addable_types = obj.getLocallyAllowedTypes()
                self.assertItemsEqual(
                    addable_types,
                    item['_addable_types'],
                    u'constraints not set on {0}'.format(path)
                )
                if '_children' in item:
                    for child in item['_children']:
                        if '_addable_types' in child:
                            _id = child['id']
                            obj = self.portal[id][_id]
                            path = obj.absolute_url_path()
                            addable_types = obj.getLocallyAllowedTypes()
                            self.assertItemsEqual(
                                addable_types,
                                child['_addable_types'],
                                u'constraints not set on {0}'.format(path)
                            )

    def test_cover_is_site_default_page(self):
        default_page = self.portal.getDefaultPage()
        self.assertEqual(default_page, 'front-page')

    def test_solgemafullcalendar_view_was_set(self):
        agendas = [
            self.portal['institucional']['eventos'],
        ]
        for a in agendas:
            self.assertEqual(a.getLayout(), 'solgemafullcalendar_view')

    def test_feedback_poll(self):
        folder = self.portal['enquetes']
        poll = getattr(folder, 'gostou-do-novo-site', None)
        self.assertIsNotNone(poll)
        self.assertEqual(poll.title, u'Gostou do novo site?')
        self.assertEqual(len(poll.options), 3)
        self.assertEqual(api.content.get_state(poll), 'open')

    def test_open_forums(self):
        folder = self.portal['foruns']
        forums = ['educacao', 'saude', 'transporte']
        for f in forums:
            self.assertIn(f, folder)
            self.assertEqual(api.content.get_state(folder[f]), 'freeforall')

    def test_add_csvdata(self):
        permission = 'interlegis.portalmodelo.transparency: Add CSVData'
        pm = api.portal.get_tool('portal_membership')
        check_permission = pm.checkPermission
        with api.env.adopt_roles(['Manager', ]):
            portal = api.portal.get()
            # Not allowed on site root
            self.assertFalse(check_permission(permission, portal))
            # Allowed on transparencia
            transparencia = portal['transparencia']
            self.assertTrue(check_permission(permission, transparencia))
