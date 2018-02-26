# -*- coding: utf-8 -*-
"""
Created on Tue Jul 19 10:44:54 2016

@author: Trunil
"""
from math import factorial
import numpy as np


def space():
    for i in range(5):
        print('')

def size(array):
    '''array should be numpy array or list of lists'''
    assert len(array) != 0, 'input matrix is empty.'
    n_row = 0
    n_col = 0

    l = len(array[0])
    for r in array:
        assert len(r) == l,'length of all rows does not match'
        n_row += 1
    for c in r:
        n_col += 1

    return n_row,n_col

#a = list(np.array([1,2,3]))
#print(size([a]))

def split_rxn(rxn):
    rxn_split = rxn.split()
    if len(find(rxn_split,'->')) > 0:
        rxn_split.remove('->')
    if len(find(rxn_split,'+')) > 0:
        while '+' in rxn_split:
            rxn_split.remove('+')
    return rxn_split



def nCr(n,r):
    '''http://stackoverflow.com/questions/4941753/is-there-a-math-ncr-function-in-python'''
    f = factorial
    return f(n)/(f(r)*f(n-r))


def find(a,b,exclude=False):
    ''' a = list
        b = item to be found
    '''
    ind = []
    for i in range(len(a)):
        item = a[i]
        if exclude == False:
            if b == item:
                ind.append(i)
        elif exclude == True:
            if b != item:
                ind.append(i)
    return ind

def prod(array):
    '''array = list of lists'''

    ans = []
    for r in array:
        p = 1
        for i in r:
            p = p*i
        ans.append(p)
    return ans

def pause():

    input('\n\nProgram paused. Put cursor in kernel and press enter to continue. ') #for python 3k

def sum_matrix(matrix):
    '''gives sum of elements in a matrix.
    matrix = list of list of numbers'''
    ans = 0
    for rows in matrix:
        for el in rows:
            ans += el

    return ans
