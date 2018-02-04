from ctypes import CDLL, c_float, POINTER
clib = CDLL('./cpp/dtw.so')	# compile with : g++ -shared -O3 -Wall -fPIC -o cpp/dtw.so cpp/dtw.cpp

# an utility function allows easy CTypes binding
def fillprototype(f, restype, argtypes):
	f.restype = restype
	f.argtypes = argtypes

recency1 = [0.2, 0.3, 0.1, 0.2, 0.2]
recency2 = [0.1, 0.2, 0.3, 0.1, 0.2, 0.1]

c_recency1 = (c_float * len(recency1))(*recency1)
c_recency2 = (c_float * len(recency2))(*recency2)

class vect(Structure):
	_fields_ = [('length', c_int), ('vec', POINTER(c_float))]

fillprototype(clib.dtw, [c_float, POINTER(POINTER(c_int))], [POINTER(vect), POINTER(vect), c_float])
fillprototype(clib.free_mem, None, [POINTER(POINTER(c_int))])

value, c_path = clib.dtw(c_recency1, c_recency2, 0.001)
path = c_path[:]
clib.free_mem(c_path)

print(res)