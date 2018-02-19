import numpy as np

a = np.array([
 [-0.239746,-0.290771,-0.867432],
 [-0.259033,-0.320312,-0.911133],
 [-0.188721,-0.356445,-0.889648],
 [-0.186279,-0.359619,-0.895996],
])

rot = np.array([
 [0.67151763, 0.1469127, 0.72627869],
 [0.47140706, 0.67151763, -0.57169875],
 [-0.57169875, 0.72627869, 0.38168025],
])

print "----- R"

print rot

print "----- A"

for i in range(a.shape[0]):
    print a[i, :]

print "----- rotated "

for i in range(a.shape[0]):
    print rot.dot(a[i, :])

#print "----- test rotated again"

#print rot.dot(a)
 
print "----- rotated again"

print rot.dot(a.T).T
