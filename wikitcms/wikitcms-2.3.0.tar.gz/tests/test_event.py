# Copyright (C) 2016 Red Hat
#
# This file is part of wikitcms.
#
# wikitcms is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Author: Adam Williamson <awilliam@redhat.com>

# these are all kinda inappropriate for pytest patterns
# pylint: disable=old-style-class, no-init, protected-access, no-self-use, unused-argument
# pylint: disable=invalid-name

"""Tests for event.py."""

from __future__ import unicode_literals
from __future__ import print_function

import fedfind.release
# note: we need the external 'mock', unittest.mock does not seem to
# work correctly with the @patch decorator still
import mock
import pytest
import wikitcms.event
import wikitcms.wiki as wk
from wikitcms.exceptions import FedfindNotFoundError

def fakemwpinit(self, site, name, *args, **kwargs):
    """Stub init for mwclient.Page, we can't just mock it out as we
    need to set site and name.
    """
    self.site = site
    self.name = name

class TestEventFedfind:
    """Tests related to fedfind release discovery from validation
    events.
    """
    # the 'fjajah' is just to make sure we're running offline; if I
    # screw up and add a test that hits the network it'll cause the
    # tests to hang/fail instead of succeeding a bit slower
    site = wk.Wiki('fjajah', do_init=False, force_login=False)

    @mock.patch('fedfind.release.Compose.exists', True)
    @mock.patch('fedfind.release.Compose.all_images', ['foo'])
    def test_candidate_ff_release_compose(self):
        """Straightforward ff_release test case for a candidate
        compose which is properly synced to stage. Should work the
        same whether or not we pass the cid hint, both properties
        should exist and be the Compose instance.
        """
        event = wikitcms.event.ComposeEvent(
            self.site, '27', 'RC', '1.6', cid='Fedora-27-20171105.0')
        assert isinstance(event.ff_release, fedfind.release.Compose)
        assert isinstance(event.ff_release_images, fedfind.release.Compose)
        event = wikitcms.event.ComposeEvent(self.site, '27', 'RC', '1.6')
        assert isinstance(event.ff_release, fedfind.release.Compose)
        assert isinstance(event.ff_release_images, fedfind.release.Compose)

    @mock.patch('fedfind.helpers.cid_from_label', return_value='')
    @mock.patch('fedfind.release.Compose.exists', False)
    @mock.patch('fedfind.release.Production.all_images', ['foo'])
    @mock.patch('fedfind.release.Production.cid', 'Fedora-27-20171105.0')
    def test_candidate_ff_release_compose_gap(self, fakecidfromlabel):
        """Test the 'compose gap' case: this occurs when a candidate
        compose has just been created, but not yet synced to stage,
        and also has not yet appeared in PDC. In this case, without
        the 'cid' hint, we will not be able to find the fedfind
        release associated with the event. With the hint, we should
        find it in the non-synced location (as a fedfind Production).
        """
        event = wikitcms.event.ComposeEvent(
            self.site, '27', 'RC', '1.6', cid='Fedora-27-20171105.0')
        assert isinstance(event.ff_release, fedfind.release.Production)
        assert isinstance(event.ff_release_images, fedfind.release.Production)
        event = wikitcms.event.ComposeEvent(self.site, '27', 'RC', '1.6')
        with pytest.raises(FedfindNotFoundError):
            print(event.ff_release)
        with pytest.raises(FedfindNotFoundError):
            print(event.ff_release_images)

    @mock.patch('fedfind.helpers.cid_from_label', return_value='Fedora-27-20171105.0')
    @mock.patch('fedfind.release.Compose.exists', False)
    @mock.patch('fedfind.release.Production.all_images', ['foo'])
    @mock.patch('fedfind.release.Production.cid', 'Fedora-27-20171105.0')
    def test_candidate_ff_release_compose_gap_pdc(self, fakecidfromlabel):
        """Test the case where the candidate compose has not yet
        synced to stage, but has appeared in PDC. In this case, we
        should find the ff_release in the non-synced location (as a
        fedfind Production) with or without the cid hint.
        """
        event = wikitcms.event.ComposeEvent(
            self.site, '27', 'RC', '1.6', cid='Fedora-27-20171105.0')
        assert isinstance(event.ff_release, fedfind.release.Production)
        assert isinstance(event.ff_release_images, fedfind.release.Production)
        event = wikitcms.event.ComposeEvent(self.site, '27', 'RC', '1.6')
        assert isinstance(event.ff_release, fedfind.release.Production)
        assert isinstance(event.ff_release_images, fedfind.release.Production)

    @mock.patch('fedfind.release.Compose.exists', True)
    @mock.patch('fedfind.release.Compose.all_images', [])
    @mock.patch('fedfind.release.Production.all_images', ['foo'])
    @mock.patch('fedfind.release.Production.cid', 'Fedora-27-20171105.0')
    def test_candidate_ff_release_compose_exists_no_images(self):
        """Test a potential tricky case where a candidate compose
        tree exists on stage but the images haven't shown up in it
        yet. With the cid hint, the event's ff_release should be the
        Compose instance, but its ff_release_images should be the
        Production instance. Without the hint, we won't get images.
        """
        event = wikitcms.event.ComposeEvent(
            self.site, '27', 'RC', '1.6', cid='Fedora-27-20171105.0')
        assert isinstance(event.ff_release, fedfind.release.Compose)
        assert isinstance(event.ff_release_images, fedfind.release.Production)
        event = wikitcms.event.ComposeEvent(self.site, '27', 'RC', '1.6')
        assert isinstance(event.ff_release, fedfind.release.Compose)
        with pytest.raises(FedfindNotFoundError):
            assert event.ff_release_images

    @mock.patch('fedfind.release.BranchedNightly.exists', True)
    @mock.patch('fedfind.release.BranchedNightly.all_images', ['foo'])
    def test_candidate_ff_release_nightly(self):
        """Straightforward ff_release test case for a nightly
        compose which exists and has images.
        """
        event = wikitcms.event.NightlyEvent(self.site, '27', 'Branched', '20171104.n.0')
        assert isinstance(event.ff_release, fedfind.release.BranchedNightly)
        assert isinstance(event.ff_release_images, fedfind.release.BranchedNightly)

    @mock.patch('fedfind.release.BranchedNightly.exists', False)
    @mock.patch('fedfind.release.BranchedNightly.all_images', [])
    def test_candidate_ff_release_nightly_no_images(self):
        """ff_release test case for a nightly compose which doesn't
        exist and has no images. We get ff_release (as fedfind doesn't
        do an existence check in this case), but not images.
        """
        event = wikitcms.event.NightlyEvent(self.site, '27', 'Branched', '20171104.n.0')
        assert isinstance(event.ff_release, fedfind.release.BranchedNightly)
        with pytest.raises(FedfindNotFoundError):
            assert event.ff_release_images

