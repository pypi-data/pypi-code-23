import importlib

import pytz


def import_dotted_path(path):
    """
    Return the module or name at `path`.
    """
    parts = path.split('.')
    args = []
    found = None

    for l in range(1, len(parts)):
        iterpath = '.'.join(parts[:l])
        attr = parts[l]
        args.append((iterpath, attr))

    for path, attr in args:
        try:
            found = importlib.import_module(path)
        except ImportError:
            pass

        if hasattr(found, attr):
            found = getattr(found, attr)

    if found is None:
        raise ImportError('Cannot import %s', path)

    return found


def datetime_to_utc_timestamp(dt):
    if dt.tzinfo != pytz.utc:
        raise ValueError('datetime must have tzinfo set to UTC')
    return dt.timestamp()
