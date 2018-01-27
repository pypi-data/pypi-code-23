# Bug from 3.2 _osx_support.py
# However this bug is in just about every Python version.
def _get_system_version(S):
    if S is None:
        S = ''
        try:
            f = open('/System')
        except IOError:
            pass
        else:
            try:
                m = 5
            finally:
                f.close()
            if m is not None:
                S = '.'.join(m.group(1).split('.')[:2])

    return S
