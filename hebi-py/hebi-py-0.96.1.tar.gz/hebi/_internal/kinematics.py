# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
#
#  HEBI Core python API - Copyright 2018 HEBI Robotics
#  See https://hebi.us/softwarelicense for license details
#
# -----------------------------------------------------------------------------
'''
Internal kinematics API
'''


# ------------------------------------------------------------------------------
# Descriptor classes returned from parser functions
# ------------------------------------------------------------------------------

class ActuatorDesc(object):

  def __init__(self, name, mass, inertia):
    self._name = name
    self._mass = mass
    self._inertia = inertia

  @property
  def name(self):
    return self._name

  @property
  def mass(self):
    return self._mass

  @property
  def moments_of_inertia(self):
    import numpy as np
    return np.array(self._inertia, np.float64)


class BracketDesc(object):

  def __init__(self, name, mount, mass):
    self._name = name
    self._mount = mount
    self._mass = mass

  @property
  def name(self):
    return self._name

  @property
  def mount(self):
    return self._mount

  @property
  def mass(self):
      return self._mass


# ------------------------------------------------------------------------------
# Descriptor Classes for parsing
# ------------------------------------------------------------------------------

# TODO: Make this a bit more future proof...


class BracketParserMatch(object):

  def __init__(self, parser, mount):
    self._parser = parser
    self._mount = mount

  @property
  def bracket_name(self):
    return self._parser.name

  @property
  def light(self):
    return 'Light' in self._parser.name

  @property
  def heavy(self):
    return 'Heavy' in self._parser.name

  @property
  def left(self):
    return 'left' in self._mount

  @property
  def right(self):
    return 'right' in self._mount

  @property
  def inside(self):
    return 'inside' in self._mount

  @property
  def outside(self):
    return 'outside' in self._mount

  @property
  def mass(self):
    return self._parser.mass


class BracketParser(object):

  def __init__(self, name, mounts, mass):
    self._name = name
    self._mounts = mounts
    self._mass = mass

  def match(self, name, mount):
    if (name == self._name):
      for entry in self._mounts:
        if (mount == entry):
          return BracketParserMatch(self, mount)
    return None

  @property
  def mass(self):
    return self._mass

  @property
  def name(self):
    return self._name


# ------------------------------------------------------------------------------
# Maps and Lists for HEBI Products
# ------------------------------------------------------------------------------

# TODO: Maybe move this into a catalogue module?

__X5_moi = [ 0.00015, 0.000255, 0.000350, 0.0000341, 0.0000118, 0.00000229 ]
__X8_moi = [ 0.000246, 0.000380, 0.000463, 0.0000444, 0.0000266, 0.00000422 ]

__actuators = {
  'X5-1' : ActuatorDesc('X5-1', 0.315, __X5_moi),
  'X5-4' : ActuatorDesc('X5-4', 0.335, __X5_moi),
  'X5-9' : ActuatorDesc('X5-9', 0.360, __X5_moi),
  'X8-3' : ActuatorDesc('X8-3', 0.460, __X8_moi),
  'X8-9' : ActuatorDesc('X8-9', 0.480, __X8_moi),
  'X8-16' : ActuatorDesc('X8-16', 0.500, __X8_moi)
}

__actuator_links = {
  'X5', 'X8'
}

__brackets = [
  BracketParser('X5-LightBracket',
                ['left', 'right'], 0.1),
  BracketParser('X5-HeavyBracket',
                ['left-inside', 'right-inside',
                 'left-outside', 'right-outside'], 0.215)
]

# ------------------------------------------------------------------------------
# Parsing Functions
# ------------------------------------------------------------------------------

def __assert_str(value, name='value'):
  if not isinstance(value, str):
    raise TypeError('{0} must be a str'.format(name))


def parse_frame_type(value):
  __assert_str(value, name='frame_type')

  from .raw import FrameTypeCenterOfMass, FrameTypeEndEffector, FrameTypeOutput

  value = value.strip()
  if (value == 'CoM' or value == 'com'):
    return FrameTypeCenterOfMass
  elif (value == 'output'):
    return FrameTypeOutput
  else:
    ValueError("{0} is not a valid frame type. Valid types are 'CoM', 'com', or 'output'".format(value))


