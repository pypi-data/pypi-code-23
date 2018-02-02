# copyright 2013-2016 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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

import json
import urlparse
import requests

from cubicweb.devtools.httptest import CubicWebServerTC


class RqlIOTC(CubicWebServerTC):

    def setup_database(self):
        with self.admin_access.client_cnx() as cnx:
            self.create_user(cnx, u'toto', password=u'toto')
            cnx.commit()

    def connectedRQLIOSession(self, login='admin', password='gingkow'):
        rsession = requests.Session()
        res = rsession.get('%s?__login=%s&__password=%s' % (
                           self.config['base-url'], login, password))
        self.assertEqual(res.status_code, 200)
        return rsession

    def assertRQLPostOK(self, rsession, queries, code=200):
        url = urlparse.urljoin(self.config['base-url'], 'rqlio/1.0')
        res_ok = rsession.post(url,
                               data=json.dumps(queries),
                               headers={'Content-Type': 'application/json'})
        self.assertEqual(res_ok.status_code, code)
        return res_ok

    def assertRQLPostKO(self, rsession, queries, reason, code=500):
        url = urlparse.urljoin(self.config['base-url'], 'rqlio/1.0')
        res_ko = rsession.post(url,
                               data=json.dumps(queries),
                               headers={'Content-Type': 'application/json'})
        self.assertEqual(res_ko.status_code, code)
        self.assertIn(reason, res_ko.json()[u'reason'])
        return res_ko

    def test_queries(self):
        queries = [('INSERT CWUser U: U login %(l)s, U upassword %(p)s',
                    {'l': 'Babar', 'p': 'cubicweb rulez & 42'}),
                   ('INSERT CWGroup G: G name "pachyderms"', {}),
                   ('SET U in_group G WHERE U eid %(u)s, G eid %(g)s',
                    {'u': '__r0', 'g': '__r1'})]

        # as an anonymous user
        rsession = requests.Session()
        reason = (u'You are not allowed to perform add operation on relation'
                  ' CWUser in_group CWGroup')
        # should really be 403 if it wasn't for cubicweb brokenness
        self.assertRQLPostKO(rsession, queries, reason, code=500)

        # as a standard user
        rsession = self.connectedRQLIOSession('toto', 'toto')
        reason = (u'You are not allowed to perform add operation on relation'
                  ' CWUser in_group CWGroup')
        # should really be 403 if it wasn't for cubicweb brokenness
        self.assertRQLPostKO(rsession, queries, reason, code=500)

        # now, as an admin
        rsession = self.connectedRQLIOSession()
        res = self.assertRQLPostOK(rsession, queries)

        with self.admin_access.client_cnx() as cnx:
            rset = cnx.execute('String N WHERE U in_group G, U login "Babar", '
                               'G name N')
            self.assertEqual('pachyderms', rset.rows[0][0])
        output = [x for x, in res.json()]
        self.assertEqual(1, len(output[0]))
        self.assertEqual(1, len(output[1]))
        self.assertEqual(2, len(output[2]))
        self.assertEqual([output[0][0], output[1][0]], output[2])

    def test_rewrite_args_errors(self):
        rql1 = 'Any U WHERE U login %(l)s'
        rql2 = 'SET U in_group G WHERE G name "managers", U eid %(u)s'
        args2 = {'u': '__r0'}
        # setup test
        rsession = self.connectedRQLIOSession()
        # check ok
        queries_ok = [(rql1, {'l': 'toto'}), (rql2, args2)]
        self.assertRQLPostOK(rsession, queries_ok)
        # check ko (1)
        queries_ko = [(rql1, {'l': 'doesnotexist'}),
                      (rql2, args2)]
        self.assertRQLPostKO(rsession, queries_ko,
                             "__r0 references empty result set")
        # check ko (2)
        queries_ko = [('Any U WHERE U is CWUser', None),
                      (rql2, args2)]
        self.assertRQLPostKO(rsession, queries_ko,
                             "__r0 references multi lines result set")
        # check ko (3)
        queries_ko = [('Any U,L WHERE U login L, U login %(l)s',
                       {'l': 'toto'}), (rql2, args2)]
        self.assertRQLPostKO(rsession, queries_ko,
                             "__r0 references multi column result set")


if __name__ == '__main__':
    import unittest
    unittest.main()
