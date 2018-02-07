import re


NUMERIC_CHARS = set("0123456789.")

NUMERIC_CHARS_BYTES = set(b"0123456789.")


def robust_float(s):
    """
    Convert a given value into a float.

    :param s: a string, int, float, or other
    :return: a float of the given value, or None if not possible.
    """
    if isinstance(s, (int, float)):
        return float(s)
    elif isinstance(s, str):
        try:
            return float("".join(c for c in s if c in NUMERIC_CHARS))
        except ValueError:
            return None
    elif isinstance(s, bytes):
        try:
            return float(b"".join(c for c in s if c in NUMERIC_CHARS_BYTES))
        except ValueError:
            return None
    else:
        return None


def robust_int(s):
    """
    Convert a given value into a int.

    :param s: a string, int, float, or other
    :return: a int of the given value, or None if not possible.
    """
    x = robust_float(s)
    return x if x is None else int(x) 


def rename_ks(d, mapping, must_exist=False):
    """
    Rename the keys in a given dictionary.

    :param d: the dict to update
    :param mapping: a dict of old_key -> new_key pairs
    """
    for k_old, k_new in mapping.items():
        key_exists = k_old in d
        if key_exists:
            d[k_new] = d[k_old]
            del d[k_old]
        elif must_exist:
            assert key_exists, "Key {} not in {}".format(k_old, d)


PYTHONIZE_IDENTIFIER_RE = re.compile('[^0-9a-z]+')


def pythonize_identifier(s, delete_chars=None):
    if delete_chars:
        for c in delete_chars:
            s = s.replace(c, '')

    s = PYTHONIZE_IDENTIFIER_RE.sub('_', s.lower())
    if s and s[0] == '_':
        s = s[1:]
    if s and s[-1] == '_':
        s = s[:-1]
    return s


def pythonize_ks(d, recursive=True, delete_chars=None):
    remapping = {}
    for k, v in d.items():
        pythonized = pythonize_identifier(k, delete_chars)
        if pythonized != k:
            remapping[k] = pythonized

        if recursive:
            if isinstance(v, dict):
                pythonize_ks(v)

    rename_ks(d, remapping)


def fill_in_unknowns(src_doc, dst_doc):
    """
    Recursively update dst_doc with items from the src_doc if it doesn't exist.

    :param src_doc: a dict with sub-documents
    :param dst_doc: a dict with sub-documents
    """
    for k, v in src_doc.items():
        if isinstance(v, dict):
            if k in dst_doc:
                assert isinstance(dst_doc[k], dict)
            else:
                dst_doc[k] = {}
            fill_in_unknowns(v, dst_doc[k])
        else:
            if k not in dst_doc:
                dst_doc[k] = v


def update_values(d, ks, converter, must_exist):
    for k in ks:
        key_exists = k in d
        if key_exists:
            d[k] = converter(d[k])
        elif must_exist:
            assert key_exists, "Key {} not in {}".format(k, d)


def dict_values_to_int(d, ks=None, must_exist=False, robust=True):
    """
    Convert values of a dict to ints for some keys.

    :param d: a dict
    :param ks: an iterable of keys
    :param must_exist: raises an exception if set to True and the given key
        does not exist in the given dict
    """
    f = robust_int if robust else int
    update_values(d, ks or d.keys(), f, must_exist)


def dict_values_to_float(d, ks=None, must_exist=False, robust=True):
    """
    Convert values of a dict to floats for some keys.

    :param d: a dict
    :param ks: an iterable of keys
    :param must_exist: raises an exception if set to True and the given key
        does not exist in the given dict
    """
    f = robust_float if robust else int
    update_values(d, ks or d.keys(), f, must_exist)


def dict_values_to_upper_if_str(d):
    for k, v in d.items():
        if isinstance(v, str):
            d[k] = v.upper()


COMMON_BOOL_TRUE = set(['yes', 'true', 'y', 't', '1'])
COMMON_BOOL_FALSE = set(['no', 'false', 'n', 'f', '0'])


def str_to_bool(s, true_set=COMMON_BOOL_TRUE, false_set=COMMON_BOOL_FALSE):
    """
    Convert a given string to a boolean value.

    :param s: a boolean value represented as a string
    :param true_set: a set of (all-lowercase) values indicating true
    :param false_set: a set of (all-lowercase) values indicating false
    :return: True if the value is in `true_set`, False if it is in `false_set`
        otherwise `None`
    """
    if isinstance(s, str):
        s = s.lower()
        if s in true_set:
            return True
        elif s in false_set:
            return False

    return None


def dict_string_values_to_bool(d, ks, true_set=None, false_set=None,
                               must_exist=False):
    """
    Convert values of a dict to floats for some keys.

    :param d: a dict
    :param ks: an iterable of keys
    :param must_exist: raises an exception if set to True and the given key
        does not exist in the given dict
    """
    true_set = true_set or COMMON_BOOL_TRUE
    false_set = false_set or COMMON_BOOL_FALSE

    def f(s):
        return str_to_bool(s, true_set, false_set)
    update_values(d, ks, f, must_exist)


WHITESPACE_RE = re.compile("\s+")


def sstrip(s):
    """
    :param s: a string
    :return: a new string with prefix and postfix spacing removed, and all
        all spacing converted to single spacing
    """
    return WHITESPACE_RE.sub(' ', s).strip()


def update_items_in_place(items, conversion):
    for i, item in enumerate(items):
        items[i] = conversion(item)


def sstrip_all(items):
    """
    Applying sstrip to items, updating in-place.
    """
    update_items_in_place(items, sstrip)


def flat_mapping_of_dict(d, sep='_', prefix=''):
    """
    Return a copy of d, recursively unpacking all dicts.

    Note: This assumes all keys are strings!

    :param d: a dict
    :param sep: the prefix to a key
    :param prefix: the prefix to keys in this dict
    :return: a new dict
    """
    new_d = {}
    for k, v in d.items():
        k = prefix + sep + str(k) if prefix else str(k)

        if isinstance(v, dict):
            new_d.update(flat_mapping_of_dict(v, sep=sep, prefix=k))
        else:
            new_d[k] = v
    return new_d


def remove_private_keys(d, recursive=True, prefix='_'):
    ks = []

    for k, v in d.items():
        if k.startswith(prefix):
            ks.append(k)

        if isinstance(v, dict):
            remove_private_keys(v, recursive, prefix)

    for k in ks:
        del d[k]


def reindex_columns_partial(df, cols):
    """
    Reorder a DataFrame so that the given columns come first.

    :param df: The DataFrame to reorder
    :param cols: The columns which should come first, in order.
    :return df: The reindex DataFrame
    """
    cols = list(cols)

    ordering = cols[:]
    for c in df.columns:
        if c in cols:
            cols.remove(c)
        else:
            ordering.append(c)

    if cols:
        raise KeyError("Unable to find keys: {}".format(",".join(cols)))

    return df.reindex(columns=ordering)
