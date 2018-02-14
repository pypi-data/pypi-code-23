"""
Module imported and name resolver.

Heavily based on mock's ``patch`` decorator's implementation.
"""


from __future__ import absolute_import, unicode_literals


def _dot_lookup(thing, comp, import_path):
    try:
        return getattr(thing, comp)
    except AttributeError:
        __import__(import_path)
        return getattr(thing, comp)


def find(target):
    """
    Import modules and return the desired object.

    Takes a fully qualified name in argument, like ``'os.path.join'``.
    In that case, loads the `os` module using ``__import__``, then returns
    ``os.path.join`` using ``getattr``. It would then try to import ``os.path``
    if that failed.
    """
    components = target.split('.')
    import_path = components.pop(0)
    thing = __import__(import_path)

    for comp in components:
        import_path += ".%s" % comp
        thing = _dot_lookup(thing, comp, import_path)
    return thing
