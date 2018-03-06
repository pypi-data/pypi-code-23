"""Welcome to the Python client library for Steno3D!

This library is used to construct 3D projects and upload them to
steno3d.com - if you do not have an account you can go to
steno3d.com/signup and sign up. You will also need to request a developer
API key at steno3d.com/settings/developer. Online documentation for this
python client is found at steno3d.com/docs.

Steno3D is built with tab-completion in mind; if you are in an
interacitve environment such as a Jupyter Notebook it is easy to explore
the base namespace and seek additional documentation and help.

If you would like to get started with some example resources,
`from steno3d import examples`
should provide a few pre-made examples to look at.

When you are ready to upload your project to steno3d.com, then
`steno3d.login()`
and provide your developer API key.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from atexit import register

from . import parsers
from . import query
from . import client
from .base import (
    FileSizeLimitExceeded,
    ProjectQuotaExceeded,
    ProjectResourceLimitExceeded,
    ProjectSizeLimitExceeded,
    ResourceSizeError,
    UploadError,
)
from .project import *
from .data import *
from .line import *
from .point import *
from .surface import *
from .texture import *
from .vector import *
from .volume import *

__version__ = '0.3.6'
__author__ = 'Seequent'
__license__ = 'MIT'
__copyright__ = 'Copyright 2018 Seequent'

login = client.Comms.login
logout = client.Comms.logout
user = client.Comms.user
# register(logout)

try:
    del project, data, line, point, surface, texture, props, volume
    del base, client, options
    del absolute_import, division, print_function, unicode_literals
    del register
except NameError:
    # Error cleaning namespace
    pass
