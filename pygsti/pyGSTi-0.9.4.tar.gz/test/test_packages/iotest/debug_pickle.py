import os
import numpy as np
import pickle

import pygsti
from pygsti.construction import std1Q_XY as std
import pygsti.io.json as json
import pygsti.io.msgpack as msgpack

codec = pickle

datagen_gateset = std.gs_target.depolarize(gate_noise=0.05, spam_noise=0.1)
print("Dumping")
s = codec.dumps(datagen_gateset)
print("Loading")
x = codec.loads(s)
assert(np.isclose(datagen_gateset.frobeniusdist(x),0))
print("OK")
