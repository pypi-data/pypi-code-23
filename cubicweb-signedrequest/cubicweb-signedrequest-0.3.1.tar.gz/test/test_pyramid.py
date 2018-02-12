# copyright 2013-2017 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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

from operator import itemgetter
import webtest

from cubicweb.pyramid.test import PyramidCWTest

from cubes.signedrequest import includeme
from cubes.signedrequest.tools import HEADERS_TO_SIGN
from cubes.signedrequest.test import TestController, SignedRequestBaseTC


class PyramidSignedRequestTC(SignedRequestBaseTC, PyramidCWTest):

    settings = {
        'cubicweb.bwcompat': True,
    }

    def includeme(self, config):
        includeme(config)

    def _assert_auth_failed(self, req, result):
        self.assertEqual('INVALID', result)

    def _assert_auth(self, req, result):
        self.assertEqual(200, req.status_int)
        self.assertEqual('VALID', result)

    def _build_string_to_sign(self, request):
        get_headers = itemgetter(*HEADERS_TO_SIGN)
        return (request.method + request.url +
                ''.join(get_headers(request.headers)))

    def _test_header_format(self, method, login, http_method='GET',
                            signature=None, headers=None,
                            content=None, url='/testauth', **params):
        if headers is None:
            headers = {}
        headers = self.get_valid_authdata(headers)
        req = webtest.TestRequest.blank(
            url, base_url=self.config['base-url'].rstrip('/'),
            method=method, headers=headers, **params)
        if http_method == 'POST':
            if content is None:
                content = "rql=Any+X+WHERE+X+is+Player"
        if content:
            req.body = content

        if signature is None:
            string_to_sign = self._build_string_to_sign(req)
            signature = self._build_signature('admin', string_to_sign)

        req.headers['Authorization'] = '%s %s:%s' % (method, login, signature)
        with self.temporary_appobjects(TestController):
            resp = self.webapp.do_request(req)
        return resp.body, resp


if __name__ == "__main__":
    from logilab.common.testlib import unittest_main
    unittest_main()
