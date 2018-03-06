"""cubicweb-celerytask application package

Run and monitor celery tasks
"""

from six import text_type
_ = text_type


class _States(object):
    """ Helper class to create customizable state "lists". Each state is
    accessible as an attribute and the list may be customized by patching the
    resulting object.
    """
    def __init__(self, *args):
        super(_States, self).__init__()
        for arg in args:
            setattr(self, arg, arg)

    def __contains__(self, item):
        return hasattr(self, item)


STATES = _States(_('PENDING'), _('STARTED'), _('SUCCESS'),
                 _('FAILURE'), _('REVOKED'))


FINAL_STATES = _States(_('SUCCESS'), _('FAILURE'), _('REVOKED'))
