import numpy as np
import numpy.random as npr
from hypothesis.strategies import integers, floats, composite

# In this file we define a number of strategies representing
# particular data types. Defining them here in one place will
# help keep ourselves consistent.

# A "real" number in the range of +- 1 million
real = floats(min_value=-1e6, max_value=1e6)


# A "size" a non negative integer representing the length of arrays etc.
size = integers(min_value=1, max_value=512)


# A stategy representing an aribrary array of vertices in cartesian coordinates
@composite
def vertices(draw):
    num = draw(size)

    return npr.rand(num, 3)


# A strategy representing an arbitrary array of faces
@composite
def faces(draw):
    num = draw(size)
    return npr.randint(1, 256, size=(num, 4))
