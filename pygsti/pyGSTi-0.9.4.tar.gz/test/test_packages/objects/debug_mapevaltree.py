from __future__ import print_function
import pygsti
from pygsti.objects.gatemapcalc import GateMapCalc
import numpy as np

def assertArraysAlmostEqual(a,b):
    assert(np.linalg.norm(a-b) < 1e-6)

mgateset = pygsti.construction.build_gateset(
    [2], [('Q0',)],['Gi','Gx','Gy'],
    [ "I(Q0)","X(pi/8,Q0)", "Y(pi/8,Q0)"])
mgateset._calcClass = GateMapCalc

gatestring1 = ('Gx','Gy')
gatestring2 = ('Gx','Gy','Gy')
gatestring3 = ('Gx',)
gatestring4 = ('Gy','Gy')
#mevt,mlookup,moutcome_lookup = mgateset.bulk_evaltree( [gatestring1,gatestring2] )
#mevt,mlookup,moutcome_lookup = mgateset.bulk_evaltree( [gatestring1,gatestring4] )
mevt,mlookup,moutcome_lookup = mgateset.bulk_evaltree( [gatestring1,gatestring2,gatestring3,gatestring4] )
print("Tree = ",mevt)
print("Cache size = ",mevt.cache_size())
print("lookup = ",mlookup)
print()

mevt_split = mevt.copy()
print("Tree copy = ",mevt_split)
print("Cache size = ",mevt_split.cache_size())
print("Eval order = ",mevt_split.get_evaluation_order())
print("Num final = ",mevt_split.num_final_strings())

print()

mevt_squeeze = mevt.copy()
mevt_squeeze.squeeze(1)
print("Squeezed Tree = ",mevt_squeeze)
print("Cache size = ",mevt_squeeze.cache_size())
print("Eval order = ",mevt_squeeze.get_evaluation_order())
print("Num final = ",mevt_squeeze.num_final_strings())

print()

mlookup_splt = mevt_split.split(mlookup,numSubTrees=4)
print("Split tree = ",mevt_split)
print("Cache size = ",mevt_split.cache_size())
print("Eval order = ",mevt_split.get_evaluation_order())
print("Num final = ",mevt_split.num_final_strings())
print("new lookup = ",mlookup_splt)
print()

subtrees = mevt_split.get_sub_trees()
print("%d subtrees" % len(subtrees))
for i,subtree in enumerate(subtrees):
    print("Sub tree %d = " % i,subtree,
          " csize = ",subtree.cache_size(),
          " eval = ",subtree.get_evaluation_order(),
          " nfinal = ",subtree.num_final_strings())
    

probs = np.zeros( mevt.num_final_elements(), 'd')
mgateset.bulk_fill_probs(probs, mevt)
print("probs = ",probs)
print("lookup = ",mlookup)

squeezed_probs = np.zeros( mevt_squeeze.num_final_elements(), 'd')
mgateset.bulk_fill_probs(squeezed_probs, mevt_squeeze)
print("squeezed probs = ",squeezed_probs)
print("lookup = ",mlookup)

split_probs = np.zeros( mevt_split.num_final_elements(), 'd')
mgateset.bulk_fill_probs(split_probs, mevt_split)
print("split probs = ",split_probs)
print("lookup = ",mlookup_splt)


#evt_split = mevt.copy()
#new_lookup = mevt_split.split(lookup, numSubTrees=2)
#print("SPLIT TREE: new elIndices = ",new_lookup)
#probs_to_fill = np.empty( mevt_split.num_final_elements(), 'd')
#mgateset.bulk_fill_probs(probs_to_fill,mevt_split,check=True)

print("DONE")
