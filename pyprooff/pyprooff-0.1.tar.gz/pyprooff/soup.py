#!/usr/bin/python

def get_parent_tree(node):
    parents = []
    curr = node
    while True:
        curr = curr.parent
        if curr.name != u'[document]':
            parents.append(curr.name)
        else:
            break
    return parents[::-1]

def parsed_tree(soup):
    import pandas as pd
    import numpy as np
    coll = []
    for item in soup.findAll():
        this = {}
        tree = get_parent_tree(item)
        this['_num_parents'] = len(tree)
        this['_parents'] = '|'.join(tree)
        this['_tag'] = item.name
        if item.string is not None:
            this['_string'] = item.string
        else:
            this['_string'] = np.nan
        for k, v in item.attrs.items():
            this[k] = v
        coll.append(this)
    return pd.DataFrame(coll)
