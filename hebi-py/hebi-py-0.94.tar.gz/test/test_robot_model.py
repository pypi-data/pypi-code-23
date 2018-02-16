import unittest
import math
import numpy as np

from math import (cos, sin, isinf, isnan)

NaN = np.nan
Inf = np.inf
PI = math.pi

class RobotModelTestCase(unittest.TestCase):

  def setUp(self):
    from hebi.robot_model import RobotModel
    self._kin = RobotModel()
    self.assertIsNotNone(self._kin)

  def tearDown(self):
    del self._kin

  def combineX5_4(self):
    """
    Add an x5-4 to the current robot model, combining with the last body.
    This isn't the expected behavior of ``robot_model.add_actuator()``
    """
    from hebi._internal.kinematics import parse_actuator
    from hebi._internal.raw import JointTypeRotationZ

    actuator, com, input_to_axis = parse_actuator('X5-4')
    mass = actuator.mass
    inertia = actuator.moments_of_inertia
    joint_type = JointTypeRotationZ

    self._kin.add_rigid_body(com, inertia, mass, input_to_axis, True)
    self._kin.add_joint(joint_type, True)

  def addX5_4(self):
    """
    Add an x5-4 to the current robot model
    """
    self._kin.add_actuator('X5-4')

  def addX5_8Link(self, ext, twist):
    """
    Add an x5-8 link to with the given extension and twist to the current
    robot model
    """
    self._kin.add_link('X5', ext, twist)

  def addBracket(self, bracket_type, mount):
    """
    Add a bracket of the given type and mount to the current robot model
    """
    self._kin.add_bracket(bracket_type, mount)

  def addHexapodShoulder(self):
    """
    Add a hexapod shoulder to the current robot model
    """
    from hebi._internal.kinematics import set_sphere_inertia
    com = np.matrix(
      [
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, -0.0225 / 2.0],
        [0.0, 0.0, 1.0, 0.055 / 2.0],
        [0.0, 0.0, 0.0, 1.0]
      ],
      dtype=np.float64)

    output = np.matrix(
      [
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, -0.0225],
        [0.0, -1.0, 0.0, 0.055],
        [0.0, 0.0, 0.0, 1.0]
      ],
      dtype=np.float64)

    mass = 0.25
    inertia = np.empty(6, dtype=np.float64)
    set_sphere_inertia(inertia, mass, 0.06)
    self._kin.add_rigid_body(com, inertia, mass, output, False)

  def isfinite(self,x):
    return not (isinf(x) or isnan(x))

  def check_translate(self, actual, x, y, z, thresh=0.002):
    """
    :param actual: a 4x4 numpy matrix
    """
    if (self.isfinite(x)):
      self.assertAlmostEqual(actual[0,3], x, delta=thresh)
    if (self.isfinite(y)):
      self.assertAlmostEqual(actual[1,3], y, delta=thresh)
    if (self.isfinite(z)):
      self.assertAlmostEqual(actual[2,3], z, delta=thresh)

  def check_last_row(self, actual, delta=0.0001):
    """
    :param actual: a 4x4 numpy matrix
    """
    self.assertAlmostEqual(actual[3,0], 0.0, delta=delta)
    self.assertAlmostEqual(actual[3,1], 0.0, delta=delta)
    self.assertAlmostEqual(actual[3,2], 0.0, delta=delta)
    self.assertAlmostEqual(actual[3,3], 1.0, delta=delta)

  def check_identity_rot(self, actual, delta=0.0001):
    """
    :param actual: a 4x4 numpy matrix
    """
    self.assertAlmostEqual(actual[0,0], 1.0, delta=delta)
    self.assertAlmostEqual(actual[0,1], 0.0, delta=delta)
    self.assertAlmostEqual(actual[0,2], 0.0, delta=delta)
    self.assertAlmostEqual(actual[1,0], 0.0, delta=delta)
    self.assertAlmostEqual(actual[1,1], 1.0, delta=delta)
    self.assertAlmostEqual(actual[1,2], 0.0, delta=delta)
    self.assertAlmostEqual(actual[2,0], 0.0, delta=delta)
    self.assertAlmostEqual(actual[2,1], 0.0, delta=delta)
    self.assertAlmostEqual(actual[2,2], 1.0, delta=delta)

  def check_rot(self, actual, expect, delta=0.0001):
    """
    :param actual: a 4x4 numpy matrix
    :param expect: a 9 element list
    """
    self.assertAlmostEqual(actual[0,0], expect[0], delta=delta)
    self.assertAlmostEqual(actual[0,1], expect[1], delta=delta)
    self.assertAlmostEqual(actual[0,2], expect[2], delta=delta)
    self.assertAlmostEqual(actual[1,0], expect[3], delta=delta)
    self.assertAlmostEqual(actual[1,1], expect[4], delta=delta)
    self.assertAlmostEqual(actual[1,2], expect[5], delta=delta)
    self.assertAlmostEqual(actual[2,0], expect[6], delta=delta)
    self.assertAlmostEqual(actual[2,1], expect[7], delta=delta)
    self.assertAlmostEqual(actual[2,2], expect[8], delta=delta)

  def check_transform_matrix(self, actual, expect, delta=0.0001):
    """
    :param actual: a 4x4 numpy matrix
    :param expect: a 4x4 numpy matrix
    """
    self.assertAlmostEqual(actual[0,0], expect[0,0], delta=delta)
    self.assertAlmostEqual(actual[0,1], expect[0,1], delta=delta)
    self.assertAlmostEqual(actual[0,2], expect[0,2], delta=delta)
    self.assertAlmostEqual(actual[0,3], expect[0,3], delta=delta)
    self.assertAlmostEqual(actual[1,0], expect[1,0], delta=delta)
    self.assertAlmostEqual(actual[1,1], expect[1,1], delta=delta)
    self.assertAlmostEqual(actual[1,2], expect[1,2], delta=delta)
    self.assertAlmostEqual(actual[1,3], expect[1,3], delta=delta)
    self.assertAlmostEqual(actual[2,0], expect[2,0], delta=delta)
    self.assertAlmostEqual(actual[2,1], expect[2,1], delta=delta)
    self.assertAlmostEqual(actual[2,2], expect[2,2], delta=delta)
    self.assertAlmostEqual(actual[2,3], expect[2,3], delta=delta)
    self.assertAlmostEqual(actual[3,0], expect[3,0], delta=delta)
    self.assertAlmostEqual(actual[3,1], expect[3,1], delta=delta)
    self.assertAlmostEqual(actual[3,2], expect[3,2], delta=delta)
    self.assertAlmostEqual(actual[3,3], expect[3,3], delta=delta)

  def check_fk_result(self, frames, expect_size):
    """
    Check type and dimensionality of a given frames result
    (list of frames, not a single frame)
    """
    self.assertIsNotNone(frames)
    self.assertIsInstance(frames, list)
    self.assertEqual(len(frames), expect_size)

  def check_j_result(self, jacobians, expect_size):
    """
    Check type and dimensionality of a given jacobian frames result
    (list of jacobian frames, not a single jacobian frame)
    """
    self.assertIsNotNone(jacobians)
    self.assertIsInstance(jacobians, list)
    self.assertEqual(len(jacobians), expect_size)

  def check_frame(self, frame):
    """
    Check type and dimensionality of a given frame
    """
    self.assertIsNotNone(frame)
    self.assertIsInstance(frame, np.matrix)
    self.assertEqual(frame.shape[0], 4)
    self.assertEqual(frame.shape[1], 4)
    self.assertEqual(frame.dtype, np.float64)

  def check_j_frame(self, jacobian, dof_count):
    """
    Check type and dimensionality of a given jacobian frame
    """
    self.assertIsNotNone(jacobian)
    self.assertIsInstance(jacobian, np.matrix)
    self.assertEqual(jacobian.dtype, np.float64)
    self.assertEqual(jacobian.shape[0], 6)
    self.assertEqual(jacobian.shape[1], dof_count)

  def check_ik_result(self, angles, seed):
    """
    Check type and dimensionality of a given ik result
    """
    self.assertIsNotNone(angles)
    self.assertIsInstance(angles, np.ndarray)
    self.assertEqual(angles.shape[0], seed.shape[0])
    self.assertEqual(angles.dtype, np.float64)

  def check_almost_equal(self, a, b, delta=0.01):
    """
    Utility function to use ``assertAlmostEqual`` on each element
    in two iterable objects of the same length
    """
    self.assertEqual(len(a), len(b))
    for i in range(0, len(a)):
      self.assertAlmostEqual(a[i], b[i], delta=delta)

