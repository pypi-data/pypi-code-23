# -*- coding: utf-8 -*-
"""
Created on Sun Jan 28 13:22:16 2018

@author: jaredmt
"""

'''===========string functions=============='''

def newlines(st,n):
    '''this takes a string and separates it with new lines
    every n characters. example:
        newlines("thisisatest",5)=
        "thisi\nsates\nt"
    '''
    
    b=""
    pos = strfind("\n",st)
    if pos[0]<0:#no "\n" found
        L=int(len(st)/n)
        for i in range(L+1):
            if i<(L):
                b=b+st[i*n:i*n+n]+"\n"
            else:
                b=b+st[i*n:]
    else:
        if pos[0]>0:
            b=b+newlines(st[0:pos[0]],n)+"\n"
            b=b+newlines(st[pos[0]+1:],n)
        else:
            b=b+newlines(st[1:],n)#eliminate newline at beginning
    if strfind("\n",b)[-1]==len(b)-1:
        b=b[:-1]#eliminate newline at the end
    return b

def strfind(sst,st):
    ''' find all positions of sst(substring) in st (string)'''
    pos=[[]]
    a=0
    pos[0]=st.find(sst)
    if pos[0]<0:
        return pos
    while pos[a]>-1:
        a=a+1
        pos.append(st.find(sst,pos[a-1]+1))
    pos.remove(-1)#if sst is found, no -1 should be in pos
    return pos

def strspace(str1,spacesize):
    '''returns str1 but with minimum length of spacesize
    by filling in extra characters with spaces'''
    if len(str1)>spacesize:
        error("str1 is larger than spacesize")
    lower = " "*int((spacesize-len(str1))*.5)
    higher=" "*ceil((spacesize-len(str1))*.5)
    str1=lower+str1+higher
    return str1

