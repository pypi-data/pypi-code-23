import pygsti
import pickle
from pygsti.construction import std1Q_XYI

gs = std1Q_XYI.gs_target.copy()
print("inds1 = ",gs['Mdefault'].gpindices, gs['rho0'].gpindices)
s = pickle.dumps(gs)
gs2 = pickle.loads(s)
print("inds2 = ",gs2['Mdefault'].gpindices, gs2['rho0'].gpindices)
