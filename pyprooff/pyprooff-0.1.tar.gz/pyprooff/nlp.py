#!/usr/bin/python

def loglikely(n1, t1, n2, t2, zerosafe=True, effect_size=False):
    """Calculates Dunning log likelihood ratio of an observation of
    frequency n1 in a corpus of size t1, compared to a frequency n2
    in a corpus of size t2. If result is positive, it is more
    likely to occur in corpus 1, otherwise in corpus 2."""
    from numpy import log  # natural log
    if zerosafe:
        if n1 == 0:
            n1 = 0.5
        if n2 == 0:
            n2 = 0.5
    elif n1 == 0 or n2 == 0:
        return None
    e1 = t1*1.0*(n1+n2)/(t1+t2)  # expected values
    e2 = t2*1.0*(n1+n2)/(t1+t2)
    LL = 2 * ((n1 * log(n1/e1)) + n2 * (log(n2/e2)))
    if n2*1.0/t2 > n1*1.0/t1:
        LL = -LL
    if effect_size:
        denom = (t1 + t2) * log(min(e1, e2))
        return LL / denom
    else:
        return LL

def count_diffs(seq1, seq2, return_text=False):
    """
    Calculates the number of diffs for two sequences.

    Args:
        seq1: list or text that will be changed to list
              with .splitlines()
        seq2: same as seq1
        return_text: if False, returns a dict
                     If True, returns its repr

    Returns:
        dict with keys ('plus', 'minus', 'change',
        'same') and values ints, or text repr

    Note:
        a minus followed by a plus is subsumed into
        one 'change'
    """
    if type(seq1) != list:
        seq1 = seq1.splitlines()
    if type(seq2) != list:
        seq2 = seq2.splitlines()

    import difflib
    d = difflib.Differ()
    diff = d.compare(seq1, seq2)
    difflist = list(diff)
    results = {'plus': 0, 'minus': 0,
               'change': 0, 'same': 0}

    last_was_change = False
    for i, item in enumerate(difflist):
        ch1 = item[0]
        try:
            ch2 = difflist[i+1][0]
        except IndexError:
            ch2 = ' '
        if ch1 == ' ':
            results['same'] += 1
            last_was_change = False
        elif ch1 == '+':
            if last_was_change:
                last_was_change = False
            else:
                results['plus'] += 1
                last_was_change = False
        elif ch1 == '-':
            if ch2 == '+':
                last_was_change = True
                results['change'] += 1
            else:
                results['minus'] += 1
                last_was_change = False

    if return_text:
        return repr(results)
    else:
        return results




