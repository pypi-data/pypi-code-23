#!/usr/bin/python
from __future__ import print_function, division
from __future__ import unicode_literals, absolute_import

def jaro_similarity(first, second, winkler=True, winkler_ajustment=True, scaling=0.1):
    """
    :param first: word to calculate distance for
    :param second: word to calculate distance with
    :param winkler: same as winkler_ajustment
    :param winkler_ajustment: add an adjustment factor to the Jaro of the distance
    :param scaling: scaling factor for the Winkler adjustment
    :return: Jaro distance adjusted (or not)
    """
    import math
    def _score(first, second):
        shorter, longer = first.lower(), second.lower()

        if len(first) > len(second):
            longer, shorter = shorter, longer

        m1 = _get_matching_characters(shorter, longer)
        m2 = _get_matching_characters(longer, shorter)

        if len(m1) == 0 or len(m2) == 0:
            return 0.0

        return (float(len(m1)) / len(shorter) +
                float(len(m2)) / len(longer) +
                float(len(m1) - _transpositions(m1, m2)) / len(m1)) / 3.0

    def _get_diff_index(first, second):
        if first == second:
            return -1

        if not first or not second:
            return 0

        max_len = min(len(first), len(second))
        for i in range(0, max_len):
            if not first[i] == second[i]:
                return i

        return max_len

    def _get_prefix(first, second):
        if not first or not second:
            return ""

        index = _get_diff_index(first, second)
        if index == -1:
            return first

        elif index == 0:
            return ""

        else:
            return first[0:index]

    def _get_matching_characters(first, second):
        common = []
        limit = math.floor(min(len(first), len(second)) / 2)

        for i, l in enumerate(first):
            left, right = int(max(0, i - limit)), int(min(i + limit + 1, len(second)))
            if l in second[left:right]:
                common.append(l)
                second = second[0:second.index(l)] + '*' + second[second.index(l) + 1:]

        return ''.join(common)

    def _transpositions(first, second):
        return math.floor(len([(f, s) for f, s in zip(first, second) if not f == s]) / 2.0)

    class JaroDistanceException(Exception):
        def __init__(self, message):
            super(Exception, self).__init__(message)

    ### starts here

    if not first or not second:
        raise JaroDistanceException("Cannot calculate distance from NoneType ({0}, {1})".format(
            first.__class__.__name__,
            second.__class__.__name__))

    jaro = _score(first, second)
    cl = min(len(_get_prefix(first, second)), 4)

    if all([winkler, winkler_ajustment]):  # 0.1 as scaling factor
        return round((jaro + (scaling * cl * (1.0 - jaro))) * 100.0) / 100.0

    return jaro

def find_closest_match(item, group, similarity_function='SequenceMatcher_0',
                       allow_identity=False):
    """Finds closest match(es) to item in group based on similarity function.

    Args:
        item: the item which will be compared to each member of group
        group: a collection of members to be compared to item
        similarity_function: any function that returns a higher number when
            items are more similar. It should take just two positional arguments,
            the two items to be compared, and order of these items should not
            matter. As a convenience, this arg can take the strings
            "SequenceMatcher_0", "...1" or "...2" which will apply the difflib
            SequenceMatcher to the items, returnint the ratio, quick_ratio or
            really_quick_ratio, respectively. Note that really_quick_ratio is
            very forgiving of differences and is probably only appropriate for
            quite long sequences
        allow_identity: will not score a group member if it is identical to an
            item. Useful if you are finding full similarity matches for every
            member of a group within that group, for example.

    Returns: tuple of:
        - list of first-place match group members. If there are no ties, this list
          will have only one member
        - similarity score, the output of the similarity function for that
          item and member.
    """
    import numpy as np
    if similarity_function in ['SequenceMatcher_0', 'SequenceMatcher_1', 'SequenceMatcher_2']:
        quickness = similarity_function[-1]
        from difflib import SequenceMatcher
        def similarity_function(a, b):
            if quickness == '0':
                return SequenceMatcher(None, a, b).ratio()
            elif quickness == '1':
                return SequenceMatcher(None, a, b).quick_ratio()
            else:
                return SequenceMatcher(None, a, b).real_quick_ratio()
    scores = []
    for member in group:
        # check for identity first
        if not allow_identity and item == member:
            score = -np.inf
        else:
            score = similarity_function(item, member)
        scores.append(score)
    scores = np.array(scores)
    mask = scores == scores.max()
    return list(np.array(group)[mask]), scores.max()

def pairwise_distance_matrix(items, function):
    """Creates an square distance matrix of items given a function.

    Args:
        items: an iterable of items
        function: a function that takes two arguments in the first position without arg names;
                  the rest of the args will be default. If need be, def a wrapper or use a lambda.
                  the function must be symmetrical, i.e. function(a, b) == function(b, a)

    Returns:
        numpy array containing distances
    """
    import numpy as np
    output = np.empty([len(items), len(items)])
    for i in range(len(items)):
        for j in range(i, len(items)):
            dist = function(items[i], items[j])
            output[i, j] = dist
            output[j, i] = dist
    return output

def group_similarities(items, similarity_function, cutoff, return_similarities=False, countdown_interval=None):
    """Creates groups of similar items according to a similarity function.

    :param: items : an iterable of items
    :param: similarity_function: a function that takes two items (unordered) as input and outputs a scalar
    :param: cutoff: scalar above which grouping happens
    :param: return_similarities: if True, returns similarity dict, does not make groups
    :countdown_Interval: if not None, how many items go by for a countdown

    :returns: nested list of groups containing all items"""

    # ensure items are unique
    assert len(items) == len(set(items))
    assert not any([x is None for x in items])
    similarities = {}  # takes tuple as key
    if countdown_interval is not None:
        print('calculating similarities: ', end='')
        countdown = len(items) // countdown_interval
    for i in range(len(items) - 1):
        if countdown_interval is not None:
            if (i + 1) % countdown_interval == 0:
                print(countdown, end=' ')
                countdown -= 1
        for j in range(i + 1, len(items)):
            similarities[(items[i], items[j])] = similarity_function(items[i], items[j])
    if countdown_interval is not None:
        print('making groups: ', end='')
        countdown = len(items) // countdown_interval
    groups = []

    remaining = items[:]

    while len(remaining) > 0:
        queue = [remaining[0]]
        to_analyze = remaining[1:]
        this_group = []
        while len(queue) > 0:
            comparator = queue[0]
            queue = queue[1:]
            analyzed = []
            for item in to_analyze:
                if similarity_function(comparator, item) >= cutoff:
                    queue.append(item)
                else:
                    analyzed.append(item)
            to_analyze = analyzed[:]
            this_group.append(comparator)
        groups.append(this_group)
        for item in this_group:
            remaining.remove(item)