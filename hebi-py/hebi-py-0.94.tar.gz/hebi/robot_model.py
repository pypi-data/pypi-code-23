# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
#
#  HEBI Core python API - Copyright 2018 HEBI Robotics
#  See https://hebi.us/softwarelicense for license details
#
# -----------------------------------------------------------------------------
"""
HEBI Robot Model API
--------------------
"""

from ._internal.errors import HEBI_Exception

from ._internal.raw import UnmanagedObject as __UnmanagedObject
from ._internal.raw import (FrameTypeCenterOfMass,
                            FrameTypeOutput, FrameTypeEndEffector,
                            JointTypeRotationX, JointTypeRotationY,
                            JointTypeRotationZ)


class RobotModel(__UnmanagedObject):
  """
  Represents a chain or tree of robot elements (rigid bodies and joints).
  Currently, only chains of elements are fully supported.
  """

  X5_LightBracket = 'X5-LightBracket'
  X5_HeavyBracket = 'X5-HeavyBracket'

  def __init__(self):
    from ._internal.raw import hebiRobotModelCreate, hebiRobotModelRelease
    super(RobotModel, self).__init__(hebiRobotModelCreate(),
                                     hebiRobotModelRelease)

  @property
  def base_frame(self):
    """
    The transform from the world coordinate system to the root kinematic body
    """
    from ._internal.type_utils import create_double_buffer as dbl_buffer
    from ._internal.raw import hebiRobotModelGetBaseFrame, StatusSuccess

    frame = dbl_buffer(16)
    code = hebiRobotModelGetBaseFrame(self, frame)
    if (code != StatusSuccess):
      raise HEBI_Exception(code, 'hebiRobotModelGetBaseFrame failed')

    from ._internal.type_utils import to_contig_sq_mat as to_mat
    return to_mat(frame, size=4)

  @base_frame.setter
  def base_frame(self, value):
    """
    Set the transform from a world coordinate system to the input of the root
    element in this robot model. Defaults to an identity 4x4 matrix.

    The world coordinate system is used for all position, vector,
    and transformation matrix parameters in the member functions.

    :param value: A 4x4 matrix representing the base frame
    """
    from ctypes import c_double, POINTER
    from ._internal.type_utils import to_contig_sq_mat as to_mat
    from ._internal.raw import hebiRobotModelSetBaseFrame, StatusSuccess

    base_frame = to_mat(value, size=4)

    c_double_p = POINTER(c_double)
    code = hebiRobotModelSetBaseFrame(self, base_frame.ctypes.data_as(c_double_p))
    if (code != StatusSuccess):
      raise HEBI_Exception(code, 'hebiRobotModelSetBaseFrame failed')

  def get_frame_count(self, frame_type):
    """
    The number of frames in the forward kinematics.

    Note that this depends on the type of frame requested:
      * for center of mass frames, there is one per added body.
      * for output frames, there is one per output per body.

    :param frame_type: Which type of frame to consider - see HebiFrameType enum.
    :return: the number of frames of the specified type
    """
    from ._internal.raw import hebiRobotModelGetNumberOfFrames

    res = hebiRobotModelGetNumberOfFrames(self, frame_type)
    if (res < 0):
      return 0
    return res

  @property
  def dof_count(self):
    """
    the number of settable degrees of freedom in the kinematic tree.
    This is equal to the number of actuators added.
    """
    from ._internal.raw import hebiRobotModelGetNumberOfDoFs

    res = hebiRobotModelGetNumberOfDoFs(self)
    if (res < 0):
      return 0
    return res

  def __try_add(self, body, combine):
    from ._internal.raw import (hebiRobotModelAdd, hebiRobotModelElementRelease,
                               StatusSuccess)

    res = hebiRobotModelAdd(self, None, 0, body, int(combine))
    if (res != StatusSuccess):
      hebiRobotModelElementRelease(body)
      raise HEBI_Exception(res, 'hebiRobotModelAdd failed')

  def add_rigid_body(self, com, inertia, mass, output, combine):
    """
    Adds a rigid body with the specified properties to the robot model.

    This can be 'combined' with the parent element
    (the element to which this is attaching), which means that the mass,
    inertia, and output frames of this element will be integrated with
    the parent. The mass will be combined, and the reported parent output frame
    that this element attached to will be replaced with the output from
    this element (so that the number of output frames and masses remains constant).

    :param com: 4x4 matrix of the homogeneous transform to the center
                of mass location, relative to the input frame of the element.
                Note that this frame is also the frame in which
                the inertia tensor is given.
    :param inertia: The 6 element representation (Ixx, Iyy, Izz, Ixy, Ixz, Iyz)
                    of the inertia tensor, in the frame given by the COM.
    :param mass: The mass of this element.
    :param output:  4x4 matrix of the homogeneous transform to the output frame,
                    relative to the input frame of the element.
    :param combine: ``True`` if the frames and masses of this body should
                    be combined with the parent, ``False`` otherwise.
    """

    from ._internal.raw import hebiRobotModelElementCreateRigidBody
    from ctypes import c_double, POINTER
    import numpy as np

    inertia = np.asarray(inertia)
    if (len(inertia) != 6):
      raise ValueError('inertia must be a 6 element array')

    c_double_p = POINTER(c_double)

    from ._internal.type_utils import to_contig_sq_mat as to_mat
    com = to_mat(com, size=4).ctypes.data_as(c_double_p)
    output = to_mat(output, size=4).ctypes.data_as(c_double_p)

    inertia = inertia.ctypes.data_as(c_double_p)
    body = hebiRobotModelElementCreateRigidBody(com, inertia, mass, 1, output)
    self.__try_add(body, combine)
    return True

  def add_joint(self, joint_type, combine):
    """
    Adds a degree of freedom about the specified axis.

    This does not represent an element with size or mass, but only a
    connection between two other elements about a particular axis.

    :param joint_type: The axis of rotation or translation about which this
                       joint allows motion.
    :param combine:
    """
    from ._internal.raw import hebiRobotModelElementCreateJoint

    self.__try_add(hebiRobotModelElementCreateJoint(joint_type), combine)
    return True

  def add_actuator(self, actuator_type):
    """
    Add an element to the robot model with the kinematics/dynamics of an
    X5 actuator.

    :param actuator_type: The type of actuator to add.
    """
    import numpy as np
    from ._internal.kinematics import parse_actuator, set_translate
    from ._internal.raw import JointTypeRotationZ

    actuator, com, input_to_axis = parse_actuator(actuator_type)

    mass = actuator.mass
    inertia = actuator.moments_of_inertia

    joint_type = JointTypeRotationZ

    if not (self.add_rigid_body(com, inertia, mass, input_to_axis, False)):
      raise RuntimeError('Could not add actuator')
    return self.add_joint(joint_type, True)

  def add_link(self, link_type, extension, twist):
    """
    Add an element to the robot model with the kinematics/dynamics
    of a link between two actuators.

    :param link_type: The type of link between the actuators, e.g. a tube link
                      between two X5 or X8 actuators.
    :param extension: The center-to-center distance between the actuator
                      rotational axes.
    :param twist:     The rotation (in radians) between the actuator axes of
                      rotation. Note that a 0 radian rotation will result
                      in a z-axis offset between the two actuators,
                      and a pi radian rotation will result in the actuator
                      interfaces to this tube being in the same plane, but the
                      rotational axes being anti-parallel.
    """
    from ._internal.kinematics import (parse_actuator_link, set_translate,
                                       set_rotate_x, set_rod_x_axis_inertia)

    extension, twist = parse_actuator_link(link_type, extension, twist)

    from math import cos, sin
    import numpy as np

    com = np.identity(4, np.float64)
    output = np.identity(4, np.float64)

    # Tube approx. 0.4kg / 1m; 0.03m shorter than the total extension length
    # End brackets + hardware approx. 0.26 kg
    mass = 0.4 * (extension - 0.03) + 0.26

    # Edge of bracket to center of pipe
    edge_to_center = 0.0175

    set_translate(com, extension * 0.5, 0, edge_to_center)
    set_rotate_x(output, twist)
    set_translate(output, extension,
                  -edge_to_center * sin(twist),
                  edge_to_center * (1 + cos(twist)))

    inertia = np.empty(6, np.float64)
    set_rod_x_axis_inertia(inertia, mass, extension)
    return self.add_rigid_body(com, inertia, mass, output, False)

  def add_bracket(self, bracket_type, mount):
    """
    Add an element to the robot model with the kinematics/dynamics of a bracket
    between two actuators.

    :param bracket_type: The type of bracket to add.
    """
    from ._internal.kinematics import parse_bracket, set_sphere_inertia

    com, output, mass = parse_bracket(bracket_type, mount)

    import numpy as np
    inertia = np.empty(6, np.float64)

    set_sphere_inertia(inertia, mass, 0.06)
    return self.add_rigid_body(com, inertia, mass, output, False)

  def get_forward_kinematics(self, frame_type, positions):
    """
    Generates the forward kinematics for the given robot model.

    The order of the returned frames is in a depth-first tree. As an example,
    assume a body A has one output, to which body B is connected. Body B has
    two outputs; actuator C is attached to the first output and actuator E is
    attached to the second output. Body D is attached to the only output of
    actuator C:

    (BASE) A - B(1) - C - D
              (2)
               |
               E

    For center of mass frames, the returned frames would be A-B-C-D-E.
    For output frames, the returned frames would be A-B(1)-C-D-B(2)-E.

    :param frame_type: Which type of frame to consider - see HebiFrameType enum.
    :param positions: A vector of joint positions/angles (in SI units of meters
                      or radians) equal in length to the number of DoFs
                      of the kinematic tree.

    :return:  An array of 4x4 transforms; this is resized as necessary
              in the function and filled in with the 4x4 homogeneous transform
              of each frame. Note that the number of frames depends
              on the frame type.
    """
    from ctypes import c_double, POINTER
    import numpy as np
    from ._internal.raw import hebiRobotModelGetForwardKinematics
    from ._internal.type_utils import create_double_buffer as dbl_buffer

    c_double_p = POINTER(c_double)

    positions = np.asarray(positions, np.float64)
    positions = positions.ctypes.data_as(c_double_p)
    num_frames = self.get_frame_count(frame_type)

    frames = dbl_buffer(num_frames * 16)
    hebiRobotModelGetForwardKinematics(self, frame_type, positions, frames)

    ret = [None] * num_frames
    for i in range(0, num_frames):
      start = i * 16
      end = start + 16
      mat = np.asmatrix(frames[start:end], np.float64)
      ret[i] = mat.reshape((4, 4))

    return ret

  def get_end_effector(self, positions):
    """
    Generates the forward kinematics to the end effector (leaf node)

    Note: for center of mass frames, this is one per leaf node; for output
    frames, this is one per output per leaf node, in depth first order.

    This overload is for kinematic chains that only have a single leaf node frame.

    *Currently, kinematic trees are not fully supported -- only kinematic
    chains -- and so there are not other overloads for this function.*

    :param positions: A vector of joint positions/angles
                      (in SI units of meters or radians) equal in length
                      to the number of DoFs of the kinematic tree.

    :return:  A 4x4 transform that is resized as necessary in the
              function and filled in with the homogeneous transform to the end
              effector frame.
    """
    from ctypes import c_double, POINTER
    import numpy as np
    from ._internal.raw import hebiRobotModelGetForwardKinematics
    from ._internal.type_utils import create_double_buffer as dbl_buffer

    c_double_p = POINTER(c_double)

    positions = np.asarray(positions, np.float64)
    positions = positions.ctypes.data_as(c_double_p)

    transforms = dbl_buffer(16)
    hebiRobotModelGetForwardKinematics(self, FrameTypeEndEffector,
                                       positions, transforms)
    return np.asmatrix(transforms, np.float64).reshape((4 ,4))

  def solve_inverse_kinematics(self, initial_positions, *objectives):
    """
    Solves for an inverse kinematics solution given a set of objectives.

    :param initial_positions: The seed positions/angles (in SI units of meters
                              or radians) from which to start the IK search;
                              equal in length to the number of DoFs of the
                              kinematic tree.
    :param objectives:  A variable number of objectives used to define the IK
                        search (e.g., target end effector positions, etc).
                        Each argument must have a base class of Objective.

    :return:  A vector equal in length to the number of DoFs of the kinematic tree;
              this will be filled in with the IK solution
              (in SI units of meters or radians) and resized as necessary.
    """
    from ctypes import c_double, POINTER
    import numpy as np
    from ._internal.raw import (hebiIKCreate, hebiIKSolve,
                               hebiIKRelease, StatusSuccess)
    from ._internal.type_utils import create_double_buffer as dbl_buffer

    c_double_p = POINTER(c_double)
    initial_positions = np.asarray(initial_positions, np.float64)
    result = dbl_buffer(len(initial_positions))
    initial_positions = initial_positions.ctypes.data_as(c_double_p)

    ik = hebiIKCreate()

    for entry in objectives:
      entry(ik)

    code = hebiIKSolve(ik, self, initial_positions, result, None)
    hebiIKRelease(ik)

    if (code != StatusSuccess):
      raise HEBI_Exception(code, 'hebiIKSolve failed')
    return np.asarray(result, np.float64)

  def get_jacobians(self, frame_type, positions):
    """
    Generates the Jacobian for each frame in the given kinematic tree.

    :param frame_type: Which type of frame to consider - see HebiFrameType enum.
    :param positions: A vector of joint positions/angles
                      (in SI units of meters or radians)
                      equal in length to the number of DoFs of the
                      kinematic tree.

    :return:  A vector (length equal to the number of frames) of
              matrices; each matrix is a (6 x number of dofs)
              jacobian matrix for the corresponding frame of reference
              on the robot. It is resized as necessary inside this function.
    """
    from ctypes import c_double, POINTER
    import numpy as np
    from ._internal.raw import hebiRobotModelGetJacobians
    from ._internal.type_utils import create_double_buffer as dbl_buffer

    c_double_p = POINTER(c_double)
    positions = np.asarray(positions, np.float64)
    positions = positions.ctypes.data_as(c_double_p)

    frames = self.get_frame_count(frame_type)
    dofs = self.dof_count
    rows = 6 * frames
    cols = dofs

    jacobians = dbl_buffer(rows * cols)
    hebiRobotModelGetJacobians(self, frame_type, positions, jacobians)

    ret = [None] * frames
    for i in range(0, frames):
      start = i * cols * 6
      end = start + cols * 6
      mat = np.asmatrix(jacobians[start:end], np.float64)
      ret[i] = mat.reshape((6, cols))
    return ret

  def get_jacobian_end_effector(self, positions, reuse_jacobians=None):
    """
    Generates the Jacobian for the end effector (leaf node) frames(s).

    Note: for center of mass frames, this is one per leaf node; for output
    frames, this is one per output per leaf node, in depth first order.

    This overload is for kinematic chains that only have a single leaf node frame.

    *Currently, kinematic trees are not fully supported -- only kinematic
    chains -- and so there are not other overloads for this function.*

    :param positions: A vector of joint positions/angles (in SI units of
                      meters or radians) equal in length to the number of
                      DoFs of the kinematic tree.
    :param reuse_jacobians: An optional parameter of previously calculated
                            jacobians. This may be None, but is useful to
                            amortize the computation.

    :return:  A (6 x number of dofs) jacobian matrix for the corresponding
              end effector frame of reference on the robot. It is resized as
              necessary inside this function.
    """
    import numpy as np

    positions = np.asarray(positions, np.float64)
    if (reuse_jacobians == None):
      reuse_jacobians = self.get_jacobians(np, positions)
    return reuse_jacobians[-1]

  @property
  def masses(self):
    """
    The mass of each rigid body (or combination of rigid bodies) in the robot.
    """
    import numpy as np
    from ._internal.raw import hebiRobotModelGetMasses
    from ._internal.type_utils import create_double_buffer as dbl_buffer

    count = self.get_frame_count(FrameTypeCenterOfMass)
    masses = dbl_buffer(count)
    hebiRobotModelGetMasses(self, masses)
    return np.asarray(masses, np.float64)


