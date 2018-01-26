# pylint: disable=W0622
"""cubicweb-eac application packaging information"""

distname = 'cubicweb-eac'
modname = 'cubicweb_eac'  # required by apycot

numversion = (0, 6, 0)
version = '.'.join(str(num) for num in numversion)

license = 'LGPL'
author = 'LOGILAB S.A. (Paris, FRANCE)'
author_email = 'contact@logilab.fr'
description = 'Implementation of Encoded Archival Context for CubicWeb'
web = 'http://www.cubicweb.org/project/%s' % distname

__depends__ = {
    'cubicweb': '>= 3.24.0',
    'six': '>= 1.4.0',
    'cubicweb-prov': '>= 0.4.0',
    'cubicweb-skos': None,
    'cubicweb-addressbook': None,
    'cubicweb-compound': '>= 0.6.0',
    'python-dateutil': None,
}
__recommends__ = {}

classifiers = [
    'Environment :: Web Environment',
    'Framework :: CubicWeb',
    'Programming Language :: Python',
    'Programming Language :: JavaScript',
]