################################################################################
# Tests adapted from C API `kinematics1.cpp`
################################################################################

  def testX5(self):
    """
    TODO: Document
    """
    from hebi.robot_model import FrameTypeOutput

    # construct body
    self.addX5_4()

    # check body dimensions
    expect_frames = 1
    expect_dof = 1
    self.assertEqual(expect_frames, self._kin.get_frame_count(FrameTypeOutput))
    self.assertEqual(expect_dof, self._kin.dof_count)

    # create array of positions (empty array)
    angles = np.array([0.0], dtype=np.float64)

    # Solve for forward kinematics and verify result type and frame count
    frames = self._kin.get_forward_kinematics(FrameTypeOutput, angles)
    self.check_fk_result(frames, expect_frames)

    # Check frame type and dimensions
    frame1 = frames[0]
    self.check_frame(frame1)

    # Check frame values
    self.check_translate(frame1, 0, 0, 0.03105)
    self.check_last_row(frame1)
    self.check_identity_rot(frame1)

    # Change position value(s), resolve, and reverify result type and frame count
    angles[0] = 0.3
    frames = self._kin.get_forward_kinematics(FrameTypeOutput, angles)
    self.check_fk_result(frames, expect_frames)

    # Check frame type and dimensions
    frame1 = frames[0]
    self.check_frame(frame1)

    # Check frame values
    self.check_translate(frame1, 0, 0, 0.03105)
    self.check_last_row(frame1)
    self.check_rot(frame1,
      [ 
        cos(angles[0]), -sin(angles[0]), 0,
        sin(angles[0]), cos(angles[0]), 0,
        0, 0, 1
      ])

  def testLink1(self):
    """
    TODO: Document
    """

    # construct body
    self.addX5_8Link(0.3, 0.0)

    # check body dimensions
    expect_frames = 1
    expect_dof = 0
    self.assertEqual(expect_frames, self._kin.get_frame_count(FrameTypeOutput))
    self.assertEqual(expect_dof, self._kin.dof_count)

    # create array of positions (empty array)
    angles = np.array([], dtype=np.float64)

    # Solve for forward kinematics and verify result type and frame count
    frames = self._kin.get_forward_kinematics(FrameTypeOutput, angles)
    self.check_fk_result(frames, expect_frames)

    # Check frame type and dimensions
    frame1 = frames[0]
    self.check_frame(frame1)

    # Check frame values
    self.check_translate(frame1, 0.3, 0.0, 0.035)
    self.check_last_row(frame1)
    self.check_identity_rot(frame1)

  def testLink2(self):
    """
    TODO: Document
    """

    # construct body
    self.addX5_8Link(0.3, math.pi)

    # check body dimensions
    expect_frames = 1
    expect_dof = 0
    self.assertEqual(expect_frames, self._kin.get_frame_count(FrameTypeOutput))
    self.assertEqual(expect_dof, self._kin.dof_count)

    # create array of positions (empty array)
    angles = np.array([], dtype=np.float64)

    # Solve for forward kinematics and verify result type and frame count
    frames = self._kin.get_forward_kinematics(FrameTypeOutput, angles)
    self.check_fk_result(frames, expect_frames)

    # Check frame type and dimensions
    frame1 = frames[0]
    self.check_frame(frame1)

    # Check frame values
    self.check_translate(frame1, 0.3, 0.0, 0.0)
    self.check_last_row(frame1)
    self.check_rot(frame1,
      [
        1.0, 0.0, 0.0,
        0.0, -1.0, 0.0,
        0.0, 0.0, -1.0
      ])

  def testLink3(self):
    """
    TODO: Document
    """

    # construct body
    self.addX5_8Link(0.5, 0.3)

    # check body dimensions
    expect_frames = 1
    expect_dof = 0
    self.assertEqual(expect_frames, self._kin.get_frame_count(FrameTypeOutput))
    self.assertEqual(expect_dof, self._kin.dof_count)

    # create array of positions (empty array)
    angles = np.array([], dtype=np.float64)

    # Solve for forward kinematics and verify result type and frame count
    frames = self._kin.get_forward_kinematics(FrameTypeOutput, angles)
    self.check_fk_result(frames, expect_frames)

    # Check frame type and dimensions
    frame1 = frames[0]
    self.check_frame(frame1)

    # Check frame values
    self.check_translate(frame1, 0.5, -0.00517160361657, 0.0342183885597)
    self.check_last_row(frame1)
    self.check_rot(frame1,
      [
        1.0, 0.0, 0.0,
        0.0, cos(0.3), -sin(0.3),
        0.0, sin(0.3), cos(0.3)
      ])

  def testLightBracketLeft(self):
    """
    TODO: Document
    """
    self.addBracket('X5-LightBracket', 'left')
    # TODO: add tests
    # (this test wasn't finished in the C API :/)

  def testLightBracketRight(self):
    """
    TODO: Document
    """
    self.addBracket('X5-LightBracket', 'right')
    # TODO: add tests
    # (this test wasn't finished in the C API :/)

  def testHeavyBracketLeftInside(self):
    """
    TODO: Document
    """
    self.addBracket('X5-HeavyBracket', 'left-inside')
    # TODO: add tests
    # (this test wasn't finished in the C API :/)

  def testHeavyBracketLeftOutside(self):
    """
    TODO: Document
    """
    self.addBracket('X5-HeavyBracket', 'left-outside')
    # TODO: add tests
    # (this test wasn't finished in the C API :/)

  def testHeavyBracketRightInside(self):
    """
    TODO: Document
    """
    self.addBracket('X5-HeavyBracket', 'right-inside')
    # TODO: add tests
    # (this test wasn't finished in the C API :/)

  def testHeavyBracketRightOutside(self):
    """
    TODO: Document
    """
    self.addBracket('X5-HeavyBracket', 'right-outside')
    # TODO: add tests
    # (this test wasn't finished in the C API :/)

  def testIK1(self):
    """
    TODO: Document
    """

    # construct body
    self.addX5_4()
    self.addX5_8Link(0.5, 0.0)
    self.addX5_4()
    self.addX5_8Link(0.7, 0.0)

    # create seed position angles and objectives for IK
    seed_angles = np.array([0.0, 0.0], np.float64)
    xyz_goal = np.array([1.1, 0.4, 0.3], np.float64)
    position_objective = endeffector_position_objective(xyz_goal, weight=1.0)

    # solve for IK and check result type and dimensionality
    final_angles = self._kin.solve_inverse_kinematics(seed_angles, position_objective)
    self.check_ik_result(final_angles, seed_angles)

    # Verify IK results
    self.assertAlmostEqual(final_angles[0], 0.085, delta=0.01)
    self.assertAlmostEqual(final_angles[1], 0.451, delta=0.01)

  def testIKUnderConstrained(self):
    """
    TODO: Document
    """

    # construct body
    self.addX5_4()
    self.addX5_8Link(0.5, 0.0)
    self.addX5_4()
    self.addX5_8Link(0.7, 0.0)
    self.addX5_4()
    self.addX5_8Link(0.3, 0.0)

    # create seed position angles and objectives for IK
    seed_angles = np.array([0.0, 0.0, 0.0], np.float64)
    xyz_goal = np.array([1.1, 0.4, 0.3], np.float64)
    position_objective = endeffector_position_objective(xyz_goal, weight=1.0)

    # solve for IK and check result type and dimensionality
    final_angles = self._kin.solve_inverse_kinematics(seed_angles, position_objective)
    self.check_ik_result(final_angles, seed_angles)

    # get end effector frame and verify dimensionality and type
    frame = self._kin.get_end_effector(final_angles)
    self.check_frame(frame)

    # verify end effector frame equals our endeffector position objective
    self.assertAlmostEqual(frame[0,3], 1.1, delta=0.01)
    self.assertAlmostEqual(frame[1,3], 0.4, delta=0.01)

  def testJacobianArm1DOF(self):
    """
    TODO: Document
    """

    # construct body
    self.addX5_4()
    self.addX5_8Link(0.3, 0.0)

    # check body dimensions
    expect_frames = 2
    expect_dof = 1
    self.assertEqual(expect_frames, self._kin.get_frame_count(FrameTypeOutput))
    self.assertEqual(expect_dof, self._kin.dof_count)

    # create array of positions
    angles = np.array([0], np.float64)

    # solve for jacobians at position and check result length and type
    jacobians = self._kin.get_jacobians(FrameTypeOutput, angles)
    self.check_j_result(jacobians, expect_frames)

    # Check jacobian frame types and dimensions
    jac1 = jacobians[0]
    jac2 = jacobians[1]
    self.check_j_frame(jac1, expect_dof)
    self.check_j_frame(jac2, expect_dof)

    # Check jacobian frame values
    self.assertAlmostEqual(jac1[0], 0.0, delta=0.01)
    self.assertAlmostEqual(jac1[1], 0.0, delta=0.01)
    self.assertAlmostEqual(jac1[2], 0.0, delta=0.01)
    self.assertAlmostEqual(jac1[3], 0.0, delta=0.01)
    self.assertAlmostEqual(jac1[4], 0.0, delta=0.01)
    self.assertAlmostEqual(jac1[5], 1.0, delta=0.01)
    self.assertAlmostEqual(jac2[0], 0.0, delta=0.01)
    self.assertAlmostEqual(jac2[1], 0.3, delta=0.01)
    self.assertAlmostEqual(jac2[2], 0.0, delta=0.01)
    self.assertAlmostEqual(jac2[3], 0.0, delta=0.01)
    self.assertAlmostEqual(jac2[4], 0.0, delta=0.01)
    self.assertAlmostEqual(jac2[5], 1.0, delta=0.01)

    # Change position value(s), resolve, and reverify result type and frame count
    angles[0] = 0.5
    jacobians = self._kin.get_jacobians(FrameTypeOutput, angles)
    self.check_j_result(jacobians, expect_frames)

    # Verify new jacobian frames
    jac1 = jacobians[0]
    jac2 = jacobians[1]
    self.check_j_frame(jac1, expect_dof)
    self.check_j_frame(jac2, expect_dof)

    # Same as above
    self.assertAlmostEqual(jac1[0], 0.0, delta=0.01)
    self.assertAlmostEqual(jac1[1], 0.0, delta=0.01)
    self.assertAlmostEqual(jac1[2], 0.0, delta=0.01)
    self.assertAlmostEqual(jac1[3], 0.0, delta=0.01)
    self.assertAlmostEqual(jac1[4], 0.0, delta=0.01)
    self.assertAlmostEqual(jac1[5], 1.0, delta=0.01)
    self.assertAlmostEqual(jac2[0], -0.1438, delta=0.01)
    self.assertAlmostEqual(jac2[1], 0.2633, delta=0.01)
    self.assertAlmostEqual(jac2[2], 0.0, delta=0.01)
    self.assertAlmostEqual(jac2[3], 0.0, delta=0.01)
    self.assertAlmostEqual(jac2[4], 0.0, delta=0.01)
    self.assertAlmostEqual(jac2[5], 1.0, delta=0.01)

  def testJacobianHexapodSmallPartialLeg(self):
    """
    TODO: Document
    """

    # construct body
    self.addX5_4()
    self.addHexapodShoulder()

    # check body dimensions
    expect_frames = 2
    expect_dof = 1
    self.assertEqual(expect_frames, self._kin.get_frame_count(FrameTypeOutput))
    self.assertEqual(expect_dof, self._kin.dof_count)

    # set base frame and check if set successfuly
    base_trans = np.array(
      [
        [0.866, -0.5, 0, .16195],
        [0.5, 0.866, 0, 0.0935],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
      ], np.float64)
    self._kin.base_frame = base_trans
    self.check_transform_matrix(self._kin.base_frame, base_trans)

    # create array of positions
    angles = np.array([0], np.float64)

    # solve for jacobians at position and check result length and type
    jacobians = self._kin.get_jacobians(FrameTypeOutput, angles)
    self.check_j_result(jacobians, expect_frames)

    # Check jacobian frame types and dimensions
    jac1 = jacobians[0]
    jac2 = jacobians[1]
    self.check_j_frame(jac1, expect_dof)
    self.check_j_frame(jac2, expect_dof)

    # Check jacobian frame values
    self.assertAlmostEqual(jac1[0], 0.0, delta=0.001)
    self.assertAlmostEqual(jac1[1], 0.0, delta=0.001)
    self.assertAlmostEqual(jac1[2], 0.0, delta=0.001)
    self.assertAlmostEqual(jac1[3], 0.0, delta=0.001)
    self.assertAlmostEqual(jac1[4], 0.0, delta=0.001)
    self.assertAlmostEqual(jac1[5], 1.0, delta=0.001)
    self.assertAlmostEqual(jac2[0], 0.0195, delta=0.001)
    self.assertAlmostEqual(jac2[1], 0.0113, delta=0.001)
    self.assertAlmostEqual(jac2[2], 0.0, delta=0.001)
    self.assertAlmostEqual(jac2[3], 0.0, delta=0.001)
    self.assertAlmostEqual(jac2[4], 0.0, delta=0.001)
    self.assertAlmostEqual(jac2[5], 1.0, delta=0.001)

    # Change position value(s), resolve, and reverify result type and frame count
    angles[0] = 0.7
    jacobians = self._kin.get_jacobians(FrameTypeOutput, angles)
    self.check_j_result(jacobians, expect_frames)

    # Verify new jacobian frames
    jac1 = jacobians[0]
    jac2 = jacobians[1]
    self.check_j_frame(jac1, expect_dof)
    self.check_j_frame(jac2, expect_dof)

    # Same as above
    self.assertAlmostEqual(jac1[0], 0.0, delta=0.001)
    self.assertAlmostEqual(jac1[1], 0.0, delta=0.001)
    self.assertAlmostEqual(jac1[2], 0.0, delta=0.001)
    self.assertAlmostEqual(jac1[3], 0.0, delta=0.001)
    self.assertAlmostEqual(jac1[4], 0.0, delta=0.001)
    self.assertAlmostEqual(jac1[5], 1.0, delta=0.001)
    self.assertAlmostEqual(jac2[0], 0.0077, delta=0.001)
    self.assertAlmostEqual(jac2[1], 0.0212, delta=0.001)
    self.assertAlmostEqual(jac2[2], 0.0, delta=0.001)
    self.assertAlmostEqual(jac2[3], 0.0, delta=0.001)
    self.assertAlmostEqual(jac2[4], 0.0, delta=0.001)
    self.assertAlmostEqual(jac2[5], 1.0, delta=0.001)

    # Solve for forward kinematics and verify result type and frame count
    frames = self._kin.get_forward_kinematics(FrameTypeOutput, angles)
    self.check_fk_result(frames, expect_frames)

    # verify kinematics frames
    frame1 = frames[0]
    frame2 = frames[1]
    self.check_frame(frame1)
    self.check_frame(frame2)

    rot1 = [0.3402, -0.9403, 0,
            0.9403, 0.3402, 0,
            0, 0, 1]
    rot2 = [0.3402, 0, -0.9403,
            0.9403, 0, 0.3402,
            0, -1, 0]
    self.check_translate(frame1, 0.16, 0.0935, 0.0311)
    self.check_translate(frame2, 0.1831, 0.0858, 0.0861)
    self.check_last_row(frame1)
    self.check_last_row(frame2)
    self.check_rot(frame1, rot1)
    self.check_rot(frame2, rot2)

  def testJacobianHexapodLeg(self):
    """
    TODO: Document
    """

    # construct body
    self.addX5_4()
    self.addHexapodShoulder()
    self.addX5_4()
    self.addX5_8Link(0.279, math.pi)
    self.addX5_4()
    self.addX5_8Link(0.276, 0)

    # check body dimensions
    expect_frames = 6
    expect_dof = 3
    self.assertEqual(expect_frames, self._kin.get_frame_count(FrameTypeOutput))
    self.assertEqual(expect_dof, self._kin.dof_count)

    # 108/6 = 18
    # 96/16 = 6

    # set base frame and check if set successfuly
    base_trans = np.matrix(
      [
        [0.866, -0.5, 0.0, .16195],
        [0.5, 0.866, 0, 0.0935],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
      ], np.float64)
    self._kin.base_frame = base_trans
    self.check_transform_matrix(self._kin.base_frame, base_trans)

    # create array of positions
    angles = np.array([0, 0, 0], np.float64)

    # Solve for forward kinematics and verify result type and frame count
    frames = self._kin.get_forward_kinematics(FrameTypeOutput, angles)
    self.check_fk_result(frames, expect_frames)

    # verify kinematics frames
    frame1 = frames[0]
    frame2 = frames[1]
    frame3 = frames[2]
    frame4 = frames[3]
    frame5 = frames[4]
    frame6 = frames[5]
    self.check_frame(frame1)
    self.check_frame(frame2)
    self.check_frame(frame3)
    self.check_frame(frame4)
    self.check_frame(frame5)
    self.check_frame(frame6)

    self.check_translate(frame1, 0.162, 0.0935, 0.0311)
    self.check_last_row(frame1)
    self.check_rot(frame1,
      [
        cos(math.pi / 6.0), -sin(math.pi / 6.0), 0,
        sin(math.pi / 6.0), cos(math.pi / 6.0), 0,
        0, 0, 1]) # /frame1
    self.check_translate(frame2, 0.1732, 0.0740, 0.0861)
    self.check_last_row(frame2)
    self.check_rot(frame2,
      [
        cos(math.pi / 6.0), 0, -sin(math.pi / 6.0),
        sin(math.pi / 6.0), 0, cos(math.pi / 6.0),
        0, -1, 0]) # /frame2
    self.check_translate(frame3, 0.1577, 0.1009, 0.0861)
    self.check_last_row(frame3)
    self.check_rot(frame3,
      [
        cos(math.pi / 6.0), 0, -sin(math.pi / 6.0),
        sin(math.pi / 6.0), 0, cos(math.pi / 6.0),
        0, -1, 0]) # /frame3
    self.check_translate(frame4, 0.3993, 0.2404, 0.0861)
    self.check_last_row(frame4)
    self.check_rot(frame4,
      [
        cos(math.pi / 6.0), 0, sin(math.pi / 6.0),
        sin(math.pi / 6.0), 0, -cos(math.pi / 6.0),
        0, 1, 0]) # /frame4
    self.check_translate(frame5, 0.4148, 0.2135, 0.0861)
    self.check_last_row(frame5)
    self.check_rot(frame5,
      [
        cos(math.pi / 6.0), 0, sin(math.pi / 6.0),
        sin(math.pi / 6.0), 0, -cos(math.pi / 6.0),
        0, 1, 0]) # /frame5
    self.check_translate(frame6, 0.6713, 0.3212, 0.0861)
    self.check_last_row(frame6)
    self.check_rot(frame6,
      [
        cos(math.pi / 6.0), 0, sin(math.pi / 6.0),
        sin(math.pi / 6.0), 0, -cos(math.pi / 6.0),
        0, 1, 0]) # /frame6

    # solve for jacobians at position and check result length and type
    jacobians = self._kin.get_jacobians(FrameTypeOutput, angles)
    self.check_j_result(jacobians, expect_frames)

    # Check jacobian frame types and dimensions
    # Check the first column of the 1st jacobian
    # Check all 6 columns of the 6th (last) jacobian
    jac1 = jacobians[0]
    jac6 = jacobians[5]
    self.check_j_frame(jac1, expect_dof)
    self.check_j_frame(jac6, expect_dof)

    self.assertAlmostEqual(jac1[0,0], 0.0, delta=0.01)
    self.assertAlmostEqual(jac1[1,0], 0.0, delta=0.01)
    self.assertAlmostEqual(jac1[2,0], 0.0, delta=0.01)
    self.assertAlmostEqual(jac1[3,0], 0.0, delta=0.01)
    self.assertAlmostEqual(jac1[4,0], 0.0, delta=0.01)
    self.assertAlmostEqual(jac1[5,0], 1.0, delta=0.01)

    self.assertAlmostEqual(jac6[0,0], -0.2277, delta=0.01)
    self.assertAlmostEqual(jac6[0,1], 0.0, delta=0.01)
    self.assertAlmostEqual(jac6[0,2], 0.0, delta=0.01)
    self.assertAlmostEqual(jac6[1,0], 0.5094, delta=0.01)
    self.assertAlmostEqual(jac6[1,1], 0.0, delta=0.01)
    self.assertAlmostEqual(jac6[1,2], 0.0, delta=0.01)
    self.assertAlmostEqual(jac6[2,0], 0.0, delta=0.01)
    self.assertAlmostEqual(jac6[2,1], -0.555, delta=0.01)
    self.assertAlmostEqual(jac6[2,2], 0.276, delta=0.01)
    self.assertAlmostEqual(jac6[3,0], 0.0, delta=0.01)
    self.assertAlmostEqual(jac6[3,1], -0.5, delta=0.01)
    self.assertAlmostEqual(jac6[3,2], 0.5, delta=0.01)
    self.assertAlmostEqual(jac6[4,0], 0.0, delta=0.01)
    self.assertAlmostEqual(jac6[4,1], 0.866, delta=0.01)
    self.assertAlmostEqual(jac6[4,2], -0.866, delta=0.01)
    self.assertAlmostEqual(jac6[5,0], 1.0, delta=0.01)
    self.assertAlmostEqual(jac6[5,1], 0.0, delta=0.01)
    self.assertAlmostEqual(jac6[5,2], 0.0, delta=0.01)

    # Change position value(s), resolve, and reverify result type and frame count
    angles[0] = 0.187
    angles[1] = -0.313
    angles[2] = -1.906

    # Change position value(s), resolve FK, and reverify result type and frame count
    frames = self._kin.get_forward_kinematics(FrameTypeOutput, angles)
    self.check_fk_result(frames, expect_frames)

    # Only spot check last row
    frame6 = frames[5]
    self.check_translate(frame6, 0.3960, 0.2191, -0.1040, 0.01)
    self.check_last_row(frame6)
    self.check_rot(frame6,
      [
        -0.0168, 0.7578, 0.6523,
        -0.0145, 0.6521, -0.7579,
        -0.9998, -0.0222, 0.0
      ])

    # Solve FK for CoM and verify result type and frame count (FrameTypeCenterOfMass)
    frames = self._kin.get_forward_kinematics(FrameTypeCenterOfMass, angles)
    self.check_fk_result(frames, expect_frames)

    # Only spot check last row
    frame6 = frames[5]
    self.check_translate(frame6, 0.3869, 0.2343, 0.0340, 0.01)
    self.check_last_row(frame6)
    self.check_rot(frame6,
      [
        -0.0168, 0.7578, 0.6523,
        -0.0145, 0.6521, -0.7579,
        -0.9998, -0.0222, 0.0
      ])

  def testTestMasses(self):
    """
    TODO: Document
    """

    # construct body
    self.addX5_4()

    # check masses
    expect_mass_count = 1
    expect_masses = [0.335]
    self.check_almost_equal(expect_masses, self._kin.masses)
    self.assertEqual(expect_mass_count, self._kin.get_frame_count(FrameTypeCenterOfMass))

    # mutate body
    self.addX5_4()

    # check masses
    expect_mass_count = 2
    expect_masses.append(0.335)
    self.check_almost_equal(expect_masses, self._kin.masses)
    self.assertEqual(expect_mass_count, self._kin.get_frame_count(FrameTypeCenterOfMass))

    # Add a massless joint to the end (don't combine this)
    self._kin.add_joint(JointTypeRotationX, False)

    # check masses
    # Masses and frame count don't change - don't mutate expect_mass* variables
    self.check_almost_equal(expect_masses, self._kin.masses)
    self.assertEqual(expect_mass_count, self._kin.get_frame_count(FrameTypeCenterOfMass))

    # mutate further: Add a massless joint to the end (combine this)
    self._kin.add_joint(JointTypeRotationX, True)

    # check masses
    # Masses and frame count don't change - don't mutate expect_mass* variables
    self.check_almost_equal(expect_masses, self._kin.masses)
    self.assertEqual(expect_mass_count, self._kin.get_frame_count(FrameTypeCenterOfMass))

    # Add a 1kg massy body to the end; combine this (with the two massless joints)
    # CoM = {0.0, 0.0, 0.0}, so identity matrix is all that we need
    com = np.identity(4)
    inertia = np.array([.01, 0.01, 0.01, 0.0, 0.0, 0.0], np.float64)
    # x = y = 1, everything else is zero
    outputs = np.identity(4)
    outputs[0,3] = outputs[1,3] = 1.0
    self._kin.add_rigid_body(com, inertia, 1.0, outputs, True)

    # check masses
    expect_mass_count = 3
    expect_masses.append(1.0)
    self.check_almost_equal(expect_masses, self._kin.masses)
    self.assertEqual(expect_mass_count, self._kin.get_frame_count(FrameTypeCenterOfMass))

    # Add a 1kg massy body to the end; don't combine!
    self._kin.add_rigid_body(com, inertia, 1.0, outputs, False)

    # check masses
    expect_mass_count = 4
    expect_masses.append(1.0)
    self.check_almost_equal(expect_masses, self._kin.masses)
    self.assertEqual(expect_mass_count, self._kin.get_frame_count(FrameTypeCenterOfMass))

    # Combine an X5 on the end
    self.combineX5_4()

    # check masses
    # Mass was combined into last one, so add 0.335 to it (mass of x5-4)
    expect_masses[expect_mass_count-1] = expect_masses[expect_mass_count-1] + 0.335
    self.check_almost_equal(expect_masses, self._kin.masses)
    self.assertEqual(expect_mass_count, self._kin.get_frame_count(FrameTypeCenterOfMass))

