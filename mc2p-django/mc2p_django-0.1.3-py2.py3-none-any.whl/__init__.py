from mc2p import MC2PClient as MC2PClientPython


__title__ = 'MyChoice2Pay Django'
__version__ = '0.1.3'
__author__ = 'MyChoice2Pay'
__license__ = 'BSD 2-Clause'
__copyright__ = 'Copyright 2017 MyChoice2Pay'

# Version synonym
VERSION = __version__

# Header encoding (see RFC5987)
HTTP_HEADER_ENCODING = 'iso-8859-1'

# Default datetime input and output formats
ISO_8601 = 'iso-8601'

default_app_config = 'django_mc2p.apps.DjangoMC2PConfig'


class MC2PClient(MC2PClientPython):
    """
    Wrapper of MC2PClient of Python
    """
    def __init__(self):
        """
        Initializes a MC2PClient getting key and secret key from DB
        """
        from .models import MC2PConfig

        try:
            mc2p_config = MC2PConfig.objects.get()
            key = mc2p_config.key
            secret_key = mc2p_config.secret_key
        except:
            key = ''
            secret_key = ''
        super(MC2PClient, self).__init__(key, secret_key)
