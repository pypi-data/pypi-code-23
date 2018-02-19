# pylint: disable=W0622
"""cubicweb-skos application packaging information"""


modname = 'cubicweb_skos'
distname = 'cubicweb-skos'

numversion = (1, 3, 0)
version = '.'.join(str(num) for num in numversion)

license = 'LGPL'
author = 'LOGILAB S.A. (Paris, FRANCE)'
author_email = 'contact@logilab.fr'
description = '"SKOS implementation for cubicweb"'
web = 'http://www.cubicweb.org/project/%s' % distname

__depends__ = {
    'cubicweb': '>= 3.24.0',
    'six': '>= 1.4.0',
}
__recommends__ = {
    'rdflib': '>= 4.1',
    'python-librdf': None,
}

classifiers = [
    'Environment :: Web Environment',
    'Framework :: CubicWeb',
    'Programming Language :: Python',
    'Programming Language :: JavaScript',
]
