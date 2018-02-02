# -*- coding: utf-8 -*-
"""
Created on Sun Jan 28 13:20:47 2018

@author: jaredmt

@description: all list functions
"""

'''===========List functions=============='''
'''
list manipulation: append, insert, remove, index, count, sort, 
'''
def mxnlist(m,n):
    '''creates a blank nested list of size mxn
    (m rows and n columns)'''
    A = [[[] for _ in range(n)] for __ in range(m)]
    return A

def listisnull(A):
    #returns true if entire list is null
    from pandas import isnull
    return isnull(A).all()


def nestedlist(*M):
    '''makes a multi-dimensional list of M dimensions
    example:
        nestedlist(2,2,2)
        = [[[[], []], [[], []]], [[[], []], [[], []]]]
        = 2x2x2 nested list
        or...
        nestedlist([2,2,2])#output same as above
    note: input may be multiple integer inputs or single list input
        '''
    if len(M)>1:#more than 1 arg: convert to list
        M=list(M)
    else:#int or list. only care about 1st & only value
        M=M[0]
        
    if type(M)==type(1):#if M is integer
        A=[[]]*M
    elif type(M[0])==type([]):
        #print("M cannot be a nested list")
        return "error: M cannot be a nested list"
    elif len(M)>1:
        A=[[]]*M[0]
        for i in range(M[0]):
            A[i]=nestedlist(M[1:])
    else:#M must be list of length 1
        A=[[]]*M[0]
    return A


def listflatten(A):
    '''flattens a nested list to a list vector'''
    m=len(A)
    K=[]
    B=[]
    for i in range(m):
        if type(A[i])==type([]) and len(A[i])>1:
            B=listflatten(A[i])
            for j in range(len(B)):
                K.append(B[j])
            
        else:
            K.append(A[i])
    return K

def nestedziplist(a):
    '''this function is similar to list(zip(a,b,c))
    where a,b,c are 3 argument lists of the same size. 
    nestedziplist gives the same output for input [a,b,c]
    in other words: it takes a nested list input rather than several inputs
    example:
        nestedziplist([[1,2,3],[4,5,6]])
        =[(1, 4), (2, 5), (3, 6)]
        '''
    b=mxnlist(len(a[0]),len(a))
    for i in range(len(a)):
        for j in range(len(a[0])):
            b[j][i]=a[i][j]
    for k in range(len(b)):
        b[k]=tuple(b[k])
    return b

def recursiveadd(a,i=0):
    '''simply a test/example for recursive add
    this funcion counts how many times it calls itself
    note that it uses an optional argument i by giving it a default value of 1
    '''
    if a<100:
        a=recursiveadd(a+1,i+1)
    else:
        return i
    return a

def listsize(A):
    '''not done yet'''
    for i in range(len(A)):
        if type(A[i])==type([]) and len(A[i])>1:
                A=1