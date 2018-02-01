# copyright 2017 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from unittest import TestCase

from mock import MagicMock

from cubicweb_jsonschema.predicates import NoWildcardAcceptPredicate


class NoWildcardAcceptPredicateTC(TestCase):

    def test_one_value(self):
        request = MagicMock()
        request.accept = ['text/html', '*/*']
        p = NoWildcardAcceptPredicate('text/html', None)
        self.assertTrue(p(None, request))
        p = NoWildcardAcceptPredicate('application/json', None)
        self.assertFalse(p(None, request))

    def test_multiple_values(self):
        request = MagicMock()
        request.accept = ['text/html', '*/*']
        p = NoWildcardAcceptPredicate(['text/html', 'application/json'], None)
        self.assertTrue(p(None, request))
        p = NoWildcardAcceptPredicate(
            ['application/json', 'application/octet-stream'], None)
        self.assertFalse(p(None, request))


if __name__ == '__main__':
    import unittest
    unittest.main()
