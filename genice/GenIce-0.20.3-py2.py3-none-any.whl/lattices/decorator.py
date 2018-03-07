#!/usr/bin/env python3

#convert a 4-network into FAU-like supernetwork

import networkx as nx
from collections import defaultdict
import sys
from genice.formats.baseclass import shortest_distance
from genice import pairlist as pl


def decorate1(atoms, cell, pair, Ncyl, nei):
    i,j = pair
    dij = atoms[j] - atoms[i]
    dij -= np.floor(dij + 0.5)
    dij /= np.linalg.norm(dij)
    sixvecs = []
    for k in nei[i]:
        if k != j:
            vec = atoms[k] - atoms[i]
            vec -= np.floor(vec + 0.5)
            shadow = np.dot(dij, vec)
            vec -= shadow*dij
            print(np.dot(vec,dij))
            sys.exit(0)

    
def decorate(atoms, cell, pairs, Ncyl):
    """
    Ncyl is the number of cylinders to be inserted (>0)
    """
    #make netghbor list
    nei = defaultdict(set)
    for i,j in pairs:
        nei[i].add(j)
        nei[j].add(i)
    for pair in pairs:
        decorate1(atoms, cell, pair, Ncyl, nei)

def main():
    #read O positions
    cell, atoms = LoadGRO(sys.stdin)
    #build the network
    dmin = shortest_distance(atoms, cell)
    pairs = [v for v in pl.pairlist_crude(atoms, dmin*1.3, cell, distance=False)]
    #decorate
    newatoms = decorate(atoms, cell, pairs, Ncyl)
    
