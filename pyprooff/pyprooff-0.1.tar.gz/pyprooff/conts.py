#!/usr/bin/python

"""Concerning Python containers such as dicts, lists, sets."""

from __future__ import print_function

def flatten(seq):
    try:
        if not isinstance(seq, (str, bytes)):
            for item in seq:
                yield from flatten(item)
            return
    except TypeError:
        pass
    yield seq

def combine_small_differences(numbers, max_between, max_contig_range):
    """
    Takes a collection of numbers and returns a dict of clusters within a maximum distance of each other,
    breaking whenever max_contig_range is reached.

    Args:
        numbers: an interable of numbers. If they are not integers, they will be coerced to integers first.
        max_between: the maximum allowable distance between two contiguous numbers within a cluster
        max_contig_range: if a cluster has a total range greater than this value, it will be split when it
                          reaches this value. This is not optimal, but it's computationally east

    Returns:
        dict of {number: new_number}, where new_number is the average within that cluster

    Prints:
        notification of how many times max_total_contig was reached
    """
    import numpy as np
    numbers = [int(x) for x in sorted(list(set(numbers)))]
    # a list of all the number-to-number differences
    diffs2next = [numbers[i+1] - numbers[i] for i in range(len(numbers)-1)]
    diffs2next.append(-1)
    # same list, but change all numbers greater than max_between to 0
    diffs2next_gt0 = [x if x <= max_between else 0 for x in diffs2next]
    # cumulative sum within a contiguous cluster

    def _calc_contig_cumul(d2ngt0):
        n = 0
        contig_cumul = []
        for i, val in enumerate(d2ngt0):
            if i == 0 or val == 0:
                n = 0
            else:
                n += val
            contig_cumul.append(n)
        return contig_cumul

    contig_cumul = _calc_contig_cumul(diffs2next_gt0)

    def calc_min_over(cc):
        a = np.array(cc)
        try:
            min_over = a[a > max_contig_range]
        except ValueError:
            min_over = 0
        return min_over

    min_over = calc_min_over(contig_cumul)

    n_found = 0

    while len(min_over) > 0:
        n_found += 1
        pos = contig_cumul.index(min_over[0])
        diffs2next_gt0[pos] = 0
        contig_cumul = _calc_contig_cumul(diffs2next_gt0)
        min_over = calc_min_over(contig_cumul)
        if n_found > 1000:
            raise Exception('probably in an infinite loop...')

    if n_found > 0:
        print('{} instances found of cluster range > {}'.format(n_found, max_contig_range))

    # go through blocks and average contigs
    n2n = {}
    current_cluster = []
    number_done = False
    for i, (number, contig) in enumerate(zip(numbers, contig_cumul)):
        if i > 0 and contig == 0:
            if len(current_cluster) > 0:
                current_cluster.append(number)
                number_done = True
            for val in current_cluster:
                n2n[val] = int(sum(current_cluster) / len(current_cluster))
            current_cluster = []
        if contig == 0:
            if not number_done:
                n2n[number] = number
            number_done = False
        else:
            current_cluster.append(number)
    for val in current_cluster:
        n2n[val] = int(sum(current_cluster) / len(current_cluster))

    assert(len(numbers)) == len(n2n.keys())

    print(contig_cumul)

    return n2n

def split_list(alist, nchunks=None, chunksize=None):
    """Splits a list into approximately equal sized chunks

    Specify number of chunks or chunksize. If the list items
    do not divide evenly, the last chunk will be differently sized.
    Either nchunks or chunksize must be specified; if both are
    specified, nchunks takes priority.

    Arguments:
        alist {list} -- the list to split into chunks

    Keyword Arguments:
        nchunks {[type]} -- [description] (default: {None})
        chunksize {[type]} -- [description] (default: {None})

    Returns:
        list of lists
    """
    if nchunks is not None:
        import numpy as np
        chunkarr = np.array_split(alist, nchunks)
        return [x.tolist() for x in chunkarr]
    elif chunksize is not None:
        from itertools import islice
        def split_seq(iterable, size):
            it = iter(iterable)
            item = list(islice(it, size))
            while item:
                yield item
                item = list(islice(it, size))
        return [x for x in split_seq(alist, chunksize)]
    else:
        raise Exception("One of nchunks or chunksize must be an integer")

def dicthead(_dict, n=10):
    for i, (k, v) in enumerate(_dict.items()):
        if i == n:
            break
        print('{}: {}'.format(repr(k), repr(v)))


