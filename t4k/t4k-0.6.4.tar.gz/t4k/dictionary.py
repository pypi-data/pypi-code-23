import t4k

def invert_dict(d):
    new_dict = {}
    for key in d:
        new_dict[d[key]] = key

    return new_dict



def max_item(dictionary):
    """
    This conceptually like an argmax function -- it finds the key whose
    corresponding value is the largest in the dictionary.
    """
    the_max = t4k.Max()
    for key, value in dictionary.iteritems(): the_max.add(value, key)
    large_val, large_key = the_max.get()
    return large_key, large_val


def min_item(dictionary):
    """
    This conceptually like an argmax function -- it finds the key whose
    corresponding value is the largest in the dictionary.
    """
    the_min = t4k.Min()
    for key, value in dictionary.iteritems(): the_min.add(value, key)
    large_val, large_key = the_min.get()
    return large_key, large_val


def max_key(dictionary):
    """
    This conceptually like an argmax function -- it finds the key whose
    corresponding value is the largest in the dictionary.
    """
    return max_item(dictionary)[0]


def min_key(dictionary):
    """
    This conceptually like an argmin function -- it finds the key whose
    corresponding value is the smallest in the dictionary.
    """
    return min_item(dictionary)[0]


def max_value(dictionary):
    """
    Returns the maximum value in the dictionary.  Equivalent to
    max(dictionary.values()).
    """
    return max_item(dictionary)[1]


def min_value(dictionary):
    """
    Returns the minimum value in the dictionary.  Equivalent to
    min(dictionary.values()).
    """
    return min_item(dictionary)[1]



def merge_dicts(*dictionaries, **kwargs):
    """
    Merge an arbitrary number of dictionaries, in such a way that values found
    in dictionaries that appear earlier in the parameter list take precedence.

    If the only kwarg ``recursive`` is True, then sub-dictionaries are merged
    in the same way, otherwise a dictionary-valued entries completely overwrite
    one another.
    """
    recursive = kwargs.pop('recursive', True)
    if recursive:
        return merge_dicts_recursive(*dictionaries)
    return merge_dicts_nonrecursive(*dictionaries)


def merge_dicts_nonrecursive(*dictionaries):
    """
    Merge an arbitrary number of dictionaries, in such a way that values found
    in dictionaries that appear earlier in the parameter list take precedence.
    Note that sub-dictionaries are treated as simple values -- the
    sub-dictionary that takes precedence completely overwrites the other(s),
    rather than being recursively merged.
    """
    merged = {}
    for dictionary in reversed(dictionaries):
        merged.update(dictionary)
    return merged


def merge_dicts_recursive(*dictionaries):
    """
    Merge an arbitrary number of dictionaries, in such a way that values found
    in dictionaries that appear earlier in the parameter list take precedence.
    Note that sub-dictionaries are recursively merged in the same way.
    """
    merged = {}
    for dictionary in reversed(dictionaries):
        for key in dictionary:

            # If this key corresponds to a sub-dictionary, both within the
            # merged dict so far and in the current dict to merge in, then we
            # recurse, so that those sub-dicts are merged well 
            both_vals_are_dicts = (
                key in merged and isinstance(merged[key], dict) 
                and isinstance(dictionary[key], dict)
            )

            if both_vals_are_dicts:
                merged[key] = merge_dicts(dictionary[key], merged[key])

            else:
                merged[key] = dictionary[key]

    return merged


def dzip(*dictionaries):
    '''
    Like zip, but for dictionaries.  Produce a dictionary whose keys are 
    given by the intersection of input dictionaries' keys, and whose
    values are are tuples of the input dicts corresponding values.
    '''

    # Define the dzip of no dictionaries to be an empty dictionary
    if len(dictionaries) == 0:
        return {}

    # Get the keys common to all dictionaries
    keys = set(dictionaries[1])
    for d in dictionaries[1:]:
            keys &= set(d)

    # Make the zipped dictionary
    return {
        key : tuple([d.get(key, None) for d in dictionaries])
        for key in keys
    }


def select(dictionary, fields, require=True):
    """
    Create a new dict by copying selected `fields` from the original
    dict `dictionary`.  If `require` is True, then a field that doesn't exist
    in the original dict will cause a KeyError; otherwise it passes over
    missing keys
    silently.
    """
    new_dict = {}
    for field in fields:
        try:
            new_dict[field] = dictionary[field]
        except KeyError:
            if require:
                raise

    return new_dict