def parse_joint_type(value):
  __assert_str(value, name='joint_type')

  from .raw import JointTypeRotationX, JointTypeRotationY, JointTypeRotationZ

  value = value.strip().upper()
  if (value == 'X'):
    return JointTypeRotationX
  elif (value == 'Y'):
    return JointTypeRotationY
  elif (value == 'Z'):
    return JointTypeRotationZ
  else:
    raise ValueError("{0} is not a valid joint type. Valid types are 'X', 'Y', or 'Z'".format(value))


def parse_actuator(value):
  __assert_str(value)

  value = value.strip().upper()
  actuator = __actuators.get(value, None)
  if (not actuator):
    raise ValueError('{0} is not a valid actuator'.format(value))

  import numpy as np
  com = np.identity(4, np.float64)
  input_to_axis = np.identity(4, np.float64)

  if (actuator.name.startswith('X5')):
    set_translate(com, -0.0142, -0.0031, 0.0165)
    set_translate(input_to_axis, 0.0, 0.0, 0.03105)
  elif (actuator.name.startswith('X8')):
    set_translate(com, -0.145, -0.0031, 0.0242)
    set_translate(input_to_axis, 0.0, 0.0, 0.0451)
  return actuator, com, input_to_axis


def parse_actuator_link(value, extension, twist):
  __assert_str(value)

  value = value.strip().upper()
  if not (value in __actuator_links):
    raise ValueError('{0} is not a valid actuator link'.format(value))

  try:
    extension = float(extension)
  except ValueError as v:
    raise ValueError('cannot convert extension={0} to a float'.format(extension))
  except TypeError as t:
    raise TypeError('cannot convert extension={0} (type {1}) to a float'.format(extension, type(extension)))

  try:
    twist = float(twist)
  except ValueError as v:
    raise ValueError('cannot convert twist={0} to a float'.format(twist))
  except TypeError as t:
    raise TypeError('cannot convert twist={0} (type {1}) to a float'.format(twist, type(twist)))

  return extension, twist


def parse_bracket(bracket, mount):
  __assert_str(bracket, 'bracket')
  __assert_str(mount, 'mount')

  bracket = bracket.strip()
  mount = mount.strip().lower()

  for entry in __brackets:
    match = entry.match(bracket, mount)
    if (match):
      break
  else:
    # Should never happen, but let's make this lint-free
    match = None

  if not (match):
    raise ValueError('bracket={0} and mount={1} is not a valid bracket'.format(bracket, mount))

  import numpy as np
  com = np.identity(4, np.float64)
  output = np.identity(4, np.float64)
  mass = match.mass

  from math import pi
  neg_half_pi = pi * -0.5

  if (match.light):
    if (match.right):
      mult = -1.0
    else:
      mult = 1.0

    set_translate(com, 0.0, mult * 0.0215, 0.02)
    set_rotate_x(output, mult * neg_half_pi)
    set_translate(output, 0.0, mult * 0.043, 0.04)

  elif(match.heavy):
    if (match.right):
      lr_mult = -1.0
    else:
      lr_mult = 1.0

    if (match.outside):
      y_dist = 0.0375
    else:
      y_dist = -0.0225

    set_translate(com, 0.0, lr_mult * 0.5 * y_dist, 0.0275)
    set_rotate_x(output, lr_mult * neg_half_pi)
    set_translate(output, 0.0, lr_mult * y_dist, 0.055)

  else:
    raise RuntimeError('Unknown bracket type {0}'.format(match.bracket_name))

  return com, output, mass


# -----------------------------------------------------------------------------
# Transform Functions
# -----------------------------------------------------------------------------


def set_translate(matrix, x, y, z):
  matrix[0, 3] = x
  matrix[1, 3] = y
  matrix[2, 3] = z


def set_rotate_x(matrix, radians):
  from math import cos, sin
  matrix[0, 0] = 1.0
  matrix[0, 1] = 0.0
  matrix[0, 2] = 0.0
  matrix[1, 0] = 0.0
  matrix[1, 1] = cos(radians)
  matrix[1, 2] = -sin(radians)
  matrix[2, 0] = 0.0
  matrix[2, 1] = sin(radians)
  matrix[2, 2] = cos(radians)


def set_sphere_inertia(inertia, mass, radius):
  inertia[0:3] = 0.4 * mass * radius * radius
  inertia[3:6] = 0.0


def set_rod_x_axis_inertia(inertia, mass, length):
  inertia[1:3] = mass * length * length * 0.083333333333333333
  inertia[3:6] = inertia[0] = 0.0