def dicthead_more(_dict, n=10, n2=10, pretty=False, to_stdout=True):
    """Prints the first n items of a dict. If pretty, on separate lines.
    If keys are lists, prints up to n2 items
    If to_stdout = True, prints result, otherwise returns it
    Nested dictionaries are not yet output nicely"""
    from collections import Counter
    i = 0
    output = ['{']
    for k, v in _dict.items():
        i+=1
        if i<=n:
            if type(k) == str:
                output.append("\'{}\'".format(k))
            else:
                output.append(str(k))
            output.append(': ')
            if type(v) == str:
                output.append("\'{}\'".format(v))
            elif type(v) in [list, set]:
                if type(v) == list:
                    # ob, cb = open brackets, closed brackets
                    ob, cb = '[', ']'
                else:
                    ob, cb = '{', '}'
                    listitems = list(v)
                if type(listitems[0]) == str:
                    listitems = ["'{}'".format(x) for x in listitems]
                else:
                    listitems = [str(x) for x in listitems]
                if len(listitems) > n2:
                    output.append(ob+', '.join(
                            listitems[:n2])+"... ({} items total.)".format(
                            len(listitems))+cb)
                else:
                    output.append(ob+', '.join(listitems)+cb)
            else:
                try:
                    dict2 = dict(v)
                    for k2, v2 in dict2.items():
                        output.append('{'+'{}: {}...'.format(k2, v2))
                        break
                except TypeError:
                    output.append(str(v))
            if i != n:
                output.append(", ")
                if pretty:
                    output.append("\n ")
            else:
                output.append(" ...")
                if pretty:
                    output.append("\n")
                else:
                    output.append(" ")
    output.append("({} items total.)".format(i))
    if to_stdout:
        print(''.join(output))
    else:
        return ''.join(output)


def dicthead_most(dict_list, n=3):
    """
    this function recursively prints the element in a possibly nested dictionary
    up to the nth element. The display right now is not pretty, so this could be
    improved.
    """

    #to count down number of elements
    c=n

    #if dict_list is a list
    if type(dict_list).__name__ in ['list','tuple']:

        #print the opening bracket
        if(type(dict_list).__name__=='list'):
            print('[', end='')
        else:
            print('(', end='')

        #for each element, either rerun this process if it's a nestable type,
        # or print the element
        for k in dict_list:
            if(c>0):
                if(type(k).__name__ in ['list','dict', 'tuple']):
                    dicthead_most(k,n)

                else:
                    print(str(k)+',', end='')

            else:
                break

            c-=1


        #if the loop broke because we had too many elements, print elements remaining
        if(c==0):
            print("("+str(len(dict_list)-n)+" left)", end='')

        #closing bracket
        if(type(dict_list).__name__=='list'):
            print(']:', end='')
        else:
            print('):', end='')


    #if dict_list is a dict
    else:

        print("{", end='')

        #for each value key pair, print value/key recursively if it's a nestable type,
        # or print the element directly
        for k in dict_list.items():

            if(c>0):
                #if (type(k[0]).__name__ in ['list', 'dict', 'tuple']):
                #    dicthead3(k[0],n)
                #else:
                print(str(k[0])+":", end='')

                if (type(k[1]).__name__ in ['list', 'dict', 'tuple']):
                    dicthead_most(k[1],n)
                else:
                    print(str(k[1])+" , ", end='')

            else:
                break

            c-=1

        #if loop broke because we had too many elements, print # elements remaining
        if(c==0):
            print("("+str(len(dict_list.items())-n) + " left) ", end='')

        print("}", end='')



