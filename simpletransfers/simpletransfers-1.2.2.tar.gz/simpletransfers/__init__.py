from __future__ import absolute_import, print_function, unicode_literals
"""
A set of classes that provide operations to
get files or put files to or from somewhere,
usually a network resource.

All these classes implement a get and put method,
for, well, getting and putting data.
"""
class TransferException( Exception ):
    pass

from .local import local
from .ftp import ftp
try:
    from .sftp import sftp
except ImportError:
    print('Install paramiko for SFTP support')
from .mail import mail
try:
    from .http_client import http_client
except ImportError:
    print('Install requests for HTTP client support')
try:
    from .http_server import http_server
except ImportError:
    print('Install Flask for HTTP server support')
from .zip import zipfile
try:
    from .soap import soap
except ImportError:
    print('Install suds for SOAP support')
