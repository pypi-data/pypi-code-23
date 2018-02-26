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

from six import text_type


ARK_MAXIT = 20
ARK_PREFIX = 'rf'
ARK_CONTROLCHAR = 'g'
ARK_NAME_LENGTH = 10
ARK_QUALIFIER_LENGTH = 10

ARK_RGX = re.compile(
    (r'^(ark:/)?(?P<naan>\d+)'
     r'/(?P<name>{prefix}\w{{{length}}}{controlchar})'
     r'(/(?P<qualifier>.{{{qualifier_length}}}))?$').format(
        prefix=ARK_PREFIX,
        length=ARK_NAME_LENGTH - len(ARK_PREFIX) - len(ARK_CONTROLCHAR),
        controlchar=ARK_CONTROLCHAR,
        qualifier_length=ARK_QUALIFIER_LENGTH,
    ),
)

# Regexp for "external" ARK identifiers (i.e. with no length, prefix or
# control character).
EXT_ARK_RGX = re.compile(
    r'^(ark:/)?(?P<naan>\d+)/(?P<name>\w+)(/(?P<qualifier>\w+))?$',
)


def match(string, external=False, **kwargs):
    if external:
        return EXT_ARK_RGX.match(string, **kwargs)
    else:
        return ARK_RGX.match(string, **kwargs)


def generate_ark(cnx, naan):
    """Insert a record in "ark" table with "naan" value, a "name" generated
    and an empty qualifier.

    Return the generated name.
    """
    cu = cnx.system_sql(
        'select * from gen_ark(%s, %s, %s, %s, %s);',
        (naan, ARK_NAME_LENGTH, ARK_PREFIX, ARK_CONTROLCHAR, ARK_MAXIT),
    )
    name, = cu.fetchone()
    return name


def generate_qualified_ark(cnx, naan, name):
    """Insert a record in "ark" table with "naan" and "name" values and a
    "qualifier" generated.

    Return the generated qualifier.
    """
    cu = cnx.system_sql(
        'select * from gen_qualified_ark(%s, %s, %s, %s);',
        (naan, name, ARK_QUALIFIER_LENGTH, ARK_MAXIT),
    )
    qualifier, = cu.fetchone()
    return qualifier


def insert_ark(cnx, naan, name, qualifier=None):
    """Insert a record in "ark" table from specified values."""
    if qualifier is None:
        qs = 'INSERT INTO ark VALUES (%s, %s) RETURNING naan, name, qualifier;'
        values = (naan, name)
    else:
        qs = 'INSERT INTO ark VALUES (%s, %s, %s) RETURNING naan, name, qualifier;'
        values = (naan, name, qualifier)
    (naan, name, qualifier), = cnx.system_sql(qs, values).fetchall()
    ark = u'/'.join([text_type(naan), name])
    if qualifier:
        ark += u'/' + qualifier
    return ark
