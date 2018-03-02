__author__ = 'Maxim Dutkin (max@dutkin.ru)'


def dict_reorder(item: dict) -> dict:
    """
    Sorts dict by keys, including nested dicts
    :param item: dict to sort
    """
    if isinstance(item, dict):
        item = {k: item[k] for k in sorted(item.keys())}
        for k, v in item.items():
            if isinstance(v, dict):
                item[k] = dict_reorder(v)
    return item
