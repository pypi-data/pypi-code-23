def merge(*dicts):

    def _merge(dict1, dict2):
        for k in set(dict1.keys()).union(dict2.keys()):
            if k in dict1 and k in dict2:
                if isinstance(dict1[k], dict) and isinstance(dict2[k], dict):
                    yield (k, dict(merge(dict1[k], dict2[k])))
                else:
                    # If one of the values is not a dict, you can't continue merging it.
                    # Value from second dict overrides one in first and we move on.
                    yield (k, dict2[k])
            elif k in dict1:
                yield (k, dict1[k])
            else:
                yield (k, dict2[k])


    result = dict()
    for index, d in reversed(list(enumerate(dicts))):
        if not result:
            result = dict(_merge(dicts[index-1], d))
        result = dict(_merge(dicts[index-1], result))

    return dict(result)



if __name__ == '__main__':
    a = {'a': 1, 'b': 2}
    b = {'b': 3, 'c': {'c1': 4, 'c2': 3}}
    c = {'a': 3, 'c': {'c1': 3 }}    
    print(merge(a,b,c))