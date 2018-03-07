# -*- coding:utf-8 -*- 
__author__ = 'denishuang'


def distrib_count(d, a):
    a = str(a)
    counts = d.setdefault('counts', {})
    percents = d.setdefault('percents', {})
    counts[a] = counts.setdefault(a, 0) + 1
    tc = sum(counts.values())
    cas = [(int(k), v) for k, v in counts.iteritems()]
    cas.sort()
    s = 0
    for k, v in cas:
        s += v
        percents[str(k)] = s / float(tc)
    d['count'] = tc
    return d