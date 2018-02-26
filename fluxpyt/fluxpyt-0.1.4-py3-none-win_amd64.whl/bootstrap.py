# -*- coding: utf-8 -*-
"""
Created on Wed Aug 23 12:06:00 2017

@author: Trunil
"""

import numpy as np
import matplotlib.pyplot as plt
import pickle
import pandas as pd


def bootstrap(**kws):
    '''
    inputs:
        kws:
            rxnList: Optional. List of reactions for which bootstrapping is
                     to be done.
                     It should be in form of python list
            ylim = Optional. It should be a tuple. e.g. (0,10).

    Example:
        bootstrap('tca',rxnList=['V01','V02'],ylim=(0,10))
    '''

    np.random.seed(1)  # for reproducibility
    print('\n\n\nBootstrapping...')
    filename = 'flux_std.pckl'

    f = open(filename, 'rb')
    data = pickle.load(f)
    f.close()

    try:
        rxnList = kws['rxnList']
    except:
        rxnList = []
    if len(rxnList) == 0:
        rxnList = data[0]

    d1 = list(data[2])
    d2 = []  # all flux values
    for r in d1:
        r1 = [float(x) for x in r]
        d2.append(r1)

    #%% bootstrap

    file = open('optimization_data.pckl', 'rb')
    obj = pickle.load(file)
    file.close()
    optimal_solution = obj[12]

    file = open('confidence_intervals_bootstrap.csv','w')
    file.write('rxnID,-95% CI,-68% CI,median,+68% CI,+95% CI\n')

    stats1 = []

    rxnIds = data[0]
    rxnInd = [rxnIds.index(x) for x in rxnList]
    ignore = [x for x in range(len(rxnIds)) if x not in rxnInd]

    bootstrap_df = pd.DataFrame({})  # pandas dataframe to store bootstrap data

    for k in range(len(d2)):
        print(k+1, 'of', len(d2))
        if k in rxnInd:
            opt_val = optimal_solution[1][k]
            sel_rxn_vals = d2[k]
            l = len(sel_rxn_vals)
            medians = []
            sixty8_lower = []
            sixty8_upper = []
            ninty5_lower = []
            ninty5_upper = []
            df_list = []  # for making dataframe
            for n in range(1000):
                sample = np.random.choice(sel_rxn_vals, size=l)
                df_list.extend(sample)

                m = np.median(sample)
                medians.append(m)

                ninty5_lower.append(np.percentile(sample, 2.5))  # lower 95ci
                ninty5_upper.append(np.percentile(sample, 97.5))  # upper 95%ci

                sixty8_lower.append(np.percentile(sample, 16))  # lower 68% ci
                sixty8_upper.append(np.percentile(sample, 84))  # upper 68% ci

            # sample_df = pd.DataFrame(df_list,columns=[rxnIds[k]])
            # bootstrap_df = bootstrap_df.append(sample_df,ignore_index=True)
            bootstrap_df[rxnIds[k]] = df_list
        #    min_val_68 = '{:0.2f}'.format(min_val_68)
            file.write(rxnIds[k])
            file.write(',')
            file.write(str('{:0.4f}'.format(np.median(ninty5_lower))))
            file.write(',')
            file.write(str('{:0.4f}'.format(np.median(sixty8_lower))))
            file.write(',')
            file.write(str('{:0.4f}'.format(np.median(medians))))
            file.write(',')
            file.write(str('{:0.4f}'.format(np.median(sixty8_upper))))
            file.write(',')
            file.write(str('{:0.4f}'.format(np.median(ninty5_upper))))
            file.write('\n')

            if k not in ignore:
                item = {}
                item["label"] = rxnIds[k]  # not required
                item["med"] = np.median(medians)
                item["q1"] = np.median(sixty8_lower)
                item["q3"] = np.median(sixty8_upper)
                item["mean"] = opt_val
                item["whislo"] = np.median(ninty5_lower)  # required
                item["whishi"] = np.median(ninty5_upper)  # required
                item["fliers"] = []  # required if showfliers=True
                item['linestyle'] = '-'

                stats1.append(item)

    from operator import itemgetter
    stats1 = sorted(stats1, key=itemgetter('label'))

    print('\n\n', bootstrap_df.head())
    bootstrap_df.to_pickle('bootstrap_dataframe.pckl')

    #%%plot figure

    fig, axes = plt.subplots(1, 1, figsize=(max(len(rxnList) / 2.5, 6), 10))

#    fig = plt.figure(figsize=(8, 6))
#    gs = gridspec.GridSpec(1, 2, width_ratios=[3, 1])
    whiskerprops = dict(linestyle='-', color='k')
    medianprops = dict(color='k', linewidth=0.5)
    boxprops = dict(color='k', linewidth=0.5)

    # first part
    bx1 = axes.bxp(stats1,
                   boxprops=boxprops,
                   whiskerprops=whiskerprops,
                   medianprops=medianprops,
                   patch_artist=True,
                   showmeans=False)
    axes.set_ylabel('Flux values', fontsize=14)

    try:
        ylim = kws['ylim']
        axes.set_ylim(ylim)
    except:
        pass

    # fill with colors
    c1 = '#708090 ' * len(d2)
    colors = c1.split()

    for patch, color in zip(bx1['boxes'], colors):
        patch.set_facecolor(color)

    plt.savefig('monte_carlo_fig.png', format='png', dpi=1000)
    plt.show()

    file.close()
