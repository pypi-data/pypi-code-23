# -*- coding: utf-8 -*-
"""
Generate correction vector for a given natural isotope distribution vector and number of atomic elements.
    iDist = isotope_dist = isotopomer distribution vector of the atom
    ele = num_atom = number of elements of the same atom
Similar to corr_vect = cVectGen(iDist, ele) in openFLux  by  Lake-Ee Quek, AIBN
Created on Mon Jul 18 16:44:48 2016

@author: Trunil
"""
import numpy as np

from fluxpyt.utility import size,nCr,find,prod
from scipy.signal import convolve

#import sys


def mid_vec_gen(iDist,ele=0):
    #similar to cVectGen in openflux

    if ele == 0:
        corr_vect = []


    if ele == 1:
         corr_vect = iDist
         if size([corr_vect]) == 1:
             corr_vect = corr_vect

#         print('corr_vect is as follows:')
#         for a in corr_vect:
#             print(round(a,4))

         return corr_vect

    if len(iDist) == 2:
        p = iDist[0]
        q = iDist[1]
        corr_vect = []
        for count in range(ele+1):

            corr_vect.append(nCr(ele,count) * p**(ele-count) * q**(count) )

#        print('corr_vect is as follows:')
#        for a in corr_vect:
#            print(round(a,4))

        return corr_vect



    no = len(iDist)
    start_comb = []
    for i in range(ele):
        start_comb.append(0)
    start_comb = np.array([start_comb])
    cont = 1

    comb_store = start_comb

    count = 0


    while cont == 1:


        comb_ini = np.copy(comb_store[-1])

        comb_ini[ele-1] = comb_ini[ele-1]+1

        if comb_ini[ele-1] == no:

            i = ele-1

            while i >= 0:

                if comb_ini[i] < no-1:
                    comb_ini[i] = comb_ini[i] + 1
                    comb_ini[i+1::] = 0

                    break

                if i == 0:
                    cont = 0

                i -= 1

        if cont == 1:


            comb_store = np.vstack((comb_store,comb_ini))


        count += 1

    sum_vect = sum_row(comb_store)
#    print('sum_vect',sum_vect)

    corr_vect = []

#    print('sum_vect',sum_vect)
    tmp = []
    p = 0
    for i in range(min(sum_vect),max(sum_vect)+1):

        hit = find(sum_vect,i)

        sum_prob = 0

        for j in range(len(hit)):
            sub_comb_store = comb_store[hit[j]]
#            print('sub_comb_store',sub_comb_store)

            p += len(sub_comb_store)
            sub_iDist = [iDist[k] for k in sub_comb_store]


            sum_prob = sum_prob + prod([sub_iDist])[0]

        corr_vect.append(sum_prob)

#    print('corr_vect is as follows:')
#    for a in corr_vect:
#        print(round(a,4))

    return corr_vect


def mid_round(vector):
    v = []
    for n in vector:
        v.append(round(n,4))
    return v
def sum_row(matrix):
    s = []
    for r in matrix:
        s.append(sum(r))
    return s



def test():
    nat = [0.9893, 0.0107]
    lab = [0.01,0.99]
    a = [x*0.99 for x in convolve(lab,mid_vec_gen(nat,2))]
    b = [x*0.01 for x in mid_vec_gen(nat,3)]
    c = [x+y for x,y in zip(a,b)]
#    print(a,'\n',c)
    d = [x-y for x,y in zip(c,a)]
    d = mid_vec_gen(lab,2)
    print(d)

#test()