# -----------------------------------------------------------------------------
# IK Objective functions
# -----------------------------------------------------------------------------


def endeffector_position_objective(xyz, weight=1.0):
  """
  Create a position end effector objective with the given parameters.
  Analogous to ``EndEffectorPositionObjective`` in the C++ API.

  :param xyz:
  :param weight:
  :return:
  """

  x = float(xyz[0])
  y = float(xyz[1])
  z = float(xyz[2])
  weight = float(weight)

  class Objective(object):
    def __init__(self):
      self._x = x
      self._y = y
      self._z = z
      self._weight = weight

    @property
    def x(self):
      return self._x

    @property
    def y(self):
      return self._y

    @property
    def z(self):
      return self._z

    @property
    def weight(self):
      return self._weight

    def __call__(self, internal):
      """
      Used internally. Do not invoke directly.
      """
      from ._internal.raw import (hebiIKAddObjectiveEndEffectorPosition,
                                  StatusSuccess)
      res = hebiIKAddObjectiveEndEffectorPosition(internal,
                                                  self._weight, 0,
                                                  self._x, self._y, self._z)
      if (res != StatusSuccess):
        raise HEBI_Exception(res, 'hebiIKAddObjectiveEndEffectorPosition failed')

  return Objective()


def endeffector_so3_objective(rotation, weight=1.0):
  """
  Create an SO3 end effector objective with the given parameters.
  Analogous to ``EndEffectorSO3Objective`` in the C++ API.

  :param rotation:
  :param weight:
  :return:
  """

  import numpy as np
  from ._internal.type_utils import to_contig_sq_mat as sq_mat
  rotation = np.array(rotation, dtype=np.float64, copy=True)
  rotation = sq_mat(rotation, size=3)
  weight = float(weight)

  class Objective(object):
    def __init__(self):
      self._rotation = rotation
      self._weight = weight

    @property
    def rotation(self):
      return self._rotation

    @property
    def weight(self):
      return self._weight

    def __call__(self, internal):
      """
      Used internally. Do not invoke directly.
      """
      from ._internal.raw import (hebiIKAddObjectiveEndEffectorSO3,
                                  StatusSuccess)
      from ctypes import POINTER, c_double
      rotation = self._rotation.ctypes.data_as(POINTER(c_double))
      res = hebiIKAddObjectiveEndEffectorSO3(internal,
                                            self._weight, 0, rotation)
      if (res != StatusSuccess):
        raise HEBI_Exception(res, 'hebiIKAddObjectiveEndEffectorSO3 failed')

  return Objective()


