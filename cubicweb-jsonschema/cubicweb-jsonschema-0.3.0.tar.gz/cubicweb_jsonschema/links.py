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

"""cubicweb-jsonschema HTTP Link header utils"""

import re

from webob.multidict import MultiDict


def serialize_links(link_dict):
    """Serialize link_dict into a Link Header
    compliant string as defined by RFC 5988
    """
    ldos = []
    for rel, links in link_dict.dict_of_lists().items():
        for link in links:
            link['rel'] = rel
            href = link.pop('href')
            params = '; '.join(['{}="{}"'.format(k, v)
                               for k, v in sorted(link.items())])
            ldos.append({"href": href, "params": params})
    ldos.sort(key=lambda ldo: (ldo["href"], ldo["params"]))
    return ', '.join(['<{href}>; {params}'.format(**ldo) for ldo in ldos])


def _split_unquotted(delimiter, string):
    r"""Split a string using using 'delimiter' as separator
    when it does not split a quoted string:

    >>> _split_unquotted(',', 'a,"b,c",d')
    ['a', '"b,c"', 'd']

    A quoted string can contain an escaped quote:

    >>> _split_unquotted(',', r'"a","\"b,\""')
    ['"a"', '"\\"b,\\""']
    """
    # Match any quoted string
    # even quoted strings which contain escaped quotes
    quoted_string = r'"(?:\\.|[^"\\])*"'
    # Match any string which does not contain an unquotted delimiter
    parts_regex = r'((?:[^"{delim}]+|{quoted_string})+)'.format(
        delim=delimiter,
        quoted_string=quoted_string)
    return [val for val in re.findall(parts_regex, string)]


def parse_links(link_header):
    r"""Parse a link header and generate a MultiDict

    This function generates a MultiDict of links
    by parsing a 'Link' header's value:

    >>> from pprint import pprint
    >>> link_header = (
    ...     '</A>;rel="a";type="application/json",'
    ...     '<B1>;rel="b";type="text/xml",'
    ...     '<B2>;rel="b";type="text/xml"'
    ... )
    >>> links = parse_links(link_header)
    >>> pprint(links.getone('a'))
    {'href': '/A', 'type': 'application/json'}
    >>> pprint(links.getall('b'))
    [{'href': 'B1', 'type': 'text/xml'}, {'href': 'B2', 'type': 'text/xml'}]

    This implementation allows spaces between links and between parameters:

    >>> links = parse_links('</A>; rel="a" ,</B> ;rel="b" ;  type="text/plain"')
    >>> pprint(links.dict_of_lists())
    {'a': [{'href': '/A'}], 'b': [{'href': '/B', 'type': 'text/plain'}]}

    It's possible to quote parameter values...

    >>> links = parse_links('</X>; rel="foo,bar"')
    >>> pprint(links.dict_of_lists())
    {'foo,bar': [{'href': '/X'}]}

    ...and to escape quotes in quoted values:

    >>> links = parse_links('</X>; title="The \"quotation\"" ; rel="related"')
    >>> pprint(links.dict_of_lists())
    {'related': [{'href': '/X', 'title': 'The "quotation"'}]}

    If a parameter is present and has no value specified, its default value
    will be True:

    >>> links = parse_links('</X>; use_modal; rel="next"')
    >>> pprint(links.dict_of_lists())
    {'next': [{'href': '/X', 'use_modal': True}]}

    Link values with several relations can also be parsed:

    >>> links = parse_links('</X>; rel="a b c"')
    >>> pprint(links.dict_of_lists())
    {'a': [{'href': '/X'}], 'b': [{'href': '/X'}], 'c': [{'href': '/X'}]}
    """

    links = MultiDict()
    for link_value in _split_unquotted(',', link_header):
        # link_value looks like '<THE_HREF>; parm="val1 val2"; parm=val3; parm4'
        href, params = re.search('^\s*<([^>]+)>\s*;(.*)$', link_value).groups()
        link = {'href': href}
        for param in _split_unquotted(';', params):
            param = param.strip()
            try:
                # expect the parameter to be a key/value pair
                key, value = _split_unquotted('=', param)
            except ValueError:
                # the parameter has no value specified
                key = param
                value = True
            else:
                value = value.strip()
                # remove quotes if the value is a quoted string
                if value[0] == '"':
                    value = value[1:-1]

            link[key] = value
        for rel in link.pop('rel').split(' '):
            links.add(rel, link)
    return links