################################################################################
# Tests adapted from C API `ik.cpp`
################################################################################

  def testBasic2DOF(self):
    """
    Verify that a simple (technically overconstrained) end effector position
    can be found for a 2 DOF arm
    """

    # construct body
    self.addX5_4()
    self.addX5_8Link(0.25, 0)
    self.addX5_4()
    self.addX5_8Link(0.25, 0)

    # check body dimensions
    expect_frames = 4
    expect_dof = 2
    self.assertEqual(expect_frames, self._kin.get_frame_count(FrameTypeOutput))
    self.assertEqual(expect_dof, self._kin.dof_count)

    # create array of positions
    seed_angles = np.array([0, 0], np.float64)

    # Target positions (technically overconstrained)
    position_objective = endeffector_position_objective([0.0, 0.0, 0.0])

    # Solve IK and verify result
    final_angles = self._kin.solve_inverse_kinematics(seed_angles, position_objective)
    self.check_ik_result(final_angles, seed_angles)

    # Solve FK and verify result
    frames = self._kin.get_forward_kinematics(FrameTypeOutput, final_angles)
    self.check_fk_result(frames, expect_frames)

    # verify kinematics frames
    frame1 = frames[0]
    self.check_frame(frame1)
    self.check_last_row(frame1)
    # Starting at 0,0 is ill-conditioned, per the comments in the C API test.
    # So this check fails, as x=0.0, not 1.0. Talk to Matt about this.
    #self.check_translate(frame1, 1.0, 0.0, 0.0)

    # Resolve with different seed angle(s)
    seed_angles[1] = 0.1

    # Solve IK and verify result
    final_angles = self._kin.solve_inverse_kinematics(seed_angles, position_objective)
    self.check_ik_result(final_angles, seed_angles)

    # Solve FK and verify result
    frames = self._kin.get_forward_kinematics(FrameTypeOutput, final_angles)
    self.check_fk_result(frames, expect_frames)

    # verify last frame
    frame4 = frames[3]
    self.check_frame(frame4)
    self.check_last_row(frame4)
    self.check_translate(frame4, 0.0, 0.0, NaN)

  def testReplaceObjective(self):
    """
    Ensure that objectives are overwritten properly
    (so the new ones take effect)
    """

    # construct body
    self.addX5_4()
    self.addX5_8Link(0.25, 0)
    self.addX5_4()
    self.addX5_8Link(0.25, 0)

    # check body dimensions
    expect_frames = 4
    expect_dof = 2
    self.assertEqual(expect_frames, self._kin.get_frame_count(FrameTypeOutput))
    self.assertEqual(expect_dof, self._kin.dof_count)

    # create array of positions
    seed_angles = np.array([0, 0.1], np.float64)

    # Target positions (technically overconstrained)
    position_objective = endeffector_position_objective([0.0, 0.0, 0.0])

    # Solve IK and verify result
    final_angles = self._kin.solve_inverse_kinematics(seed_angles, position_objective)
    self.check_ik_result(final_angles, seed_angles)

    # Assign new objective - result should be different
    position_objective = endeffector_position_objective([0.25, 0.0, 0.0])

    # Solve IK and verify result
    final_angles = self._kin.solve_inverse_kinematics(seed_angles, position_objective)
    self.check_ik_result(final_angles, seed_angles)

    # Solve FK and verify result
    frames = self._kin.get_forward_kinematics(FrameTypeOutput, final_angles)
    self.check_fk_result(frames, expect_frames)

    # Ensure new objective is used by verifying last frame
    frame4 = frames[3]
    self.check_frame(frame4)
    self.check_last_row(frame4)
    self.check_translate(frame4, 0.25, 0.0, NaN)

  def testTipPositionWithNaN(self):
    """
    Ensure using "NaN" value can be used to allow one dimensions
    of end effector position to be unconstrained
    """

    # construct body
    self.addX5_4()
    self.addX5_8Link(0.25, 0)
    self.addX5_4()
    self.addX5_8Link(0.25, 0)

    # check body dimensions
    expect_frames = 4
    expect_dof = 2
    self.assertEqual(expect_frames, self._kin.get_frame_count(FrameTypeOutput))
    self.assertEqual(expect_dof, self._kin.dof_count)

    # create array of positions
    seed_angles = np.array([0, 0.1], np.float64)

    # Target positions (technically overconstrained)
    position_objective = endeffector_position_objective([NaN, 0.1, 0.0])

    # Solve IK and verify result
    final_angles = self._kin.solve_inverse_kinematics(seed_angles, position_objective)
    self.check_ik_result(final_angles, seed_angles)

    # Solve FK and verify result
    frames = self._kin.get_forward_kinematics(FrameTypeOutput, final_angles)
    self.check_fk_result(frames, expect_frames)

    # verify kinematics frames
    frame4 = frames[3]
    self.check_frame(frame4)
    self.check_last_row(frame4)
    self.check_translate(frame4, NaN, 0.1, NaN)

    # Try a different objective and verify
    position_objective = endeffector_position_objective([0.1, NaN, 0.0])

    # Solve IK and verify result
    final_angles = self._kin.solve_inverse_kinematics(seed_angles, position_objective)
    self.check_ik_result(final_angles, seed_angles)

    # Solve FK and verify result
    frames = self._kin.get_forward_kinematics(FrameTypeOutput, final_angles)
    self.check_fk_result(frames, expect_frames)

    # verify kinematics frames
    frame4 = frames[3]
    self.check_frame(frame4)
    self.check_last_row(frame4)
    self.check_translate(frame4, 0.1, NaN, NaN)

  def testJointLimits(self):
    """
    Ensure that joint limits properly force an elbow
    up or down solution for a simple 2 DOF arm
    """

    # construct body
    self.addX5_4()
    self.addX5_8Link(0.25, 0)
    self.addX5_4()
    self.addX5_8Link(0.25, 0)

    # check body dimensions
    expect_frames = 4
    expect_dof = 2
    self.assertEqual(expect_frames, self._kin.get_frame_count(FrameTypeOutput))
    self.assertEqual(expect_dof, self._kin.dof_count)

    # create array of positions
    seed_angles = np.array([0, 0.1], np.float64)
    mins = np.array([0, -Inf], np.float64)
    maxs = np.array([PI * 0.5, Inf], np.float64)

    # Looking for the "up elbow" position here
    position_objective = endeffector_position_objective([0.4, 0.0, 0.0])
    joint_constraint = joint_limit_constraint(mins, maxs)

    # Solve IK and verify result
    final_angles = self._kin.solve_inverse_kinematics(seed_angles, position_objective, joint_constraint)
    self.check_ik_result(final_angles, seed_angles)
    self.assertTrue(final_angles[0] > 0.0)

    # Solve FK and verify result
    frames = self._kin.get_forward_kinematics(FrameTypeOutput, final_angles)
    self.check_fk_result(frames, expect_frames)

    # verify kinematics frames
    frame4 = frames[3]
    self.check_frame(frame4)
    self.check_last_row(frame4)
    self.check_translate(frame4, 0.4, 0.0, NaN)

    # Update joint angles
    mins[0] = -PI * 0.5
    maxs[0] = 0.0
    joint_constraint = joint_limit_constraint(mins, maxs)

    # Solve IK and verify result
    # Looking for the "down elbow" position here
    final_angles = self._kin.solve_inverse_kinematics(seed_angles, position_objective, joint_constraint)
    self.check_ik_result(final_angles, seed_angles)
    self.assertTrue(final_angles[0] < 0.0)

    # Solve FK and verify result
    frames = self._kin.get_forward_kinematics(FrameTypeOutput, final_angles)
    self.check_fk_result(frames, expect_frames)

    # verify kinematics frames
    frame4 = frames[3]
    self.check_frame(frame4)
    self.check_last_row(frame4)
    self.check_translate(frame4, 0.4, 0.0, NaN)

  def test3DOFTipAxis(self):
    """
    Find a solution for end effector tip orientation
    using 3 DOF wrist (underconstrained)
    """

    # construct body
    self.addX5_4()
    self.addBracket('X5-LightBracket', 'left')
    self.addX5_4()
    self.addBracket('X5-LightBracket', 'left')
    self.addX5_4()

    # check body dimensions
    expect_frames = 5
    expect_dof = 3
    self.assertEqual(expect_frames, self._kin.get_frame_count(FrameTypeOutput))
    self.assertEqual(expect_dof, self._kin.dof_count)

    # create array of positions
    seed_angles = np.array([0, 0.1, -0.1], np.float64)

    # Norm of [0.4, 0.4, 1.0]
    tipaxis_objective = endeffector_tipaxis_objective([0.3482, 0.3482, 0.8704])

    # Solve IK and verify result
    final_angles = self._kin.solve_inverse_kinematics(seed_angles, tipaxis_objective)
    self.check_ik_result(final_angles, seed_angles)

    # Solve FK and verify result
    frames = self._kin.get_forward_kinematics(FrameTypeOutput, final_angles)
    self.check_fk_result(frames, expect_frames)

    # verify kinematics frame
    frame5 = frames[4]
    self.check_frame(frame5)
    self.check_last_row(frame5)
    self.assertAlmostEqual(frame5[0,2], 0.3482, delta=0.0001)
    self.assertAlmostEqual(frame5[1,2], 0.3482, delta=0.0001)
    self.assertAlmostEqual(frame5[2,2], 0.8704, delta=0.0001)

  def test3DOFSO3(self):
    """
    Find a solution for end effector orientation of a 3 DOF wrist
    """

    # construct body
    self.addX5_4()
    self.addBracket('X5-LightBracket', 'left')
    self.addX5_4()
    self.addBracket('X5-LightBracket', 'left')
    self.addX5_4()

    # check body dimensions
    expect_frames = 5
    expect_dof = 3
    self.assertEqual(expect_frames, self._kin.get_frame_count(FrameTypeOutput))
    self.assertEqual(expect_dof, self._kin.dof_count)

    # create array of positions
    seed_angles = np.array([0, 0.1, 0.1], np.float64)

    theta = 0.5
    rot_y = [
      cos(theta), 0.0, sin(theta),
      0.0, 1.0, 0.0,
      -sin(theta), 0.0, cos(theta)
    ]
    so3_objective = endeffector_so3_objective(rot_y)

    # Solve IK and verify result
    final_angles = self._kin.solve_inverse_kinematics(seed_angles, so3_objective)
    self.check_ik_result(final_angles, seed_angles)

    # Solve FK and verify result
    frames = self._kin.get_forward_kinematics(FrameTypeOutput, final_angles)
    self.check_fk_result(frames, expect_frames)

    # verify kinematics frame
    frame5 = frames[4]
    self.check_frame(frame5)
    self.check_last_row(frame5)
    self.check_rot(frame5, rot_y)

  def test6DOFxyz(self):
    """
    Ensure we can find an (underconstrained) solution for end effector position
    """

    # construct body
    self.addX5_4()
    self.addBracket('X5-LightBracket', 'right')
    self.addX5_4()
    self.addX5_8Link(0.25, 0.0)
    self.addX5_4()
    self.addX5_8Link(0.25, 0.0)
    self.addX5_4()
    self.addBracket('X5-LightBracket', 'right')
    self.addX5_4()
    self.addBracket('X5-LightBracket', 'left')
    self.addX5_4()

    # check body dimensions
    expect_frames = 11
    expect_dof = 6
    self.assertEqual(expect_frames, self._kin.get_frame_count(FrameTypeOutput))
    self.assertEqual(expect_dof, self._kin.dof_count)

    # create array of positions
    seed_angles = np.array([1.3, 0.1173, -2.1971, 3.4298, 0.0, 0.05], np.float64)

    # Target positions (technically overconstrained)
    position_objective = endeffector_position_objective([0.25, 0.0, 0.25])

    # Solve IK and verify result
    final_angles = self._kin.solve_inverse_kinematics(seed_angles, position_objective)
    self.check_ik_result(final_angles, seed_angles)

    # Solve FK and verify result
    frames = self._kin.get_forward_kinematics(FrameTypeOutput, final_angles)
    self.check_fk_result(frames, expect_frames)

    # verify kinematics frame
    frame11 = frames[10]
    self.check_frame(frame11)
    self.check_last_row(frame11)
    self.check_translate(frame11, 0.25, 0.0, 0.25)

    # Change objective and try again
    # Target positions (technically overconstrained)
    position_objective = endeffector_position_objective([0.15, 0.15, -0.15])

    # Solve IK and verify result
    final_angles = self._kin.solve_inverse_kinematics(seed_angles, position_objective)
    self.check_ik_result(final_angles, seed_angles)

    # Solve FK and verify result
    frames = self._kin.get_forward_kinematics(FrameTypeOutput, final_angles)
    self.check_fk_result(frames, expect_frames)

    # verify kinematics frame
    frame11 = frames[10]
    self.check_frame(frame11)
    self.check_last_row(frame11)
    self.check_translate(frame11, 0.15, 0.15, -0.15)

  def test6DOFxyzAndSO3(self):
    """
    Ensure that we can find a solution for end effector position
    and orientation (assuming the target is in the workspace)
    """

    # construct body
    self.addX5_4()
    self.addBracket('X5-LightBracket', 'right')
    self.addX5_4()
    self.addX5_8Link(0.25, 0.0)
    self.addX5_4()
    self.addX5_8Link(0.25, 0.0)
    self.addX5_4()
    self.addBracket('X5-LightBracket', 'right')
    self.addX5_4()
    self.addBracket('X5-LightBracket', 'left')
    self.addX5_4()

    # check body dimensions
    expect_frames = 11
    expect_dof = 6
    self.assertEqual(expect_frames, self._kin.get_frame_count(FrameTypeOutput))
    self.assertEqual(expect_dof, self._kin.dof_count)

    # create array of positions
    seed_angles = np.array([1.3, 0.1173, -2.1971, 3.4298, 0.0, 0.05], np.float64)

    # SO3 objective
    theta = 0.5
    rot_y = [
      cos(theta), 0.0, sin(theta),
      0.0, 1.0, 0.0,
      -sin(theta), 0.0, cos(theta)
    ]
    so3_objective = endeffector_so3_objective(rot_y)

    # Target positions (technically overconstrained)
    position_objective = endeffector_position_objective([0.35, 0.0, 0.25])

    # Solve IK and verify result
    final_angles = self._kin.solve_inverse_kinematics(seed_angles, so3_objective, position_objective)
    self.check_ik_result(final_angles, seed_angles)

    # Solve FK and verify result
    frames = self._kin.get_forward_kinematics(FrameTypeOutput, final_angles)
    self.check_fk_result(frames, expect_frames)

    # verify kinematics frame
    frame11 = frames[10]
    self.check_frame(frame11)
    self.check_last_row(frame11)
    self.check_translate(frame11, 0.35, 0.0, 0.25)
    self.check_rot(frame11, rot_y)

