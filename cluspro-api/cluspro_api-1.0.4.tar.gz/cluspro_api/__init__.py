from __future__ import absolute_import
import logging

from .config import get_config
from .version import version

from path import Path

import hmac as _hmac
import hashlib as _hashlib

__version__ = version

CONFIG = get_config()
PRMS_DIR = Path(CONFIG['prms_dir'])

logging.getLogger(__name__).addHandler(logging.NullHandler())

def make_sig(form, secret):
    sig = ""
    for k in sorted(form.keys()):
        if form[k] is not None:
            sig += "{}{}".format(k, form[k])
    return _hmac.new(
        secret.encode('utf-8'), sig.encode('utf-8'), _hashlib.md5).hexdigest()
