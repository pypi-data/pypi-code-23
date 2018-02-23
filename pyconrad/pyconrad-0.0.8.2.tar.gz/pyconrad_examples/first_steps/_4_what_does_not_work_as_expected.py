# from pyconrad import *
import pyconrad.autoinit
from pyconrad import JArray, JDouble

_ = pyconrad.ClassGetter(
    'edu.stanford.rsl.conrad.geometry.trajectories',
    'edu.stanford.rsl.conrad.geometry'
)


# Common error: "no matching overload"
# There is no method overloading in python!
# Use JPype boxed types: http://jpype.readthedocs.io/en/latest/userguide.html#boxed-types

# Creating a PointND
# _.PointND(3, 3)  # does not work
# _.PointND([3, 3])  # neither does this
_.PointND([3., 3.])
# works since this can be unambiguosly understood as float[]
_.PointND(JArray(JDouble)([3, 2]))  # works
_.PointND.from_list([3, 2])  # works

# The same applies for SimpleVector
_.SimpleVector(JArray(JDouble)([3, 2]))  # works
# Does not work! SimpleVector has a float[] and a double[] constructor:
# _.SimpleVector([2., 3., 5.])
_.SimpleVector.from_list([3, 3])  # works

# Grid.setOrigin(...), setSpacing
# Does not work ambiguity setOrigin(float[]) and setOrigin(double[])
# _.Grid2D(3, 2).setOrigin([2, 3])
_.Grid2D(3, 2).setOrigin(JArray(JDouble)([2, 3]))

#
# # Creating nested enums
traj = _.HelicalTrajectory()
print(traj.getDetectorOffsetU())  # returns a float
enumval = _['Projection$CameraAxisDirection'].values(
)[int(traj.getDetectorOffsetU())]  # Convert back to enum
enumval = _.enumval_from_int(
    'Projection$CameraAxisDirection', traj.getDetectorOffsetU())  # or like that
enumval = _.enumval_from_int(
    'Projection$CameraAxisDirection', traj.getDetectorOffsetU())  # or like that
