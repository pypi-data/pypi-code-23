"""Dictionaries assigning Wilson coefficients to classes and sectors,
needed to construct appropriate vectors."""

from collections import defaultdict


def listdict():
    return defaultdict(list)


sectors = defaultdict(listdict)


# class 1
for qq in ['sb', 'db', 'ds']:
    if qq == 'ds':
        sname = 'sdsd'
    else:
        sname = 2 * qq  # e.g. sbsb
    sectors[sname]['I'].append(['{}{}'.format(i, 2 * qq)
                                for i in ['1', '2', '3', '4', '5', '1p', '2p', '3p']])


# class 2
for qq in ['cb', 'ub', 'us', 'cs', 'cd', 'ud']:
    for l in ['e', 'mu', 'tau']:
        for lp in ['e', 'mu', 'tau']:
            sname = qq + l + 'nu'  # e.g. cbenu
            sectors[sname]['II'].append(['{}{}'.format(i, qq + l + lp)
                                         for i in ['1', '5', '1p', '5p', '7p']])

# class 3
for dd in ['sb', 'db', 'ds']:
    for uu in ['uc', 'cu']:
        if dd == 'ds':
            sname = 'sd' + uu[::-1]  # e.g. dsuc -> sdcu
        else:
            sname = dd + uu  # e.g. sbuc
        for p in ['', 'p']:
            sectors[sname]['III'].append(['{}{}{}'.format(i, p, dd + uu)
                                          for i in range(1, 11)])

# class 4
for qq in ['sbsd', 'dbds']:
    for p in ['', 'p']:
        sectors[qq]['IV'].append(['{}{}{}'.format(i, p, qq)
                                  for i in range(1, 11, 2)])


qqdict = {
'sb': ['uu', 'dd', 'cc', 'ss', 'bb'],
'db': ['uu', 'ss', 'cc', 'dd', 'bb'],
'ds': ['uu', 'bb', 'cc', 'dd', 'ss'],
}
# class 5
for qq in ['sb', 'db', 'ds']:
    if qq == 'ds':
        sname = 'sd'
    else:
        sname = qq
    for p in ['', 'p']:
        _C = []
        for pp in qqdict[qq]:
            if pp[0] in qq:
                _C += ['{}{}{}{}'.format(i, p, qq, pp)
                       for i in range(1, 11, 2)]  # 1, 3, 5, 7, 9
            else:
                _C += ['{}{}{}{}'.format(i, p, qq, pp)
                       for i in range(1, 11)]  # 1, 2, ..., 10
        _C += ['7{}gamma{}'.format(p, qq),
               '8{}g{}'.format(p, qq)]
        for l in ['e', 'mu', 'tau']:
            # e.g. 1sbee
            _C += ['{}{}{}{}'.format(i, p, qq, 2 * l)
                   for i in range(1, 11, 2)]  # 1, 3, 5, 7, 9
        sectors[sname]['V' + qq].append(_C)

# class 5b
for qq in ['sb', 'db', 'ds']:
    for l in ['e', 'mu', 'tau']:
        for lp in ['e', 'mu', 'tau']:
            if l != lp:
                if qq == 'ds':
                    sname = 'sd' + lp + l
                else:
                    sname = qq + l + lp
                for p in ['', 'p']:
                    sectors[sname]['Vb'].append(['{}{}{}'.format(i, p,  qq + l + lp)
                                                 for i in range(1, 11, 2)])

# class 5nu
for qq in ['sb', 'db', 'ds']:
        for p in ['', 'p']:
            if qq == 'ds':
                sname = 'sdnunu'
            else:
                sname = qq + 'nunu'
            sectors[sname]['Vnu'].append(['nu1{}{}{}{}'.format(p, qq, l, lp)
                                         for l in ['e', 'mu', 'tau']
                                         for lp in ['e', 'mu', 'tau']])
