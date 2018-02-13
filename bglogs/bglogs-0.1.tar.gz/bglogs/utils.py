
def override_dict(a, b, path=None):
    """
    Merge a dictionary (b) into another (a)
    and override any field in a which is also
    present in b

    Args:
        a (dict): the one to be updated
        b (dict): with the values to update
        path:

    """
    if path is None: path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                override_dict(a[key], b[key], path + [str(key)])
            else:
                a[key] = b[key]
                # a.update(b)
                # elif a[key] == b[key]:
                #     pass # same leaf value
                # else:
                #     raise Exception('Conflict at %s' % '.'.join(path + [str(key)]))
        else:
            a[key] = b[key]
    return