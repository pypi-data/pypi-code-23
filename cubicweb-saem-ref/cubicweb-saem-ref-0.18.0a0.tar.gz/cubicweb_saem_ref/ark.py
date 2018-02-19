# copyright 2018 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.
"""cubicweb-saem-ref utilities for ARK identifiers"""

import re


ARK_PREFIX = 'rf'
ARK_CONTROLCHAR = 'g'
ARK_NAME_LENGTH = 10
ARK_QUALIFIER_LENGTH = 10

ARK_RGX = re.compile(
    r'^(ark:/)?(?P<naan>\d+)/(?P<name>{prefix}\w{{{length}}}{controlchar})$'.format(
        prefix=ARK_PREFIX,
        length=ARK_NAME_LENGTH - len(ARK_PREFIX) - len(ARK_CONTROLCHAR),
        controlchar=ARK_CONTROLCHAR,
    ),
)


match = ARK_RGX.match


def generate_ark(cnx, naan):
    """Insert a record in "ark" table with "naan" value, a "name" generated
    and an empty qualifier.

    Return the generated name.
    """
    cu = cnx.system_sql(
        'select * from gen_ark(%s, %s, %s, %s);',
        (naan, ARK_NAME_LENGTH, ARK_PREFIX, ARK_CONTROLCHAR),
    )
    name, = cu.fetchone()
    return name


def generate_qualified_ark(cnx, naan, name):
    """Insert a record in "ark" table with "naan" and "name" values and a
    "qualifier" generated.

    Return the generated qualifier.
    """
    cu = cnx.system_sql(
        'select * from gen_qualified_ark(%s, %s, %s);',
        (naan, name, ARK_QUALIFIER_LENGTH),
    )
    qualifier, = cu.fetchone()
    return qualifier
