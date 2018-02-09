#!/usr/bin/python

# Generate all sudoku grids of a given rank 
# MIT License
# Copyright 2018 (c) George Carder 2018

################################################
# A set of functions contributing to the task of
# generating all sudoku grids of a given rank.
################################################
# Use and Examples:
#
# B=buildAndFinalizeAll(3) gives a list B where
# each entry is a distinct 9x9 sudoku grid with
# entries from set of symbols {1,2,..,9}
#
# B=buildAllBoards(3) gives a list B where each
# entry is a distinct 9x9 sudoku grid with
# entries from set of symbols 
# {[0,0],[1,0],..,[2,2]} i.e. the image
# of addition Z_3xZ_3 with Z_3xZ_3
#
# B=buildStandardBoard(3) gives a single 
# sudoku grid with entries as the previous
# example but the grid configuration arises
# from "standard" ordering of domain wrt
# addition.
#
# buildboard(gen1,gen2,d) builds a sudoku
# grid given generating lists and rank d
#
# buildGenerators(d) gives a pair of 
# 'standard' generators for a given
# rank d
#
# factorial.. we all know what that is..
# factorial(d) gives the unary operator
# d!
#
# boardFinalizer(board,d) takes a board
# with rank d and entries the image 
# of addition (Z_nxZ_n)x(Z_nxZ_n)
# and converts the entries in a well-
# defined way to elements of 
# {1,2,..,n^2}
################################################
################################################

from itertools import permutations

def buildAndFinalizeAll(d):
    B=buildAllBoards(d)
    F=[]
    for b in B:
        F.append(boardFinalizer(b,d))
    ### here put Aut(n). revision for v0.2.0
    P=list(permutations(range(1,d**2+1)))
    FF=[]
    for r in range(factorial(d**2)):
        for f in F:
            N=[]
            for i in range(d**2):
                for j in range(d**2):
                    N.append(P[r][f[j+i*(d**2)]-1])
            FF.append(N)
    return FF 

def factorial(n): 
    if n==1:
        return 1
    else:
        return n*factorial(n-1)

def buildGenerators(d): 
    # called by buildAllBoards and buildStandarBoard
    gen1=[]
    gen2=[]
    for i in range(d):
        for j in range(d):
            gen1.append([j%d,i%d])
            gen2.append([i%d,j%d])
    return [gen1,gen2]

def permuteGenerator(gen,d):  
    # called by buildAllBoards
    f=factorial(d)
    P=list(permutations(range(1,d+1)))
    ALLGEN=[] # will have d*f rows... (d*d)*d*f length
    for i in range(d):
        for p in range(f):
            toPermute=gen[i*d:(i+1)*d]
            permuted=[]
            for j in range(d):
                permuted.append(toPermute[P[p][j]-1])
            genPermuted=gen[0:(d*d)]
            genPermuted[i*d:(i+1)*d]=permuted
            if (i==0) or (i>0 and p>0):
                ALLGEN.append(genPermuted)
    return ALLGEN

def buildStandardBoard(d): 
    dd=d*d
    gen=buildGenerators(d)
    gen1=gen[0] 
    gen2=gen[1]
    l=dd*dd
    B=[]
    for i in range(dd):
        for j in range(dd):
            B.append(list(map(lambda x,y: (x+y)%d,gen1[i],gen2[j])))
    return B

def buildAllBoards(d): 
    dd=d*d
    gen=buildGenerators(d)
    gen1=gen[0]
    gen2=gen[1]
    allgen1=permuteGenerator(gen1,d)
    allgen2=permuteGenerator(gen2,d)
    BOARDS=[]
    for gen1 in allgen1:
        for gen2 in allgen2:
            board=buildboard(gen1,gen2,d)
            BOARDS.append(board)
    return BOARDS


def buildboard(gen1,gen2,d): 
    # called by buildAllBoards
    dd=d*d
    board=[]
    for i in range(dd):
      for j in range(dd):
        board.append(list(map(lambda x,y: (x+y)%d,gen1[i],gen2[j])))
    return board

def boardFinalizer(board,d):
    gen=buildGenerators(d)
    FinalBoard=[]
    for b in board:
        FinalBoard.append(gen[0].index(b)+1)
    return FinalBoard