################################################################################
# Python Specific tests
################################################################################

  def testActuatorParser(self):
    """
    Test internal parser for ``add_actuator`` function
    """
    self._kin.add_actuator('X5-1')
    self._kin.add_actuator('X5-4')
    self._kin.add_actuator('X5-9')
    self._kin.add_actuator('X8-3')
    self._kin.add_actuator('X8-9')
    self._kin.add_actuator('X8-16')

    self.assertEqual(self._kin.get_frame_count(FrameTypeOutput), 6)
    self.assertEqual(self._kin.dof_count, 6)
    masses = self._kin.masses

    self.assertIsNotNone(masses)
    self.assertEqual(len(masses), 6)
    self.assertAlmostEqual(masses[0], 0.315, delta=0.0001) # X5-1
    self.assertAlmostEqual(masses[1], 0.335, delta=0.0001) # X5-4
    self.assertAlmostEqual(masses[2], 0.360, delta=0.0001) # X5-9
    self.assertAlmostEqual(masses[3], 0.460, delta=0.0001) # X8-3
    self.assertAlmostEqual(masses[4], 0.480, delta=0.0001) # X8-9
    self.assertAlmostEqual(masses[5], 0.500, delta=0.0001) # X8-16

    # Test lowercase works too
    self._kin.add_actuator('x5-1')
    self.assertEqual(self._kin.get_frame_count(FrameTypeOutput), 7)
    self.assertEqual(self._kin.dof_count, 7)
    masses = self._kin.masses
    self.assertIsNotNone(masses)
    self.assertEqual(len(masses), 7)
    self.assertAlmostEqual(masses[6], 0.315, delta=0.0001) # X5-1

  def testInvalidActuatorParserValues(self):
    """
    Test invalid values for internal ``add_actuator`` parser
    """
    with self.assertRaises(ValueError):
      self._kin.add_actuator('foo')
    with self.assertRaises(TypeError):
      self._kin.add_actuator(420)
    with self.assertRaises(TypeError):
      self._kin.add_actuator(None)
    with self.assertRaises(TypeError):
      self._kin.add_actuator(dict())

  def testAddLink(self):
    """
    Test internal parser for ``add_link`` function
    """
    self._kin.add_link('X5', 0.5, 0.0)
    self._kin.add_link('X8', 0.5, 0.0)
    self._kin.add_link('x5', 0.5, 0.0)
    self._kin.add_link('x8', 0.5, 0.0)

    self.assertEqual(self._kin.get_frame_count(FrameTypeOutput), 4)
    self.assertEqual(self._kin.dof_count, 0)

  def testInvalidLinkParserValues(self):
    """
    Test invalid values for internal ``add_link`` parser
    """
    with self.assertRaises(ValueError):
      self._kin.add_link('foo', 0.5, 0.0)
    with self.assertRaises(TypeError):
      self._kin.add_link(420, 0.5, 0.0)
    with self.assertRaises(TypeError):
      self._kin.add_link(None, 0.5, 0.0)
    with self.assertRaises(ValueError):
      self._kin.add_link('X5', 'foo', 0.0)
    with self.assertRaises(ValueError):
      self._kin.add_link('X5', 0.5, 'foo')
    with self.assertRaises(ValueError):
      self._kin.add_link('X5', 'foo', 'foo')
    with self.assertRaises(TypeError):
      self._kin.add_link('X5', None, 0.0)
    with self.assertRaises(TypeError):
      self._kin.add_link('X5', 0.5, None)
    with self.assertRaises(TypeError):
      self._kin.add_link('X5', None, None)

  def testAddBracket(self):
    """
    Test internal parser for ``add_bracket`` function
    """
    self._kin.add_bracket('X5-LightBracket', 'left')
    self._kin.add_bracket('X5-LightBracket', 'right')
    self._kin.add_bracket('X5-HeavyBracket', 'left-inside')
    self._kin.add_bracket('X5-HeavyBracket', 'right-inside')
    self._kin.add_bracket('X5-HeavyBracket', 'left-outside')
    self._kin.add_bracket('X5-HeavyBracket', 'right-outside')
    # Test that `mount` parameter is case insensitive
    self._kin.add_bracket('X5-LightBracket', 'LEFT')
    self._kin.add_bracket('X5-LightBracket', 'Right')
    self._kin.add_bracket('X5-HeavyBracket', 'RIGHT-OUTSIDE')

    self.assertEqual(self._kin.get_frame_count(FrameTypeOutput), 9)
    self.assertEqual(self._kin.dof_count, 0)

  def testInvalidBracketParserValues(self):
    """
    Test invalid values for internal ``add_bracket`` parser
    """
    with self.assertRaises(TypeError):
      self._kin.add_bracket('X5-LightBracket', None)
    with self.assertRaises(TypeError):
      self._kin.add_bracket(None, 'right-inside')
    with self.assertRaises(TypeError):
      self._kin.add_bracket(None, None)
    with self.assertRaises(TypeError):
      self._kin.add_bracket('X5-LightBracket', 420)
    with self.assertRaises(TypeError):
      self._kin.add_bracket(420, 'right-inside')
    with self.assertRaises(TypeError):
      self._kin.add_bracket(420, 420)
    with self.assertRaises(ValueError):
      # X8-[Light|Heavy]Bracket isn't valid for now...
      self._kin.add_bracket('X8-LightBracket', 'left')
    with self.assertRaises(ValueError):
      self._kin.add_bracket('X5-LightBracket', 'foo')
    with self.assertRaises(ValueError):
      self._kin.add_bracket('foo', 'foo')


def __load_hebi():
  # Force add the current directory as a package, which will in return
  # import the `hebi` package from this repository, taking precedence over
  # any user installed variant of the hebi-py API
  if __package__ == None:
    from os.path import abspath, dirname
    from importlib import import_module
    import sys
    sys.path = [dirname(dirname(abspath(__file__)))] + sys.path
    import_module('test')


def main():
  __load_hebi()
  unittest.main()


if __name__ == '__main__':
  __load_hebi()

from hebi.robot_model import (FrameTypeOutput, FrameTypeCenterOfMass, RobotModel,
                              JointTypeRotationX,
                              endeffector_position_objective,
                              endeffector_so3_objective,
                              endeffector_tipaxis_objective,
                              joint_limit_constraint)

if __name__ == '__main__':
  main()
