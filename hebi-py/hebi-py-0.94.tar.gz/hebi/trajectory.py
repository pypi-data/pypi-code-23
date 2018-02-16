# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
#
#  HEBI Core python API - Copyright 2018 HEBI Robotics
#  See https://hebi.us/softwarelicense for license details
#
# -----------------------------------------------------------------------------
"""
HEBI Trajectory API
-------------------
"""


def create_trajectory(time, position, velocity=None, acceleration=None):
  import numpy as np

  time = np.asarray(time, np.float64)
  position = np.asmatrix(position, np.float64)

  joints = position.shape[0]
  waypoints = position.shape[1]

  if (time.size != waypoints):
    raise RuntimeError('length of time vector must be equal to number of waypoints')

  if (type(velocity) != type(None)):
    velocity = np.asmatrix(velocity, np.float64)
    if (velocity.shape[0] != joints or velocity.shape[1] != waypoints):
      raise RuntimeError('Invalid dimensionality of velocities matrix')
  else:
    # First and last waypoint will have value zero - everything else NaN
    velocity = np.asmatrix(np.zeros(position.shape, np.float64))
    velocity[:, -1] = velocity[:, 0] = float('nan')

  if (type(acceleration) != type(None)):
    acceleration = np.asmatrix(acceleration, np.float64)
    if (acceleration.shape[0] != joints or acceleration.shape[1] != waypoints):
      raise RuntimeError('Invalid dimensionality of velocities matrix')
  else:
    # First and last waypoint will have value zero - everything else NaN
    acceleration = np.asmatrix(np.zeros(position.shape, np.float64))
    acceleration[:, -1] = acceleration[:, 0] = float('nan')


  from ctypes import c_double, POINTER, cast, byref
  c_double_p = POINTER(c_double)
  time_c = time.ctypes.data_as(c_double_p)
  position_c = position.getA1().ctypes.data_as(c_double_p)
  velocity_c = velocity.getA1().ctypes.data_as(c_double_p)
  acceleration_c = acceleration.getA1().ctypes.data_as(c_double_p)

  from ._internal.raw import hebiTrajectoryCreateUnconstrainedQp
  trajectories = [ None ] * joints

  for i in range(0, joints):

    pos_offset = cast(byref(position_c.contents, i * waypoints * 8), c_double_p)
    vel_offset = cast(byref(velocity_c.contents, i * waypoints * 8), c_double_p)
    acc_offset = cast(byref(acceleration_c.contents, i * waypoints * 8), c_double_p)

    trajectory = hebiTrajectoryCreateUnconstrainedQp(
      waypoints, pos_offset, vel_offset, acc_offset, time_c
    )

    if not (trajectory):
      raise RuntimeError('Could not create trajectory')
    trajectories[i] = trajectory


  from ._internal.trajectory import Trajectory
  return Trajectory(trajectories, waypoints, time[0], time[-1])