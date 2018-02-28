import pathlib

def Dir(x):
    p = pathlib.Path(x)
    if not p.is_dir():
        raise ValueError('No such directory: %s' % x)
    return p

def File(x):
    p = pathlib.Path(x)
    if not p.is_file():
        raise ValueError('No such file: %s' % x)
    return p