@mock.patch('wikitcms.page.mwp.Page.__init__', fakemwpinit)
@mock.patch('wikitcms.page.Page.save', autospec=True)
@mock.patch('wikitcms.page.ValidationPage.update_current', autospec=True)
@mock.patch('wikitcms.event.ValidationEvent.update_current', autospec=True)
@mock.patch('test_event.wk.Wiki.testtypes', ['Installation', 'Base', 'Server', 'Cloud', 'Desktop'])
class TestEventCreate:
    """Tests related to event creation."""
    site = wk.Wiki('fjajah', do_init=False, force_login=False)

    @mock.patch('fedfind.release.BranchedNightly.exists', True)
    @mock.patch('fedfind.release.BranchedNightly.all_images',
                [{
                    'arch': 'x86_64',
                    'format': 'iso',
                    'path': ('Workstation/x86_64/iso/'
                             'Fedora-Workstation-Live-x86_64-27-2011104.n.0.iso'),
                    'subvariant': 'Workstation',
                    'type': 'live',
                    'url': ('https://kojipkgs.fedoraproject.org/compose/branched/'
                            'Fedora-27-20171104.n.0/Workstation/x86_64/iso/'
                            'Fedora-Workstation-Live-x86_64-27-2011104.n.0.iso'),
                }])
    def test_event_create(self, fakeevup, fakepageup, fakepagesave):
        """Test normal event creation."""
        event = wikitcms.event.NightlyEvent(self.site, '27', 'Branched', '20171104.n.0')
        event.create()
        # we should save 5 test pages, plus the summary page,
        # download page and two category pages
        assert fakepagesave.call_count == 9
        # we should call update_current for all 5 test pages
        assert fakepageup.call_count == 5
        # we should call update_current for the event itself
        assert fakeevup.call_count == 1

    @mock.patch('fedfind.release.BranchedNightly.exists', False)
    @mock.patch('fedfind.release.BranchedNightly.all_images', [])
    def test_event_create_no_images(self, fakeevup, fakepageup, fakepagesave):
        """Test event creation where no images are available. This
        should succeed, but not create a download page.
        """
        event = wikitcms.event.NightlyEvent(self.site, '27', 'Branched', '20171104.n.0')
        event.create()
        # we should save 5 test pages, plus the summary page and
        # two category pages - but no download page
        assert fakepagesave.call_count == 8
        # we should call update_current for all 5 test pages
        assert fakepageup.call_count == 5
        # we should call update_current for the event itself
        assert fakeevup.call_count == 1

    @mock.patch('wikitcms.page.mwp.Page.text', return_value="sometext")
    @mock.patch('fedfind.release.BranchedNightly.exists', False)
    @mock.patch('fedfind.release.BranchedNightly.all_images', [])
    def test_event_create_check(self, fakepagetext, fakeevup, fakepageup, fakepagesave):
        """Test event creation when pages already exist and check is
        True. We should raise an error in this case. Using the 'no
        download page' case because the mocks are shorter.
        """
        event = wikitcms.event.NightlyEvent(self.site, '27', 'Branched', '20171104.n.0')
        with pytest.raises(ValueError):
            event.create(check=True)

    @mock.patch('fedfind.release.BranchedNightly.exists', False)
    @mock.patch('fedfind.release.BranchedNightly.all_images', [])
    def test_event_create_testtypes(self, fakeevup, fakepageup, fakepagesave):
        """Test event creation for a specified set of test types."""
        event = wikitcms.event.NightlyEvent(self.site, '27', 'Branched', '20171104.n.0')
        event.create(testtypes=['Installation', 'Server'])
        # we should save 2 test pages, plus the summary page and
        # two category pages - but no download page
        assert fakepagesave.call_count == 5
        # we should call update_current for both test pages
        assert fakepageup.call_count == 2
        # we should call update_current for the event itself
        assert fakeevup.call_count == 1
