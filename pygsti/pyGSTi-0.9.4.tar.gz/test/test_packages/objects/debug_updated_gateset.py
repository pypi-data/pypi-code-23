import pygsti
import numpy as np
import pickle


def assertArraysAlmostEqual(a,b):
    assert(np.linalg.norm(a-b) < 1e-6)

gateset = pygsti.construction.build_gateset(
    [2], [('Q0',)],['Gi','Gx','Gy'],
    [ "I(Q0)","X(pi/8,Q0)", "Y(pi/8,Q0)"])
#    prepLabels=["rho0"], prepExpressions=["0"],
#    effectLabels=["0","1"], effectExpressions=["0","complement"])

v0 = pygsti.construction.basis_build_vector("0", pygsti.obj.Basis("pp",2))
v1 = pygsti.construction.basis_build_vector("1", pygsti.obj.Basis("pp",2))
P0 = np.dot(v0,v0.T)
P1 = np.dot(v1,v1.T)
#print("v0 = ",v0)
#print("P0 = ",P0)
#print("P0+P1 = ",P0+P1)

gateset.instruments["Itest"] = pygsti.obj.Instrument( [('0',P0),('1',P1)] )

for param in ("full","TP","CPTP"):
    print(param)
    gateset.set_all_parameterizations(param)
    for lbl,obj in gateset.preps.items():
        print(lbl,':',obj.gpindices, pygsti.tools.length(obj.gpindices))
    for lbl,obj in gateset.povms.items():
        print(lbl,':',obj.gpindices, pygsti.tools.length(obj.gpindices))
        for sublbl,subobj in obj.items():
            print("  > ",sublbl,':',subobj.gpindices, pygsti.tools.length(subobj.gpindices))
    for lbl,obj in gateset.gates.items():
        print(lbl,':',obj.gpindices, pygsti.tools.length(obj.gpindices))
    for lbl,obj in gateset.instruments.items():
        print(lbl,':',obj.gpindices, pygsti.tools.length(obj.gpindices))
        for sublbl,subobj in obj.items():
            print("  > ",sublbl,':',subobj.gpindices, pygsti.tools.length(subobj.gpindices))


    print("NPARAMS = ",gateset.num_params())
    print("")


print("PICKLING")

x = gateset.preps #.copy(None)
p = pickle.dumps(x) #gateset.preps)
print("loading")
preps = pickle.loads(p)
assert(list(preps.keys()) == list(gateset.preps.keys()))

#p = pickle.dumps(gateset.effects)
#effects = pickle.loads(p)
#assert(list(effects.keys()) == list(gateset.effects.keys()))

p = pickle.dumps(gateset.gates)
gates = pickle.loads(p)
assert(list(gates.keys()) == list(gateset.gates.keys()))

p = pickle.dumps(gateset)
g = pickle.loads(p)
assert(np.isclose(gateset.frobeniusdist(g), 0.0))


print("GateSet IO")
pygsti.io.write_gateset(gateset, "testGateset.txt")
gateset2 = pygsti.io.load_gateset("testGateset.txt")
assert(np.isclose(gateset.frobeniusdist(gateset2),0.0))

print("Multiplication")

gatestring1 = ('Gx','Gy')
gatestring2 = ('Gx','Gy','Gy')

p1 = np.dot( gateset['Gy'], gateset['Gx'] )
p2 = gateset.product(gatestring1, bScale=False)
p3,scale = gateset.product(gatestring1, bScale=True)

print(p1)
print(p2)
print(p3*scale)
assert(np.linalg.norm(p1-scale*p3) < 1e-6)

dp = gateset.dproduct(gatestring1)
dp_flat = gateset.dproduct(gatestring1,flat=True)

evt, lookup, outcome_lookup = gateset.bulk_evaltree( [gatestring1,gatestring2] )

p1 = np.dot( gateset['Gy'], gateset['Gx'] )
p2 = np.dot( gateset['Gy'], np.dot( gateset['Gy'], gateset['Gx'] ))

bulk_prods = gateset.bulk_product(evt)
bulk_prods_scaled, scaleVals = gateset.bulk_product(evt, bScale=True)
bulk_prods2 = scaleVals[:,None,None] * bulk_prods_scaled
assertArraysAlmostEqual(bulk_prods[0],p1)
assertArraysAlmostEqual(bulk_prods[1],p2)
assertArraysAlmostEqual(bulk_prods2[0],p1)
assertArraysAlmostEqual(bulk_prods2[1],p2)

print("Probabilities")
gatestring1 = ('Gx','Gy') #,'Itest')
gatestring2 = ('Gx','Gy','Gy')

evt, lookup, outcome_lookup = gateset.bulk_evaltree( [gatestring1,gatestring2] )

p1 = np.dot( np.transpose(gateset.povms['Mdefault']['0']),
             np.dot( gateset['Gy'],
                     np.dot(gateset['Gx'],
                            gateset.preps['rho0'])))
probs = gateset.probs(gatestring1)
print(probs)
p20,p21 = probs[('0',)],probs[('1',)]

#probs = gateset.probs(gatestring1, bUseScaling=True)
#print(probs)
#p30,p31 = probs['0'],probs['1']

assertArraysAlmostEqual(p1,p20)
#assertArraysAlmostEqual(p1,p30)
#assertArraysAlmostEqual(p21,p31)

bulk_probs = gateset.bulk_probs([gatestring1,gatestring2],check=True)

evt_split = evt.copy()
new_lookup = evt_split.split(lookup, numSubTrees=2)
print("SPLIT TREE: new elIndices = ",new_lookup)
probs_to_fill = np.empty( evt_split.num_final_elements(), 'd')
gateset.bulk_fill_probs(probs_to_fill,evt_split,check=True)

dProbs = gateset.dprobs(gatestring1)
bulk_dProbs = gateset.bulk_dprobs([gatestring1,gatestring2], returnPr=False, check=True)

hProbs = gateset.hprobs(gatestring1)
bulk_hProbs = gateset.bulk_hprobs([gatestring1,gatestring2], returnPr=False, check=True)


print("DONE")