def dictdiff(dict1, dict2, show_identical=True, print_output=True, left_name=None, right_name=None,
             lengths_only=False):
    """Determines differences between two dicts

    ARGS:
        dict1, dict2: dicts to compare
        show_identical: if False, will only show differences, not similarities
        print_output: if True, prints results to stdout. If False, returns a descriptive dict
        left_name, right_name: str names for dict1 and dict2, if desired, to identify them in output
        lengths_only: returns number of keys instead of introspecting them (overrides show_identical being False)

    RETURNS:
        None or dict
"""
    def printkv(k, v, left=True):
        """creates a repr of a key and value of a dict entry
           if left is false, prints only the value, with a
           blank for the key"""
        if left:
            krepr = k
        else:
            krepr = ' ' * len(k)
        if type(k) == str:
            if left:
                kapos = "'"
            else:
                kapos = ' '
        else:
            kapos = ''
        if type(v) == str:
            vapos = "'"
        else:
            vapos = ''

        print('{}{}{}{}: {}{}{}'.format('  ',
                                       kapos,
                                       krepr,
                                       kapos,
                                       vapos,
                                       v,
                                       vapos))
    k1 = set(dict1.keys())
    k2 = set(dict2.keys())
    out = {}
    if left_name is None:
        left_name = 'left'
    if right_name is None:
        right_name= 'right'
    if k1 == k2:
        if print_output:
            print("Identical keys in both dicts")
        else:
            out['key_comparison'] = 'same in both dicts'
    else:
        d12 = k1.difference(k2)
        d21 = k2.difference(k1)
        if len(d12) > 0:
            if print_output:
                if not lengths_only:
                    print("Keys in {} only:".format(left_name))
                    for k in d12:
                        printkv(k, dict1[k])
                else:
                    print('{} keys in {} only'.format(len(d12), left_name))
            else:
                if not lengths_only:
                    out['keys_in_{}_only'.format(left_name)] =  {k: dict1[k] for k in d12}
                else:
                    out['keys_in_{}_only'.format(left_name)] = len(d12)
        if len(d21) > 0:
            if print_output:
                if not lengths_only:
                    print("Keys in {} only:".format(right_name))
                    for k in d21:
                        printkv(k, dict2[k])
                else:
                    print('{} keys in {} only'.format(len(d21), right_name))
            else:
                if not lengths_only:
                    out['keys_in_{}_only'.format(right_name)] = {k: dict2[k] for k in d21}
                else:
                    out['keys_in_{}_only'.format(right_name)] = len(d21)

    if not lengths_only:
        first = True
        coll = {}
        found = False
        for k in k1.intersection(k2):
            if dict1[k] != dict2[k]:
                if print_output:
                    if first:
                        print("Different values in {} and {}:".format(left_name, right_name))
                        first = False
                    printkv(k, dict1[k])
                    printkv(k, dict2[k], False)
                else:
                    coll[k] = {left_name: dict1[k], right_name: dict2[k]}
                    found = True
        if found:
            out['same_key_different_values'] = coll

        first = True
        coll = {}
        found = False
        for k in k1.intersection(k2):
            if dict1[k] == dict2[k]:
                if print_output:
                    if first:
                        print("Same values in {} and {}:".format(left_name, right_name))
                        first = False
                    if show_identical:
                        printkv(k, dict1[k])
                    else:
                        print('<omitted>')
                else:
                    coll[k] = dict1[k]
                    found = True
        if found:
            if show_identical:
                out['same_key_same_value'] = coll
            else:
                out['same_key_same_value'] = '<omitted>'

    else:
        n_same = 0
        n_diff = 0
        for k in k1.intersection(k2):
            if dict1[k] == dict2[k]:
                n_same += 1
            else:
                n_diff += 1
        if print_output:
            print("{} keys in both with different values".format(n_diff))
            print("{} keys with same values".format(n_same))
        else:
            out['same_key_different_values'] = n_diff
            out['same_key_same_value'] = n_same

    if not print_output:
        return out


def setdiff(set1, set2, show_identical=True, print_output=True, left_name=None, right_name=None,
           lengths_only=False):
    """Determines differences between two sets

    ARGS:
        set1, set2: sets to compare (will accept lists as well, they will be converted)
        show_identical: if False, will only show differences between the sets, not similarities
        print_output: if True, prints results to stdout. If False, returns a descriptive dict
        left_name, right_name: str names for set1 and set2, if desired.
        lengths_only: returns number of keys instead of introspecting them (overrides show_identical being False)

    RETURNS:
        None or dict

    DOCTEST:
        >>> s1 = {1, 2, 3, 4}
        >>> s2 = {3, 4, 5, 6}
        >>> setdiff(s1, s2, print_output=False, left_name='alpha', right_name='beta')
        {'intersection': [3, 4], 'alpha_only': [1, 2], 'beta_only': [5, 6]}
        >>> setdiff(s1, s2, print_output=False, lengths_only=True)
        {'intersection': 2, 'left_only': 2, 'right_only': 2}
    """
    if left_name is None:
        left_name = 'left'
    if right_name is None:
        right_name = 'right'
    set1 = set(set1)
    set2 = set(set2)
    intersection = sorted(list(set1.intersection(set2)))
    left = sorted(list(set1.difference(set2)))
    right = sorted(list(set2.difference(set1)))

    out = {}
    if len(intersection) == 0:
        if print_output:
            if not lengths_only:
                print('intersection: {} and {} have no members in common')
            else:
                print('intersection: 0')
        else:
            out['intersection'] = 0
    else:
        if not lengths_only:
            if print_output:
                print('intersection:')
                if not show_identical:
                    print('    <omitted {} values>'.format(len(intersection)))
                else:
                    for item in intersection:
                        print('    {}'.format(item))
            else:
                out['intersection'] = intersection
        else:
            if print_output:
                print('intersection: {}'.format(len(intersection)))
            else:
                out['intersection'] = len(intersection)

    for set_, name in [[left, left_name], [right, right_name]]:
        if lengths_only:
            if print_output:
                print('{} only: {}'.format(name, len(set_)))
            else:
                out['{}_only'.format(name)] = len(set_)
        else:
            if print_output:
                print('{} only:'.format(name))
                for item in set_:
                    print('    {}'.format(item))
            else:
                out['{}_only'.format(name)] = set_

    if not print_output:
        return out