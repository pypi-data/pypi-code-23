#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np

def blockAverage(data, nblocks):
    # size = len(data)
    blocks = []
    for blockId in xrange(nblocks):
        a = []
        size = len(data)
        if size <= 2:
            break
        for i in range(1, int(size/2)):
            a.append( np.average(data[2*i-1:2*i]) )
        a = np.array(a)
        blocks.append(np.average(a))
        obs = np.var(a)/(size-1)
        print blockId, size, np.average(a), np.std(a), np.var(a), obs
        data = a
    return (np.average(blocks), np.std(blocks))

