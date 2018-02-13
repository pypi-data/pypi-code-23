"""
Authenticaton related utilities
"""


def require_signin(*conditions):
    """
    A decorator that appends conditions to the authentication.require config
    variable.
    """
    def decorate(f):
        if not hasattr(f, '_cp_config'):
            f._cp_config = dict()
        if 'authentication.require' not in f._cp_config:
            f._cp_config['authentication.require'] = []
        f._cp_config['authentication.require'].extend(conditions)
        return f
    return decorate


def any_of(*conditions):
    """
    Returns True if any of the conditions match
    """
    def check():
        for c in conditions:
            if c():
                return True
        return False
    return check


def all_of(*conditions):
    """
    Returns True if all of the conditions match

    By default all conditions are required, but this might still be
    needed if you want to use it inside of an any_of(...) condition
    """
    def check():
        for c in conditions:
            if not c():
                return False
        return True
    return check
