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
"""cubicweb-jsonschema permissions tests"""

from cubicweb.pyramid.test import PyramidCWTest


class PermissionsTests(PyramidCWTest):

    settings = {
        'cubicweb.bwcompat': False,
        'pyramid.debug_notfound': True,
        'cubicweb.auth.authtkt.session.secret': 'x',
        'cubicweb.auth.authtkt.persistent.secret': 'x',
        'cubicweb.session.secret': 'x',
    }

    def includeme(self, config):
        config.include('cubicweb_jsonschema.api')
        # Disable anonymous-user from Pyramid side (the user still exists, but
        # we make it hidden from Pyramid) so that, without an explicit login,
        # the request is unauthenticated (instead of authenticated with an
        # "anon" user).
        del config.registry['cubicweb.anonymous_eid']

    def test_anon(self):
        self.login('anon', 'anon')
        self.webapp.get('/cwuser', status=200,
                        headers={'Accept': 'application/json'})

    def test_user(self):
        self.login()
        self.webapp.get('/cwuser', status=200,
                        headers={'Accept': 'application/json'})

    def test_nobody(self):
        for path in [
                '/',
                '/schema',
                '/cwuser',
                '/cwuser/987',  # does not exist, but still 403
                '/cwuser/schema',
        ]:
            if path.endswith('/schema'):
                mtype = 'application/schema+json'
            else:
                mtype = 'application/json'
            with self.subTest(path=path):
                self.webapp.get(path, status=403,
                                headers={'Accept': mtype})


if __name__ == '__main__':
    import unittest
    unittest.main()
