import unittest
import math
import numpy as np

from math import (cos, sin, isinf, isnan)

NaN = np.nan
Inf = np.inf
PI = math.pi

class UnconstrainedQpTrajectoryTestCase(unittest.TestCase):

  def check_state_result(self, p, v, a, num_joints):
    """
    Check type and dimensionality of a given trajectory ``get_state`` result
    """
    self.assertIsNotNone(p)
    self.assertIsNotNone(v)
    self.assertIsNotNone(a)
    self.assertIsInstance(p, np.ndarray)
    self.assertIsInstance(v, np.ndarray)
    self.assertIsInstance(a, np.ndarray)
    self.assertEqual(len(p), num_joints)
    self.assertEqual(len(v), num_joints)
    self.assertEqual(len(a), num_joints)

  def check_almost_equal(self, a, b, delta=0.01):
    """
    Utility function to use ``assertAlmostEqual`` on each element
    in two iterable objects of the same length
    """
    self.assertEqual(len(a), len(b))
    for i in range(0, len(a)):
      self.assertAlmostEqual(a[i], b[i], delta=delta)

################################################################################
# Adapted from `trajectory1.cpp` tests from C API
################################################################################

  def testSingleJointWithDefaultConstraints(self):
    """
    TODO: Document
    """
    from hebi.trajectory import create_trajectory

    num_waypoints = 4
    num_joints = 1
    times = [0.0, 3.0, 9.0, 10.0]
    positions = [0.0, 1.0, 2.0, 3.0]
    velocities = [0.0, None, None, 0]
    accelerations = [0.0, None, None, 0]
    trajectory = create_trajectory(times, positions, velocities, accelerations)

    # Validate trajectory fields
    self.assertIsNotNone(trajectory)
    self.assertEqual(trajectory.number_of_waypoints, num_waypoints)
    self.assertEqual(trajectory.number_of_joints, num_joints)
    self.assertAlmostEqual(trajectory.start_time, times[0])
    self.assertAlmostEqual(trajectory.end_time, times[-1])

    # Verify trajectory duration
    self.assertAlmostEqual(times[-1] - times[0], trajectory.duration, delta=0.001)

    # Verify beginning state
    p, v, a = trajectory.get_state(0.0)
    self.check_state_result(p, v, a, num_joints)
    self.check_almost_equal(p, [0.0])
    self.check_almost_equal(v, [0.0])
    self.check_almost_equal(a, [0.0])

    p, v, a = trajectory.get_state(2.0)
    self.check_state_result(p, v, a, num_joints)
    self.check_almost_equal(p, [0.7144])
    self.check_almost_equal(v, [0.5682])
    self.check_almost_equal(a, [-0.2681])

    p, v, a = trajectory.get_state(8.0)
    self.check_state_result(p, v, a, num_joints)
    self.check_almost_equal(p, [-0.4147])
    self.check_almost_equal(v, [2.2651])
    self.check_almost_equal(a, [0.9575])

    p, v, a = trajectory.get_state(10.0)
    self.check_state_result(p, v, a, num_joints)
    self.check_almost_equal(p, [3.0])
    self.check_almost_equal(v, [0.0])
    self.check_almost_equal(a, [0.0])

  def testStraightLineTrajectory(self):
    """
    TODO: Document
    """
    from hebi.trajectory import create_trajectory

    num_waypoints = 4
    num_joints = 1
    times = [0.0, 1.0, 2.0, 3.0]
    positions = [0.0, 1.0, 2.0, 3.0]
    velocities = [1.0, 1.0, 1.0, 1.0]
    accelerations = [0.0, 0.0, 0.0, 0]
    trajectory = create_trajectory(times, positions, velocities, accelerations)

    # Validate trajectory fields
    self.assertIsNotNone(trajectory)
    self.assertEqual(trajectory.number_of_waypoints, num_waypoints)
    self.assertEqual(trajectory.number_of_joints, num_joints)
    self.assertAlmostEqual(trajectory.start_time, times[0])
    self.assertAlmostEqual(trajectory.end_time, times[-1])

    # Verify trajectory duration
    self.assertAlmostEqual(times[-1] - times[0], trajectory.duration, delta=0.001)

    # Verify beginning state
    p, v, a = trajectory.get_state(0.5)
    self.check_state_result(p, v, a, num_joints)
    self.check_almost_equal(p, [0.5])
    self.check_almost_equal(v, [1.0])
    self.check_almost_equal(a, [0.0])

    p, v, a = trajectory.get_state(1.1)
    self.check_state_result(p, v, a, num_joints)
    self.check_almost_equal(p, [1.1])
    self.check_almost_equal(v, [1.0])
    self.check_almost_equal(a, [0.0])

    p, v, a = trajectory.get_state(2.0)
    self.check_state_result(p, v, a, num_joints)
    self.check_almost_equal(p, [2.0])
    self.check_almost_equal(v, [1.0])
    self.check_almost_equal(a, [0.0])

    p, v, a = trajectory.get_state(3.0)
    self.check_state_result(p, v, a, num_joints)
    self.check_almost_equal(p, [3.0])
    self.check_almost_equal(v, [1.0])
    self.check_almost_equal(a, [0.0])

  def testSingleUnconstrainedValue(self):
    """
    TODO: Document
    """
    num_waypoints = 2

################################################################################
# Python Specific
################################################################################

  def testThrowOnNoneTime(self):
    from hebi.trajectory import create_trajectory
    with self.assertRaises(RuntimeError):
      result = create_trajectory(None, [1, 2, 3])
      self.fail('Unreachable statement. Trajectory: {0}'.format(result))

  def testThrowOnNonePosition(self):
    from hebi.trajectory import create_trajectory
    with self.assertRaises(RuntimeError):
      result = create_trajectory([1, 2, 3], None)
      self.fail('Unreachable statement. Trajectory: {0}'.format(result))


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
  main()
