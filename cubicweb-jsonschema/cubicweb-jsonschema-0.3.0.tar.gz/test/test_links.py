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

"""cubicweb-jsonschema unit tests for HTTP Link header utils"""

import doctest
from unittest import TestCase
from webob.multidict import MultiDict

from cubicweb_jsonschema.links import (serialize_links,
                                       parse_links)


class LinkHeaderTest(TestCase):

    def test_serialize(self):
        links = MultiDict()
        links.add('describedby', {'href': 'LINK1'})
        links.add('describedby', {'href': 'LINK2'})
        links['up'] = {'href': 'LINK3'}

        expected = ('<LINK1>; rel="describedby", '
                    '<LINK2>; rel="describedby", '
                    '<LINK3>; rel="up"')
        self.assertEqual(serialize_links(links), expected)

    def test_parse(self):
        link_header = ('<LINK1>; rel="describedby",'
                       '<LINK2> ; rel="describedby" ,'
                       '<LINK3>;    rel="up" ')

        links = MultiDict()
        links.add('describedby', {'href': 'LINK1'})
        links.add('describedby', {'href': 'LINK2'})
        links['up'] = {'href': 'LINK3'}

        self.assertEqual(parse_links(link_header), links)


def load_tests(loader, tests, ignore):
    tests.addTests(
        doctest.DocTestSuite('cubicweb_jsonschema.links')
    )
    return tests


if __name__ == '__main__':
    import unittest
    unittest.main()
