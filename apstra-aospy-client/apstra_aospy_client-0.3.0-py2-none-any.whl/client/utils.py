# Copyright 2014-present, Apstra, Inc. All rights reserved.
#
# This source code is licensed under End User License Agreement found in the
# LICENSE file at http://www.apstra.com/eula

import six
import socket
import datetime
import operator
import time
from itertools import chain

if six.PY2:
    from itertools import imap
else:
    imap = map
    from functools import reduce


def probe(host, port, timeout=5, intvtimeout=1):
    start = datetime.datetime.now()
    end = start + datetime.timedelta(seconds=timeout)

    while datetime.datetime.now() < end:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(intvtimeout)
        try:
            s.connect((host, port))
            s.shutdown(socket.SHUT_RDWR)
            s.close()
            return True
        except socket.error:
            time.sleep(1)
            pass
    else:
        # elapsed = datetime.datetime.now() - start
        return False


def itemgetter(item):
    path = item.split('.')

    def wrapper(obj):
        try:
            return reduce(operator.getitem, path, obj)
        except KeyError:
            return None
    return wrapper


def iter_items_by_key(items, item_key, items_key='items'):
    """
    Have you ever wanted to go through a list of dict-items,
    and then extact a specific key from each dict-item?  This
    function does this, and return an iterator that you can
    then loop through.  This is great if you need to "flatten"
    a list-of-lists type data structure.

    Parameters
    ----------
    items : dict
        A dict, such that items[items_key] returns a list-of-dict
        items.

    item_key : str
        The key-name of the list-of-dict items you want to extract

    items_key : str
        defaults to "items" because most API calls return this;
        but some do not, so you can override the value.

    Returns
    -------
    Iterator
    """
    return chain.from_iterable(         # return 'flattened' iterator
        imap(itemgetter(item_key),      # get each key from the item-dict
             items[items_key]))         # across each list item
