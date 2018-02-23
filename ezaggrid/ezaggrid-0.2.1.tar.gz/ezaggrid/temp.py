def mklbl(prefix, n):
    return ["%s%s" % (prefix, i) for i in range(n)]

miindex = pd.MultiIndex.from_product([mklbl('A', 4),
                                      mklbl('B', 2),
                                      mklbl('C', 4),
                                      mklbl('D', 2)])
index  =[' '.join(col).strip() for col in miindex.values]
micolumns = pd.MultiIndex.from_tuples([('a', 'foo'),
                                       ('a', 'bar'),
                                       ('b', 'foo'),
                                       ('b', 'bah')],
                                      names=['lvl0', 'lvl1'])
cols  =[' '.join(col).strip() for col in micolumns.values]

dfrc = pd.DataFrame(np.arange(len(miindex) * len(micolumns)).reshape((len(miindex),
                                                                    len(micolumns))),
                  index=miindex,
                  columns=micolumns).sort_index().sort_index(axis=1)
dfr = pd.DataFrame(np.arange(len(miindex) * len(micolumns)).reshape((len(miindex),
                                                                    len(micolumns))),
                  index=miindex,
                  columns=cols).sort_index().sort_index(axis=1)
dfc = pd.DataFrame(np.arange(len(miindex) * len(micolumns)).reshape((len(miindex),
                                                                    len(micolumns))),
                  index=index,
                  columns=micolumns).sort_index().sort_index(axis=1)


