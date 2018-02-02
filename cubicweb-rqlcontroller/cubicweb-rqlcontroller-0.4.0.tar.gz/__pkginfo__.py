# pylint: disable=W0622
"""cubicweb-rqlcontroller application packaging information"""

from os.path import join
from glob import glob


modname = 'rqlcontroller'
distname = 'cubicweb-rqlcontroller'

numversion = (0, 4, 0)
version = '.'.join(str(num) for num in numversion)

license = 'LGPL'
author = 'LOGILAB S.A. (Paris, FRANCE)'
author_email = 'contact@logilab.fr'
description = 'restfull rql edition capabilities'
web = 'http://www.cubicweb.org/project/%s' % distname

__depends__ = {
    'cubicweb': '>= 3.19.0',
    'six': None,
}
__recommends__ = {'cubicweb-signedrequest': None}

classifiers = [
    'Environment :: Web Environment',
    'Framework :: CubicWeb',
    'Programming Language :: Python',
    'Programming Language :: JavaScript',
]

THIS_CUBE_DIR = join('share', 'cubicweb', 'cubes', modname)


data_files = [
    # common files
    [THIS_CUBE_DIR, [fname for fname in glob('*.py') if fname != 'setup.py']],
]
