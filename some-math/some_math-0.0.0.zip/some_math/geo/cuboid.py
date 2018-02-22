# -*- coding: utf-8 -*-

### imports ###################################################################
import numpy as np

### imports from ##############################################################
from . import isLeft
from .line_segment import LineSegment

###############################################################################
class Cuboid:
    def __init__(self, Pmin = (-1,-1,-1), Pmax = (1,1,1)):
        self.Pmin = np.array(Pmin)
        self.Pmax = np.array(Pmax)
        self.MinMax = [self.Pmin, self.Pmax]
        
        self.vertices = []
        
        for k in range(2):
            for j in range(2):
                for i in range(2):
                    x = self.MinMax[i][0]
                    y = self.MinMax[j][1]
                    z = self.MinMax[k][2]
                    P = np.array([x, y, z])
                    self.vertices.append(P)

        self.edges = []

        ls = LineSegment(self.vertices[0], self.vertices[1])
        self.edges.append(ls)
        
        ls = LineSegment(self.vertices[0], self.vertices[2])
        self.edges.append(ls)

        ls = LineSegment(self.vertices[0], self.vertices[4])
        self.edges.append(ls)

        ls = LineSegment(self.vertices[1], self.vertices[3])
        self.edges.append(ls)

        ls = LineSegment(self.vertices[1], self.vertices[5])
        self.edges.append(ls)

        ls = LineSegment(self.vertices[2], self.vertices[3])
        self.edges.append(ls)

        ls = LineSegment(self.vertices[2], self.vertices[6])
        self.edges.append(ls)

        ls = LineSegment(self.vertices[3], self.vertices[7])
        self.edges.append(ls)

        ls = LineSegment(self.vertices[4], self.vertices[5])
        self.edges.append(ls)

        ls = LineSegment(self.vertices[4], self.vertices[6])
        self.edges.append(ls)

        ls = LineSegment(self.vertices[5], self.vertices[7])
        self.edges.append(ls)

        ls = LineSegment(self.vertices[6], self.vertices[7])
        self.edges.append(ls)


    def planeCut(self, plane):
        cuts = []        
        
        for edge in self.edges:
            Xc = plane.LineSegmentCut(edge)
            
            if Xc is not None:
                cuts.append(Xc)

        Nc = len(cuts)

        if Nc == 0:
            sortedCuts = []
        elif Nc < 4:
            cuts.append(cuts[0])
            sortedCuts = cuts
        else:
            cuts.append(cuts[0])
            sortedCuts = [cuts[0], cuts[1], cuts[2], cuts[0]]

            for ic in range(3, Nc):            
            
                D = cuts[ic]
                Ns = len(sortedCuts)
                
                for i in range(Ns - 1):
                    i1 = i
                    i2 = (i1 + 1) % (Ns - 1)
                    i3 = (i1 + 2) % (Ns - 1)
    
                    right = not isLeft(
                        sortedCuts[i1], sortedCuts[i2], sortedCuts[i3], D
                    )

                    if right:
                        sortedCuts.insert(i+1, D)
                        break

        '''
        if len(cuts) != len(sortedCuts):
            print("DEBUG: unsorted cuts")
            for cut in cuts:
                print(cut)
                
            print("DEBUG: sorted cuts")
            for cut in sortedCuts:
                print(cut)

        print("DEBUG: planeCut finished")
        '''
        
        return np.array(sortedCuts)
