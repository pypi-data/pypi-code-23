from typing import List, Union  # NOQA


def _ensure_rowids_are_real_ints(rowids):
    # numpy int64s aren't JSON serializable, even though they look like
    # ints in pretty much every other way. Convert them. Yes, this also
    # casts strings, but if they successfully cast, so be it.
    return [int(r) for r in rowids]


def rowids_from_arg(rowids):
    # type: (List[int]) -> Union[str, List[int]]
    """Return `rowids` if non-None or the 'all' selector if None."""
    # Ask yourself, is `pd.Index([97, 108, 108]) == 'all'`? That is why we call
    # `isinstance`.
    if rowids is None or (isinstance(rowids, str) and rowids == 'all'):
        return 'all'
    else:
        return _ensure_rowids_are_real_ints(rowids)