def endeffector_tipaxis_objective(axis, weight=1.0):
  """
  Create a tip axis end effector objective with the given parameters.
  Analogous to ``EndEffectorTipAxisObjective`` in the C++ API.

  :param axis:
  :param weight:
  :return:
  """

  x = float(axis[0])
  y = float(axis[1])
  z = float(axis[2])
  weight = float(weight)

  class Objective(object):
    def __init__(self):
      self._x = x
      self._y = y
      self._z = z
      self._weight = weight

    @property
    def x(self):
      return self._x

    @property
    def y(self):
      return self._y

    @property
    def z(self):
      return self._z

    @property
    def weight(self):
      return self._weight

    def __call__(self, internal):
      """
      Used internally. Do not invoke directly.
      """
      from ._internal.raw import (hebiIKAddObjectiveEndEffectorTipAxis,
                                  StatusSuccess)
      res = hebiIKAddObjectiveEndEffectorTipAxis(internal,
                                                  self._weight, 0,
                                                  self._x, self._y, self._z)
      if (res != StatusSuccess):
        raise HEBI_Exception(res, 'hebiIKAddObjectiveEndEffectorTipAxis failed')

  return Objective()


def joint_limit_constraint(minimum, maximum, weight=1.0):
  """
  Create a joint limit constraint objective.
  Analogous to ``JointLimitConstraint`` in the C++ API.

  :param minimum:
  :param maximum:
  :param weight:
  :return:
  """

  import numpy as np
  minimum = np.array(minimum, dtype=np.float64, copy=True)
  maximum = np.array(maximum, dtype=np.float64, copy=True)

  if (minimum.size != maximum.size):
    raise RuntimeError('size of min and max joint limit constraints must be equal')

  class Objective(object):
    def __init__(self):
      self._minimum = minimum
      self._maximum = maximum
      self._weight = weight

    @property
    def minimum(self):
      return self._minimum

    @property
    def maximum(self):
      return self._maximum

    @property
    def weight(self):
      return self._weight

    def __call__(self, internal):
      """
      Used internally. Do not invoke directly.
      """
      from ._internal.raw import (hebiIKAddConstraintJointAngles,
                                  StatusSuccess)
      from ctypes import POINTER, c_double
      minimum = self._minimum.ctypes.data_as(POINTER(c_double))
      maximum = self._maximum.ctypes.data_as(POINTER(c_double))
      res = hebiIKAddConstraintJointAngles(internal, self._weight,
                                           self._minimum.size,
                                           minimum, maximum)
      if (res != StatusSuccess):
        raise HEBI_Exception(res, 'hebiIKAddConstraintJointAngles failed')

  return Objective()