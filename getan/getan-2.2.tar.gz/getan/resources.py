import gettext as py_gettext
import os

_base_dir = os.path.join(os.path.dirname(__file__), os.pardir)
share_dir = os.path.join(_base_dir, "share")


def gettext(message):
    modir = os.path.join(share_dir, "locale")
    t = py_gettext.translation("getan", modir, fallback=True)

    return t.ugettext(message)
