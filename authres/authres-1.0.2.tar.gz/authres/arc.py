# coding: utf-8

# Copyright © 2017 Gene Shuman <gene@valimail.com>,
# Copyright © 2012-2013 Scott Kitterman <scott@kitterman.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
authres extension module for the Authenticated Recieved Chain (ARC)
(draft-ietf-dmarc-arc-protocol-08) authentication method.
"""

#MODULE = 'authres'

__author__  = 'Scott Kitterman, Gene Shuman'
__email__   = 'scott@kitterman.com, gene@valimail.com'

import authres.core
from authres.core import make_result_class_properties

class ARCAuthenticationResult(authres.core.AuthenticationResult):
    """
    ARC (draft-ietf-dmarc-arc-protocol-08) result clause of an
    ``Authentication-Results`` header
    Note: Still under development API subject to change."""

    METHOD = 'arc'

    def __init__(self, version = None,
        result               = None,  result_comment               = None,
        reason               = None,  reason_comment               = None,
        properties = None,
        header_ams_d                = None,  header_ams_d_comment                = None,
        header_ams_s                = None,  header_ams_s_comment                = None,
        header_as_d                 = None,  header_as_d_comment                 = None,
        header_as_s                 = None,  header_as_s_comment                 = None,
    ):
        authres.core.AuthenticationResult.__init__(self, self.METHOD, version,
            result, result_comment, reason, reason_comment, properties)
        if header_ams_d:                        self.header_ams_d                    = header_ams_d
        if header_ams_d_comment:                self.header_ams_d_comment            = header_ams_d_comment
        if header_ams_s:                        self.header_ams_s                    = header_ams_s
        if header_ams_s_comment:                self.header_ams_s_comment            = header_ams_s_comment
        if header_as_d:                         self.header_as_d                     = header_as_d
        if header_as_d_comment:                 self.header_as_d_comment             = header_as_d_comment
        if header_as_s:                         self.header_as_s                     = header_as_s
        if header_as_s_comment:                 self.header_as_s_comment             = header_as_s_comment

    header_ams_d,             header_ams_d_comment             = make_result_class_properties('header', 'ams-d')
    header_ams_s,             header_ams_s_comment             = make_result_class_properties('header', 'ams-s')
    header_as_d,              header_ams_d_comment             = make_result_class_properties('header', 'as-d')
    header_as_s,              header_ams_s_comment             = make_result_class_properties('header', 'as-s')

RESULT_CLASSES = [
    ARCAuthenticationResult
]

# vim:sw=4 sts=4
