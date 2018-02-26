# coding: utf-8
# pylint: disable=W0622
"""cubicweb-saem-ref application packaging information"""

distname = 'cubicweb-saem-ref'
modname = 'cubicweb_saem_ref'

numversion = (0, 18, 0)
version = '.'.join(str(num) for num in numversion)

license = 'LGPL'
author = 'LOGILAB S.A. (Paris, FRANCE)'
author_email = 'contact@logilab.fr'
description = "Référenciel de Système d'Archivage Électronique Mutualisé"
web = 'http://www.cubicweb.org/project/%s' % distname

__depends__ = {
    'cubicweb[pyramid]': '>= 3.26.1',
    'cubicweb-squareui': None,
    'cubicweb-eac': '>= 0.6.0, < 0.7.0',
    'cubicweb-seda': '>= 0.13.2, < 0.14.0',
    'cubicweb-compound': '>= 0.7.0, < 0.8.0',
    'cubicweb-prov': '>= 0.4.0, < 0.5.0',
    'cubicweb-oaipmh': '>= 0.4.2, < 0.5.0',
    'cubicweb-relationwidget': '>= 0.4.0, < 0.5.0',
    'cubicweb-skos': '>= 1.3.0',
    'cubicweb-vtimeline': None,
    'cubicweb-signedrequest': None,
    'isodate': None,
    'python-dateutil': None,
    'pytz': None,
    'psycopg2': None,
    'rdflib': '>= 4.1',
}
__recommends__ = {}

classifiers = [
    'Environment :: Web Environment',
    'Framework :: CubicWeb',
    'Programming Language :: Python',
    'Programming Language :: JavaScript',
]
