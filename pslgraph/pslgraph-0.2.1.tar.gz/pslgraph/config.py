D3M_API_VERSION = '2018.1.5'
VERSION = '0.2.0'
TAG_NAME = ''

REPOSITORY = 'https://gitlab.datadrivendiscovery.org/dhartnett/psl'
PACAKGE_NAME = 'pslgraph'

# D3M_PERFORMER_TEAM = 'SRI-UCSC'
D3M_PERFORMER_TEAM = 'SRI'

PACKAGE_URI = ''
if TAG_NAME:
    PACKAGE_URI = "git+%s@%s" % (REPOSITORY, TAG_NAME)
else:
    PACKAGE_URI = "git+%s" % (REPOSITORY)

PACKAGE_URI = "%s#egg=%s" % (PACKAGE_URI, PACAKGE_NAME)

INSTALLATION_TYPE = 'GIT'
if INSTALLATION_TYPE == 'PYPI':
    INSTALLATION = {
        'type' : 'PIP',
        'package': PACAKGE_NAME,
        'version': VERSION
    }
else:
    # INSTALLATION_TYPE == 'GIT'
    INSTALLATION = {
        'type' : 'PIP',
        'package_uri': PACKAGE_URI,
    }
