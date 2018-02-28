# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#  HEBI Core python API - Copyright 2018 HEBI Robotics
#  See https://hebi.us/softwarelicense for license details
#
# ------------------------------------------------------------------------------


def create_trajectory(time, position, velocity=None, acceleration=None):
  """
  Creates a smooth trajectory through a set of waypoints (position
  velocity and accelerations defined at particular times). This trajectory
  wrapper object can create multi-dimensional trajectories (i.e., multiple
  joints moving together using the same time reference).

  :param time: A vector of desired times at which to reach each
               waypoint; this must be defined
               (and not ``None`` or ``nan`` for any element).
  :type time:  list, numpy.ndarray

  :param position: A matrix of waypoint joint positions (in SI units). The
                   number of rows should be equal to the number of joints,
                   and the number of columns equal to the number of waypoints. 
                   Any elements that are ``None`` or ``nan`` will be considered
                   free parameters when solving for a trajectory.
                   Values of ``+/-inf`` are not allowed.
  :type position:  str, list, numpy.ndarray, ctypes.Array
  
  :param velocity: An optional matrix of velocity constraints at the
                   corresponding waypoints; should either be ``None``
                   or matching the size of the positions matrix.
                   Any elements that are ``None`` or ``nan`` will be considered
                   free parameters when solving for a trajectory.
                   Values of ``+/-inf`` are not allowed.
  :type velocity:  NoneType, str, list, numpy.ndarray, ctypes.Array
  
  :param acceleration: An optional matrix of acceleration constraints at
                       the corresponding waypoints; should either be ``None``
                       or matching the size of the positions matrix.
                       Any elements that are ``None`` or ``nan`` will be considered
                       free parameters when solving for a trajectory.
                       Values of ``+/-inf`` are not allowed.
  :type acceleration:  NoneType, str, list, numpy.ndarray, ctypes.Array
  
  :return: The trajectory. This will never be ``None``.
  :rtype: Trajectory

  :raises ValueError: If dimensionality or size of any
                      input parameters are invalid.
  :raises RuntimeError: If trajectory could not be created.
  """
  import numpy as np
  time = np.asarray(time, np.float64)
  position = np.asmatrix(position, np.float64)

  joints = position.shape[0]
  waypoints = position.shape[1]

  if (time.size != waypoints):
    raise ValueError('length of time vector must be equal to number of waypoints')

  from ._internal.math_utils import is_finite
  if not is_finite(time):
    raise ValueError('time vector must have all finite values')

  if (type(velocity) != type(None)):
    velocity = np.asmatrix(velocity, np.float64)
    if (velocity.shape[0] != joints or velocity.shape[1] != waypoints):
      raise ValueError('Invalid dimensionality of velocities matrix')
  else:
    # First and last waypoint will have value zero - everything else NaN
    velocity = np.asmatrix(np.zeros(position.shape, np.float64))
    velocity[:, -1] = velocity[:, 0] = np.nan

  if (type(acceleration) != type(None)):
    acceleration = np.asmatrix(acceleration, np.float64)
    if (acceleration.shape[0] != joints or acceleration.shape[1] != waypoints):
      raise ValueError('Invalid dimensionality of velocities matrix')
  else:
    # First and last waypoint will have value zero - everything else NaN
    acceleration = np.asmatrix(np.zeros(position.shape, np.float64))
    acceleration[:, -1] = acceleration[:, 0] = np.nan


  from ctypes import c_double, POINTER, cast, byref
  c_double_p = POINTER(c_double)
  time_c = time.ctypes.data_as(c_double_p)
  position_c = position.getA1().ctypes.data_as(c_double_p)
  velocity_c = velocity.getA1().ctypes.data_as(c_double_p)
  acceleration_c = acceleration.getA1().ctypes.data_as(c_double_p)

  from ._internal.raw import hebiTrajectoryCreateUnconstrainedQp
  trajectories = [None] * joints

  for i in range(0, joints):

    pos_offset = cast(byref(position_c.contents, i * waypoints * 8), c_double_p)
    vel_offset = cast(byref(velocity_c.contents, i * waypoints * 8), c_double_p)
    acc_offset = cast(byref(acceleration_c.contents, i * waypoints * 8), c_double_p)

    trajectory = hebiTrajectoryCreateUnconstrainedQp(
      waypoints, pos_offset, vel_offset, acc_offset, time_c)

    if not (trajectory):
      raise RuntimeError('Could not create trajectory')
    trajectories[i] = trajectory

  from ._internal.trajectory import Trajectory
  return Trajectory(trajectories, waypoints, time[0], time[-1])
