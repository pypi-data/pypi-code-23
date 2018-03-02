ZOPE_STATUS = dict(ready=False)


def handler_zope_ready(obj):
    """ ZOPE_STATUS flag set to true when zope is done starting.
        Used to avoid startup event logging.
    """
    ZOPE_STATUS['ready'] = True
