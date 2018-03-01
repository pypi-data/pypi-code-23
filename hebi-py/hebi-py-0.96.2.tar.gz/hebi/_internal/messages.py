# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#  HEBI Core python API - Copyright 2018 HEBI Robotics
#  See https://hebi.us/softwarelicense for license details
#
# ------------------------------------------------------------------------------
"""
HEBI data types
---------------
"""

from .raw import *
from .message_utils import *

class FakeGroupMessage(UnmanagedObject):
  """
  Used to wrap a single (non-group) message into appearing like a group.
  Do not use directly.
  """

  def __init__(self, internal):
    super(FakeGroupMessage, self).__init__(internal)

  @property
  def modules(self):
    return [self._internal]

  @property
  def size(self):
    return 1


# ------------------------------------------------------------------------------
# Field Classes
# ------------------------------------------------------------------------------


class Command(UnmanagedObject):
  """
  Used to represent a Command object.
  Do not instantiate directly - use only through a GroupCommand instance.
  """

  def __init__(self, internal):
    """
    This is invoked internally. Do not use directly.
    """
    super(Command, self).__init__(internal)
    self._fake_group = FakeGroupMessage(self._internal)

  @property
  def velocity(self):
    """
    Velocity of the module output (post-spring), in radians/second.
    """
    return get_group_command_float(self._fake_group, CommandFloatVelocity)[0]

  @property
  def effort(self):
    """
    Effort at the module output; units vary (*e.g.*, :math:`N \cdot m` for rotational joints and *N* for linear stages).
    """
    return get_group_command_float(self._fake_group, CommandFloatEffort)[0]

  @property
  def position_kp(self):
    """
    Proportional PID gain for position
    """
    return get_group_command_float(self._fake_group, CommandFloatPositionKp)[0]

  @property
  def position_ki(self):
    """
    Integral PID gain for position
    """
    return get_group_command_float(self._fake_group, CommandFloatPositionKi)[0]

  @property
  def position_kd(self):
    """
    Derivative PID gain for position
    """
    return get_group_command_float(self._fake_group, CommandFloatPositionKd)[0]

  @property
  def position_feed_forward(self):
    """
    Feed forward term for position (this term is multiplied by the target and added to the output).
    """
    return get_group_command_float(self._fake_group, CommandFloatPositionFeedForward)[0]

  @property
  def position_dead_zone(self):
    """
    Error values within +/- this value from zero are treated as zero (in terms of computed proportional output, input to numerical derivative, and accumulated integral error).
    """
    return get_group_command_float(self._fake_group, CommandFloatPositionDeadZone)[0]

  @property
  def position_i_clamp(self):
    """
    Maximum allowed value for the output of the integral component of the PID loop; the integrated error is not allowed to exceed value that will generate this number.
    """
    return get_group_command_float(self._fake_group, CommandFloatPositionIClamp)[0]

  @property
  def position_punch(self):
    """
    Constant offset to the position PID output outside of the deadzone; it is added when the error is positive and subtracted when it is negative.
    """
    return get_group_command_float(self._fake_group, CommandFloatPositionPunch)[0]

  @property
  def position_min_target(self):
    """
    Minimum allowed value for input to the PID controller
    """
    return get_group_command_float(self._fake_group, CommandFloatPositionMinTarget)[0]

  @property
  def position_max_target(self):
    """
    Maximum allowed value for input to the PID controller
    """
    return get_group_command_float(self._fake_group, CommandFloatPositionMaxTarget)[0]

  @property
  def position_target_lowpass(self):
    """
    A simple lowpass filter applied to the target set point; needs to be between 0 and 1. At each timestep: x_t = x_t * a + x_{t-1} * (1 - a).
    """
    return get_group_command_float(self._fake_group, CommandFloatPositionTargetLowpass)[0]

  @property
  def position_min_output(self):
    """
    Output from the PID controller is limited to a minimum of this value.
    """
    return get_group_command_float(self._fake_group, CommandFloatPositionMinOutput)[0]

  @property
  def position_max_output(self):
    """
    Output from the PID controller is limited to a maximum of this value.
    """
    return get_group_command_float(self._fake_group, CommandFloatPositionMaxOutput)[0]

  @property
  def position_output_lowpass(self):
    """
    A simple lowpass filter applied to the controller output; needs to be between 0 and 1. At each timestep: x_t = x_t * a + x_{t-1} * (1 - a).
    """
    return get_group_command_float(self._fake_group, CommandFloatPositionOutputLowpass)[0]

  @property
  def velocity_kp(self):
    """
    Proportional PID gain for velocity
    """
    return get_group_command_float(self._fake_group, CommandFloatVelocityKp)[0]

  @property
  def velocity_ki(self):
    """
    Integral PID gain for velocity
    """
    return get_group_command_float(self._fake_group, CommandFloatVelocityKi)[0]

  @property
  def velocity_kd(self):
    """
    Derivative PID gain for velocity
    """
    return get_group_command_float(self._fake_group, CommandFloatVelocityKd)[0]

  @property
  def velocity_feed_forward(self):
    """
    Feed forward term for velocity (this term is multiplied by the target and added to the output).
    """
    return get_group_command_float(self._fake_group, CommandFloatVelocityFeedForward)[0]

  @property
  def velocity_dead_zone(self):
    """
    Error values within +/- this value from zero are treated as zero (in terms of computed proportional output, input to numerical derivative, and accumulated integral error).
    """
    return get_group_command_float(self._fake_group, CommandFloatVelocityDeadZone)[0]

  @property
  def velocity_i_clamp(self):
    """
    Maximum allowed value for the output of the integral component of the PID loop; the integrated error is not allowed to exceed value that will generate this number.
    """
    return get_group_command_float(self._fake_group, CommandFloatVelocityIClamp)[0]

  @property
  def velocity_punch(self):
    """
    Constant offset to the velocity PID output outside of the deadzone; it is added when the error is positive and subtracted when it is negative.
    """
    return get_group_command_float(self._fake_group, CommandFloatVelocityPunch)[0]

  @property
  def velocity_min_target(self):
    """
    Minimum allowed value for input to the PID controller
    """
    return get_group_command_float(self._fake_group, CommandFloatVelocityMinTarget)[0]

  @property
  def velocity_max_target(self):
    """
    Maximum allowed value for input to the PID controller
    """
    return get_group_command_float(self._fake_group, CommandFloatVelocityMaxTarget)[0]

  @property
  def velocity_target_lowpass(self):
    """
    A simple lowpass filter applied to the target set point; needs to be between 0 and 1. At each timestep: x_t = x_t * a + x_{t-1} * (1 - a).
    """
    return get_group_command_float(self._fake_group, CommandFloatVelocityTargetLowpass)[0]

  @property
  def velocity_min_output(self):
    """
    Output from the PID controller is limited to a minimum of this value.
    """
    return get_group_command_float(self._fake_group, CommandFloatVelocityMinOutput)[0]

  @property
  def velocity_max_output(self):
    """
    Output from the PID controller is limited to a maximum of this value.
    """
    return get_group_command_float(self._fake_group, CommandFloatVelocityMaxOutput)[0]

  @property
  def velocity_output_lowpass(self):
    """
    A simple lowpass filter applied to the controller output; needs to be between 0 and 1. At each timestep: x_t = x_t * a + x_{t-1} * (1 - a).
    """
    return get_group_command_float(self._fake_group, CommandFloatVelocityOutputLowpass)[0]

  @property
  def effort_kp(self):
    """
    Proportional PID gain for effort
    """
    return get_group_command_float(self._fake_group, CommandFloatEffortKp)[0]

  @property
  def effort_ki(self):
    """
    Integral PID gain for effort
    """
    return get_group_command_float(self._fake_group, CommandFloatEffortKi)[0]

  @property
  def effort_kd(self):
    """
    Derivative PID gain for effort
    """
    return get_group_command_float(self._fake_group, CommandFloatEffortKd)[0]

  @property
  def effort_feed_forward(self):
    """
    Feed forward term for effort (this term is multiplied by the target and added to the output).
    """
    return get_group_command_float(self._fake_group, CommandFloatEffortFeedForward)[0]

  @property
  def effort_dead_zone(self):
    """
    Error values within +/- this value from zero are treated as zero (in terms of computed proportional output, input to numerical derivative, and accumulated integral error).
    """
    return get_group_command_float(self._fake_group, CommandFloatEffortDeadZone)[0]

  @property
  def effort_i_clamp(self):
    """
    Maximum allowed value for the output of the integral component of the PID loop; the integrated error is not allowed to exceed value that will generate this number.
    """
    return get_group_command_float(self._fake_group, CommandFloatEffortIClamp)[0]

  @property
  def effort_punch(self):
    """
    Constant offset to the effort PID output outside of the deadzone; it is added when the error is positive and subtracted when it is negative.
    """
    return get_group_command_float(self._fake_group, CommandFloatEffortPunch)[0]

  @property
  def effort_min_target(self):
    """
    Minimum allowed value for input to the PID controller
    """
    return get_group_command_float(self._fake_group, CommandFloatEffortMinTarget)[0]

  @property
  def effort_max_target(self):
    """
    Maximum allowed value for input to the PID controller
    """
    return get_group_command_float(self._fake_group, CommandFloatEffortMaxTarget)[0]

  @property
  def effort_target_lowpass(self):
    """
    A simple lowpass filter applied to the target set point; needs to be between 0 and 1. At each timestep: x_t = x_t * a + x_{t-1} * (1 - a).
    """
    return get_group_command_float(self._fake_group, CommandFloatEffortTargetLowpass)[0]

  @property
  def effort_min_output(self):
    """
    Output from the PID controller is limited to a minimum of this value.
    """
    return get_group_command_float(self._fake_group, CommandFloatEffortMinOutput)[0]

  @property
  def effort_max_output(self):
    """
    Output from the PID controller is limited to a maximum of this value.
    """
    return get_group_command_float(self._fake_group, CommandFloatEffortMaxOutput)[0]

  @property
  def effort_output_lowpass(self):
    """
    A simple lowpass filter applied to the controller output; needs to be between 0 and 1. At each timestep: x_t = x_t * a + x_{t-1} * (1 - a).
    """
    return get_group_command_float(self._fake_group, CommandFloatEffortOutputLowpass)[0]

  @property
  def spring_constant(self):
    """
    The spring constant of the module.
    """
    return get_group_command_float(self._fake_group, CommandFloatSpringConstant)[0]

  @property
  def reference_position(self):
    """
    Set the internal encoder reference offset so that the current position matches the given reference command
    """
    return get_group_command_float(self._fake_group, CommandFloatReferencePosition)[0]

  @property
  def reference_effort(self):
    """
    Set the internal effort reference offset so that the current effort matches the given reference command
    """
    return get_group_command_float(self._fake_group, CommandFloatReferenceEffort)[0]

  @property
  def position(self):
    """
    Position of the module output (post-spring), in radians.
    """
    return get_group_command_highresangle(self._fake_group, CommandHighResAnglePosition)[0]

  @property
  def position_d_on_error(self):
    """
    Controls whether the Kd term uses the "derivative of error" or "derivative of measurement." When the setpoints have step inputs or are noisy, setting this to :code:`False` can eliminate corresponding spikes or noise in the output.
    """
    return get_group_command_bool(self._fake_group, CommandBoolPositionDOnError)[0]

  @property
  def velocity_d_on_error(self):
    """
    Controls whether the Kd term uses the "derivative of error" or "derivative of measurement." When the setpoints have step inputs or are noisy, setting this to :code:`False` can eliminate corresponding spikes or noise in the output.
    """
    return get_group_command_bool(self._fake_group, CommandBoolVelocityDOnError)[0]

  @property
  def effort_d_on_error(self):
    """
    Controls whether the Kd term uses the "derivative of error" or "derivative of measurement." When the setpoints have step inputs or are noisy, setting this to :code:`False` can eliminate corresponding spikes or noise in the output.
    """
    return get_group_command_bool(self._fake_group, CommandBoolEffortDOnError)[0]

  @property
  def save_current_settings(self):
    """
    Indicates if the module should save the current values of all of its settings.
    """
    return get_group_command_flag(self._fake_group, CommandFlagSaveCurrentSettings)[0]

  @property
  def control_strategy(self):
    """
    How the position, velocity, and effort PID loops are connected in order to control motor PWM.
    """
    return get_group_command_enum(self._fake_group, CommandEnumControlStrategy)[0]

  @velocity.setter
  def velocity(self, value):
    """
    Velocity of the module output (post-spring), in radians/second.
    """
    set_group_command_float(self._fake_group, CommandFloatVelocity, value)
  
  @effort.setter
  def effort(self, value):
    """
    Effort at the module output; units vary (*e.g.*, :math:`N \cdot m` for rotational joints and *N* for linear stages).
    """
    set_group_command_float(self._fake_group, CommandFloatEffort, value)
  
  @position_kp.setter
  def position_kp(self, value):
    """
    Proportional PID gain for position
    """
    set_group_command_float(self._fake_group, CommandFloatPositionKp, value)
  
  @position_ki.setter
  def position_ki(self, value):
    """
    Integral PID gain for position
    """
    set_group_command_float(self._fake_group, CommandFloatPositionKi, value)
  
  @position_kd.setter
  def position_kd(self, value):
    """
    Derivative PID gain for position
    """
    set_group_command_float(self._fake_group, CommandFloatPositionKd, value)
  
  @position_feed_forward.setter
  def position_feed_forward(self, value):
    """
    Feed forward term for position (this term is multiplied by the target and added to the output).
    """
    set_group_command_float(self._fake_group, CommandFloatPositionFeedForward, value)
  
  @position_dead_zone.setter
  def position_dead_zone(self, value):
    """
    Error values within +/- this value from zero are treated as zero (in terms of computed proportional output, input to numerical derivative, and accumulated integral error).
    """
    set_group_command_float(self._fake_group, CommandFloatPositionDeadZone, value)
  
  @position_i_clamp.setter
  def position_i_clamp(self, value):
    """
    Maximum allowed value for the output of the integral component of the PID loop; the integrated error is not allowed to exceed value that will generate this number.
    """
    set_group_command_float(self._fake_group, CommandFloatPositionIClamp, value)
  
  @position_punch.setter
  def position_punch(self, value):
    """
    Constant offset to the position PID output outside of the deadzone; it is added when the error is positive and subtracted when it is negative.
    """
    set_group_command_float(self._fake_group, CommandFloatPositionPunch, value)
  
  @position_min_target.setter
  def position_min_target(self, value):
    """
    Minimum allowed value for input to the PID controller
    """
    set_group_command_float(self._fake_group, CommandFloatPositionMinTarget, value)
  
  @position_max_target.setter
  def position_max_target(self, value):
    """
    Maximum allowed value for input to the PID controller
    """
    set_group_command_float(self._fake_group, CommandFloatPositionMaxTarget, value)
  
  @position_target_lowpass.setter
  def position_target_lowpass(self, value):
    """
    A simple lowpass filter applied to the target set point; needs to be between 0 and 1. At each timestep: x_t = x_t * a + x_{t-1} * (1 - a).
    """
    set_group_command_float(self._fake_group, CommandFloatPositionTargetLowpass, value)
  
  @position_min_output.setter
  def position_min_output(self, value):
    """
    Output from the PID controller is limited to a minimum of this value.
    """
    set_group_command_float(self._fake_group, CommandFloatPositionMinOutput, value)
  
  @position_max_output.setter
  def position_max_output(self, value):
    """
    Output from the PID controller is limited to a maximum of this value.
    """
    set_group_command_float(self._fake_group, CommandFloatPositionMaxOutput, value)
  
  @position_output_lowpass.setter
  def position_output_lowpass(self, value):
    """
    A simple lowpass filter applied to the controller output; needs to be between 0 and 1. At each timestep: x_t = x_t * a + x_{t-1} * (1 - a).
    """
    set_group_command_float(self._fake_group, CommandFloatPositionOutputLowpass, value)
  
  @velocity_kp.setter
  def velocity_kp(self, value):
    """
    Proportional PID gain for velocity
    """
    set_group_command_float(self._fake_group, CommandFloatVelocityKp, value)
  
  @velocity_ki.setter
  def velocity_ki(self, value):
    """
    Integral PID gain for velocity
    """
    set_group_command_float(self._fake_group, CommandFloatVelocityKi, value)
  
  @velocity_kd.setter
  def velocity_kd(self, value):
    """
    Derivative PID gain for velocity
    """
    set_group_command_float(self._fake_group, CommandFloatVelocityKd, value)
  
  @velocity_feed_forward.setter
  def velocity_feed_forward(self, value):
    """
    Feed forward term for velocity (this term is multiplied by the target and added to the output).
    """
    set_group_command_float(self._fake_group, CommandFloatVelocityFeedForward, value)
  
  @velocity_dead_zone.setter
  def velocity_dead_zone(self, value):
    """
    Error values within +/- this value from zero are treated as zero (in terms of computed proportional output, input to numerical derivative, and accumulated integral error).
    """
    set_group_command_float(self._fake_group, CommandFloatVelocityDeadZone, value)
  
  @velocity_i_clamp.setter
  def velocity_i_clamp(self, value):
    """
    Maximum allowed value for the output of the integral component of the PID loop; the integrated error is not allowed to exceed value that will generate this number.
    """
    set_group_command_float(self._fake_group, CommandFloatVelocityIClamp, value)
  
  @velocity_punch.setter
  def velocity_punch(self, value):
    """
    Constant offset to the velocity PID output outside of the deadzone; it is added when the error is positive and subtracted when it is negative.
    """
    set_group_command_float(self._fake_group, CommandFloatVelocityPunch, value)
  
  @velocity_min_target.setter
  def velocity_min_target(self, value):
    """
    Minimum allowed value for input to the PID controller
    """
    set_group_command_float(self._fake_group, CommandFloatVelocityMinTarget, value)
  
  @velocity_max_target.setter
  def velocity_max_target(self, value):
    """
    Maximum allowed value for input to the PID controller
    """
    set_group_command_float(self._fake_group, CommandFloatVelocityMaxTarget, value)
  
  @velocity_target_lowpass.setter
  def velocity_target_lowpass(self, value):
    """
    A simple lowpass filter applied to the target set point; needs to be between 0 and 1. At each timestep: x_t = x_t * a + x_{t-1} * (1 - a).
    """
    set_group_command_float(self._fake_group, CommandFloatVelocityTargetLowpass, value)
  
  @velocity_min_output.setter
  def velocity_min_output(self, value):
    """
    Output from the PID controller is limited to a minimum of this value.
    """
    set_group_command_float(self._fake_group, CommandFloatVelocityMinOutput, value)
  
  @velocity_max_output.setter
  def velocity_max_output(self, value):
    """
    Output from the PID controller is limited to a maximum of this value.
    """
    set_group_command_float(self._fake_group, CommandFloatVelocityMaxOutput, value)
  
  @velocity_output_lowpass.setter
  def velocity_output_lowpass(self, value):
    """
    A simple lowpass filter applied to the controller output; needs to be between 0 and 1. At each timestep: x_t = x_t * a + x_{t-1} * (1 - a).
    """
    set_group_command_float(self._fake_group, CommandFloatVelocityOutputLowpass, value)
  
  @effort_kp.setter
  def effort_kp(self, value):
    """
    Proportional PID gain for effort
    """
    set_group_command_float(self._fake_group, CommandFloatEffortKp, value)
  
  @effort_ki.setter
  def effort_ki(self, value):
    """
    Integral PID gain for effort
    """
    set_group_command_float(self._fake_group, CommandFloatEffortKi, value)
  
  @effort_kd.setter
  def effort_kd(self, value):
    """
    Derivative PID gain for effort
    """
    set_group_command_float(self._fake_group, CommandFloatEffortKd, value)
  
  @effort_feed_forward.setter
  def effort_feed_forward(self, value):
    """
    Feed forward term for effort (this term is multiplied by the target and added to the output).
    """
    set_group_command_float(self._fake_group, CommandFloatEffortFeedForward, value)
  
  @effort_dead_zone.setter
  def effort_dead_zone(self, value):
    """
    Error values within +/- this value from zero are treated as zero (in terms of computed proportional output, input to numerical derivative, and accumulated integral error).
    """
    set_group_command_float(self._fake_group, CommandFloatEffortDeadZone, value)
  
  @effort_i_clamp.setter
  def effort_i_clamp(self, value):
    """
    Maximum allowed value for the output of the integral component of the PID loop; the integrated error is not allowed to exceed value that will generate this number.
    """
    set_group_command_float(self._fake_group, CommandFloatEffortIClamp, value)
  
  @effort_punch.setter
  def effort_punch(self, value):
    """
    Constant offset to the effort PID output outside of the deadzone; it is added when the error is positive and subtracted when it is negative.
    """
    set_group_command_float(self._fake_group, CommandFloatEffortPunch, value)
  
  @effort_min_target.setter
  def effort_min_target(self, value):
    """
    Minimum allowed value for input to the PID controller
    """
    set_group_command_float(self._fake_group, CommandFloatEffortMinTarget, value)
  
  @effort_max_target.setter
  def effort_max_target(self, value):
    """
    Maximum allowed value for input to the PID controller
    """
    set_group_command_float(self._fake_group, CommandFloatEffortMaxTarget, value)
  
  @effort_target_lowpass.setter
  def effort_target_lowpass(self, value):
    """
    A simple lowpass filter applied to the target set point; needs to be between 0 and 1. At each timestep: x_t = x_t * a + x_{t-1} * (1 - a).
    """
    set_group_command_float(self._fake_group, CommandFloatEffortTargetLowpass, value)
  
  @effort_min_output.setter
  def effort_min_output(self, value):
    """
    Output from the PID controller is limited to a minimum of this value.
    """
    set_group_command_float(self._fake_group, CommandFloatEffortMinOutput, value)
  
  @effort_max_output.setter
  def effort_max_output(self, value):
    """
    Output from the PID controller is limited to a maximum of this value.
    """
    set_group_command_float(self._fake_group, CommandFloatEffortMaxOutput, value)
  
  @effort_output_lowpass.setter
  def effort_output_lowpass(self, value):
    """
    A simple lowpass filter applied to the controller output; needs to be between 0 and 1. At each timestep: x_t = x_t * a + x_{t-1} * (1 - a).
    """
    set_group_command_float(self._fake_group, CommandFloatEffortOutputLowpass, value)
  
  @spring_constant.setter
  def spring_constant(self, value):
    """
    The spring constant of the module.
    """
    set_group_command_float(self._fake_group, CommandFloatSpringConstant, value)
  
  @reference_position.setter
  def reference_position(self, value):
    """
    Set the internal encoder reference offset so that the current position matches the given reference command
    """
    set_group_command_float(self._fake_group, CommandFloatReferencePosition, value)
  
  @reference_effort.setter
  def reference_effort(self, value):
    """
    Set the internal effort reference offset so that the current effort matches the given reference command
    """
    set_group_command_float(self._fake_group, CommandFloatReferenceEffort, value)
  
  @position.setter
  def position(self, value):
    """
    Position of the module output (post-spring), in radians.
    """
    set_group_command_highresangle(self._fake_group, CommandHighResAnglePosition, value)
  
  @position_d_on_error.setter
  def position_d_on_error(self, value):
    """
    Controls whether the Kd term uses the "derivative of error" or "derivative of measurement." When the setpoints have step inputs or are noisy, setting this to :code:`False` can eliminate corresponding spikes or noise in the output.
    """
    set_group_command_bool(self._fake_group, CommandBoolPositionDOnError, value)
  
  @velocity_d_on_error.setter
  def velocity_d_on_error(self, value):
    """
    Controls whether the Kd term uses the "derivative of error" or "derivative of measurement." When the setpoints have step inputs or are noisy, setting this to :code:`False` can eliminate corresponding spikes or noise in the output.
    """
    set_group_command_bool(self._fake_group, CommandBoolVelocityDOnError, value)
  
  @effort_d_on_error.setter
  def effort_d_on_error(self, value):
    """
    Controls whether the Kd term uses the "derivative of error" or "derivative of measurement." When the setpoints have step inputs or are noisy, setting this to :code:`False` can eliminate corresponding spikes or noise in the output.
    """
    set_group_command_bool(self._fake_group, CommandBoolEffortDOnError, value)
  
  @save_current_settings.setter
  def save_current_settings(self, value):
    """
    Indicates if the module should save the current values of all of its settings.
    """
    set_group_command_flag(self._fake_group, CommandFlagSaveCurrentSettings, value)
  
  @control_strategy.setter
  def control_strategy(self, value):
    """
    How the position, velocity, and effort PID loops are connected in order to control motor PWM.
    """
    set_group_command_enum(self._fake_group, CommandEnumControlStrategy, value)

  @property
  def name(self):
    return get_group_command_string(self._fake_group, CommandStringName)[0]

  @name.setter
  def name(self, value):
    set_group_command_string(self._fake_group, CommandStringName, value)

  @property
  def family(self):
    return get_group_command_string(self._fake_group, CommandStringFamily)[0]

  @family.setter
  def family(self, value):
    set_group_command_string(self._fake_group, CommandStringFamily, value)


class Feedback(UnmanagedObject):
  """
  Used to represent a Feedback object.
  Do not instantiate directly - use only through a GroupFeedback instance.
  """

  def __init__(self, internal):
    """
    This is invoked internally. Do not use directly.
    """
    super(Feedback, self).__init__(internal)
    self._fake_group = FakeGroupMessage(self._internal)

  @property
  def board_temperature(self):
    """
    Ambient temperature inside the module (measured at the IMU chip), in degrees Celsius.
    """
    return get_group_feedback_float(self._fake_group, FeedbackFloatBoardTemperature)[0]

  @property
  def processor_temperature(self):
    """
    Temperature of the processor chip, in degrees Celsius.
    """
    return get_group_feedback_float(self._fake_group, FeedbackFloatProcessorTemperature)[0]

  @property
  def voltage(self):
    """
    Bus voltage that the module is running at (in Volts).
    """
    return get_group_feedback_float(self._fake_group, FeedbackFloatVoltage)[0]

  @property
  def velocity(self):
    """
    Velocity of the module output (post-spring), in radians/second.
    """
    return get_group_feedback_float(self._fake_group, FeedbackFloatVelocity)[0]

  @property
  def effort(self):
    """
    Effort at the module output; units vary (*e.g.*, :math:`N \cdot m` for rotational joints and *N* for linear stages).
    """
    return get_group_feedback_float(self._fake_group, FeedbackFloatEffort)[0]

  @property
  def velocity_command(self):
    """
    Commanded velocity of the module output (post-spring), in radians/second.
    """
    return get_group_feedback_float(self._fake_group, FeedbackFloatVelocityCommand)[0]

  @property
  def effort_command(self):
    """
    Commanded effort at the module output; units vary (*e.g.*, :math:`N \cdot m` for rotational joints and *N* for linear stages).
    """
    return get_group_feedback_float(self._fake_group, FeedbackFloatEffortCommand)[0]

  @property
  def deflection(self):
    """
    Difference (in radians) between the pre-spring and post-spring output position.
    """
    return get_group_feedback_float(self._fake_group, FeedbackFloatDeflection)[0]

  @property
  def deflection_velocity(self):
    """
    Velocity (in radians/second) of the difference between the pre-spring and post-spring output position.
    """
    return get_group_feedback_float(self._fake_group, FeedbackFloatDeflectionVelocity)[0]

  @property
  def motor_velocity(self):
    """
    The velocity (in radians/second) of the motor shaft.
    """
    return get_group_feedback_float(self._fake_group, FeedbackFloatMotorVelocity)[0]

  @property
  def motor_current(self):
    """
    Current supplied to the motor.
    """
    return get_group_feedback_float(self._fake_group, FeedbackFloatMotorCurrent)[0]

  @property
  def motor_sensor_temperature(self):
    """
    The temperature from a sensor near the motor housing.
    """
    return get_group_feedback_float(self._fake_group, FeedbackFloatMotorSensorTemperature)[0]

  @property
  def motor_winding_current(self):
    """
    The estimated current in the motor windings.
    """
    return get_group_feedback_float(self._fake_group, FeedbackFloatMotorWindingCurrent)[0]

  @property
  def motor_winding_temperature(self):
    """
    The estimated temperature of the motor windings.
    """
    return get_group_feedback_float(self._fake_group, FeedbackFloatMotorWindingTemperature)[0]

  @property
  def motor_housing_temperature(self):
    """
    The estimated temperature of the motor housing.
    """
    return get_group_feedback_float(self._fake_group, FeedbackFloatMotorHousingTemperature)[0]

  @property
  def position(self):
    """
    Position of the module output (post-spring), in radians.
    """
    return get_group_feedback_highresangle(self._fake_group, FeedbackHighResAnglePosition)[0]

  @property
  def position_command(self):
    """
    Commanded position of the module output (post-spring), in radians.
    """
    return get_group_feedback_highresangle(self._fake_group, FeedbackHighResAnglePositionCommand)[0]

  @property
  def sequence_number(self):
    """
    Sequence number going to module (local)
    """
    return get_group_feedback_uint64(self._fake_group, FeedbackUInt64SequenceNumber)[0]

  @property
  def receive_time(self):
    """
    Timestamp of when message was received from module (local)
    """
    return get_group_feedback_uint64(self._fake_group, FeedbackUInt64ReceiveTime)[0]

  @property
  def transmit_time(self):
    """
    Timestamp of when message was transmitted to module (local)
    """
    return get_group_feedback_uint64(self._fake_group, FeedbackUInt64TransmitTime)[0]

  @property
  def hardware_receive_time(self):
    """
    Timestamp of when message was received by module (remote)
    """
    return get_group_feedback_uint64(self._fake_group, FeedbackUInt64HardwareReceiveTime)[0]

  @property
  def hardware_transmit_time(self):
    """
    Timestamp of when message was transmitted from module (remote)
    """
    return get_group_feedback_uint64(self._fake_group, FeedbackUInt64HardwareTransmitTime)[0]

  @property
  def sender_id(self):
    """
    Unique ID of the module transmitting this feedback
    """
    return get_group_feedback_uint64(self._fake_group, FeedbackUInt64SenderId)[0]

  @property
  def accelerometer(self):
    """
    Accelerometer data, in m/s^2.
    """
    return get_group_feedback_vector3f(self._fake_group, FeedbackVector3fAccelerometer)[0]

  @property
  def gyro(self):
    """
    Gyro data, in radians/second.
    """
    return get_group_feedback_vector3f(self._fake_group, FeedbackVector3fGyro)[0]


class Info(UnmanagedObject):
  """
  Used to represent a Info object.
  Do not instantiate directly - use only through a GroupInfo instance.
  """

  def __init__(self, internal):
    """
    This is invoked internally. Do not use directly.
    """
    super(Info, self).__init__(internal)
    self._fake_group = FakeGroupMessage(self._internal)

  @property
  def position_kp(self):
    """
    Proportional PID gain for position
    """
    return get_group_info_float(self._fake_group, InfoFloatPositionKp)[0]

  @property
  def position_ki(self):
    """
    Integral PID gain for position
    """
    return get_group_info_float(self._fake_group, InfoFloatPositionKi)[0]

  @property
  def position_kd(self):
    """
    Derivative PID gain for position
    """
    return get_group_info_float(self._fake_group, InfoFloatPositionKd)[0]

  @property
  def position_feed_forward(self):
    """
    Feed forward term for position (this term is multiplied by the target and added to the output).
    """
    return get_group_info_float(self._fake_group, InfoFloatPositionFeedForward)[0]

  @property
  def position_dead_zone(self):
    """
    Error values within +/- this value from zero are treated as zero (in terms of computed proportional output, input to numerical derivative, and accumulated integral error).
    """
    return get_group_info_float(self._fake_group, InfoFloatPositionDeadZone)[0]

  @property
  def position_i_clamp(self):
    """
    Maximum allowed value for the output of the integral component of the PID loop; the integrated error is not allowed to exceed value that will generate this number.
    """
    return get_group_info_float(self._fake_group, InfoFloatPositionIClamp)[0]

  @property
  def position_punch(self):
    """
    Constant offset to the position PID output outside of the deadzone; it is added when the error is positive and subtracted when it is negative.
    """
    return get_group_info_float(self._fake_group, InfoFloatPositionPunch)[0]

  @property
  def position_min_target(self):
    """
    Minimum allowed value for input to the PID controller
    """
    return get_group_info_float(self._fake_group, InfoFloatPositionMinTarget)[0]

  @property
  def position_max_target(self):
    """
    Maximum allowed value for input to the PID controller
    """
    return get_group_info_float(self._fake_group, InfoFloatPositionMaxTarget)[0]

  @property
  def position_target_lowpass(self):
    """
    A simple lowpass filter applied to the target set point; needs to be between 0 and 1. At each timestep: x_t = x_t * a + x_{t-1} * (1 - a).
    """
    return get_group_info_float(self._fake_group, InfoFloatPositionTargetLowpass)[0]

  @property
  def position_min_output(self):
    """
    Output from the PID controller is limited to a minimum of this value.
    """
    return get_group_info_float(self._fake_group, InfoFloatPositionMinOutput)[0]

  @property
  def position_max_output(self):
    """
    Output from the PID controller is limited to a maximum of this value.
    """
    return get_group_info_float(self._fake_group, InfoFloatPositionMaxOutput)[0]

  @property
  def position_output_lowpass(self):
    """
    A simple lowpass filter applied to the controller output; needs to be between 0 and 1. At each timestep: x_t = x_t * a + x_{t-1} * (1 - a).
    """
    return get_group_info_float(self._fake_group, InfoFloatPositionOutputLowpass)[0]

  @property
  def velocity_kp(self):
    """
    Proportional PID gain for velocity
    """
    return get_group_info_float(self._fake_group, InfoFloatVelocityKp)[0]

  @property
  def velocity_ki(self):
    """
    Integral PID gain for velocity
    """
    return get_group_info_float(self._fake_group, InfoFloatVelocityKi)[0]

  @property
  def velocity_kd(self):
    """
    Derivative PID gain for velocity
    """
    return get_group_info_float(self._fake_group, InfoFloatVelocityKd)[0]

  @property
  def velocity_feed_forward(self):
    """
    Feed forward term for velocity (this term is multiplied by the target and added to the output).
    """
    return get_group_info_float(self._fake_group, InfoFloatVelocityFeedForward)[0]

  @property
  def velocity_dead_zone(self):
    """
    Error values within +/- this value from zero are treated as zero (in terms of computed proportional output, input to numerical derivative, and accumulated integral error).
    """
    return get_group_info_float(self._fake_group, InfoFloatVelocityDeadZone)[0]

  @property
  def velocity_i_clamp(self):
    """
    Maximum allowed value for the output of the integral component of the PID loop; the integrated error is not allowed to exceed value that will generate this number.
    """
    return get_group_info_float(self._fake_group, InfoFloatVelocityIClamp)[0]

  @property
  def velocity_punch(self):
    """
    Constant offset to the velocity PID output outside of the deadzone; it is added when the error is positive and subtracted when it is negative.
    """
    return get_group_info_float(self._fake_group, InfoFloatVelocityPunch)[0]

  @property
  def velocity_min_target(self):
    """
    Minimum allowed value for input to the PID controller
    """
    return get_group_info_float(self._fake_group, InfoFloatVelocityMinTarget)[0]

  @property
  def velocity_max_target(self):
    """
    Maximum allowed value for input to the PID controller
    """
    return get_group_info_float(self._fake_group, InfoFloatVelocityMaxTarget)[0]

  @property
  def velocity_target_lowpass(self):
    """
    A simple lowpass filter applied to the target set point; needs to be between 0 and 1. At each timestep: x_t = x_t * a + x_{t-1} * (1 - a).
    """
    return get_group_info_float(self._fake_group, InfoFloatVelocityTargetLowpass)[0]

  @property
  def velocity_min_output(self):
    """
    Output from the PID controller is limited to a minimum of this value.
    """
    return get_group_info_float(self._fake_group, InfoFloatVelocityMinOutput)[0]

  @property
  def velocity_max_output(self):
    """
    Output from the PID controller is limited to a maximum of this value.
    """
    return get_group_info_float(self._fake_group, InfoFloatVelocityMaxOutput)[0]

  @property
  def velocity_output_lowpass(self):
    """
    A simple lowpass filter applied to the controller output; needs to be between 0 and 1. At each timestep: x_t = x_t * a + x_{t-1} * (1 - a).
    """
    return get_group_info_float(self._fake_group, InfoFloatVelocityOutputLowpass)[0]

  @property
  def effort_kp(self):
    """
    Proportional PID gain for effort
    """
    return get_group_info_float(self._fake_group, InfoFloatEffortKp)[0]

  @property
  def effort_ki(self):
    """
    Integral PID gain for effort
    """
    return get_group_info_float(self._fake_group, InfoFloatEffortKi)[0]

  @property
  def effort_kd(self):
    """
    Derivative PID gain for effort
    """
    return get_group_info_float(self._fake_group, InfoFloatEffortKd)[0]

  @property
  def effort_feed_forward(self):
    """
    Feed forward term for effort (this term is multiplied by the target and added to the output).
    """
    return get_group_info_float(self._fake_group, InfoFloatEffortFeedForward)[0]

  @property
  def effort_dead_zone(self):
    """
    Error values within +/- this value from zero are treated as zero (in terms of computed proportional output, input to numerical derivative, and accumulated integral error).
    """
    return get_group_info_float(self._fake_group, InfoFloatEffortDeadZone)[0]

  @property
  def effort_i_clamp(self):
    """
    Maximum allowed value for the output of the integral component of the PID loop; the integrated error is not allowed to exceed value that will generate this number.
    """
    return get_group_info_float(self._fake_group, InfoFloatEffortIClamp)[0]

  @property
  def effort_punch(self):
    """
    Constant offset to the effort PID output outside of the deadzone; it is added when the error is positive and subtracted when it is negative.
    """
    return get_group_info_float(self._fake_group, InfoFloatEffortPunch)[0]

  @property
  def effort_min_target(self):
    """
    Minimum allowed value for input to the PID controller
    """
    return get_group_info_float(self._fake_group, InfoFloatEffortMinTarget)[0]

  @property
  def effort_max_target(self):
    """
    Maximum allowed value for input to the PID controller
    """
    return get_group_info_float(self._fake_group, InfoFloatEffortMaxTarget)[0]

  @property
  def effort_target_lowpass(self):
    """
    A simple lowpass filter applied to the target set point; needs to be between 0 and 1. At each timestep: x_t = x_t * a + x_{t-1} * (1 - a).
    """
    return get_group_info_float(self._fake_group, InfoFloatEffortTargetLowpass)[0]

  @property
  def effort_min_output(self):
    """
    Output from the PID controller is limited to a minimum of this value.
    """
    return get_group_info_float(self._fake_group, InfoFloatEffortMinOutput)[0]

  @property
  def effort_max_output(self):
    """
    Output from the PID controller is limited to a maximum of this value.
    """
    return get_group_info_float(self._fake_group, InfoFloatEffortMaxOutput)[0]

  @property
  def effort_output_lowpass(self):
    """
    A simple lowpass filter applied to the controller output; needs to be between 0 and 1. At each timestep: x_t = x_t * a + x_{t-1} * (1 - a).
    """
    return get_group_info_float(self._fake_group, InfoFloatEffortOutputLowpass)[0]

  @property
  def spring_constant(self):
    """
    The spring constant of the module.
    """
    return get_group_info_float(self._fake_group, InfoFloatSpringConstant)[0]

  @property
  def position_d_on_error(self):
    """
    Controls whether the Kd term uses the "derivative of error" or "derivative of measurement." When the setpoints have step inputs or are noisy, setting this to :code:`False` can eliminate corresponding spikes or noise in the output.
    """
    return get_group_info_bool(self._fake_group, InfoBoolPositionDOnError)[0]

  @property
  def velocity_d_on_error(self):
    """
    Controls whether the Kd term uses the "derivative of error" or "derivative of measurement." When the setpoints have step inputs or are noisy, setting this to :code:`False` can eliminate corresponding spikes or noise in the output.
    """
    return get_group_info_bool(self._fake_group, InfoBoolVelocityDOnError)[0]

  @property
  def effort_d_on_error(self):
    """
    Controls whether the Kd term uses the "derivative of error" or "derivative of measurement." When the setpoints have step inputs or are noisy, setting this to :code:`False` can eliminate corresponding spikes or noise in the output.
    """
    return get_group_info_bool(self._fake_group, InfoBoolEffortDOnError)[0]

  @property
  def save_current_settings(self):
    """
    Indicates if the module should save the current values of all of its settings.
    """
    return get_group_info_flag(self._fake_group, InfoFlagSaveCurrentSettings)[0]

  @property
  def control_strategy(self):
    """
    How the position, velocity, and effort PID loops are connected in order to control motor PWM.
    """
    return get_group_info_enum(self._fake_group, InfoEnumControlStrategy)[0]


# ------------------------------------------------------------------------------
# Group Field Classes
# ------------------------------------------------------------------------------


class SharedGroupMessage(UnmanagedSharedObject):

  def __init__(self, number_of_modules, on_create, on_delete):
    super(SharedGroupMessage, self).__init__(on_create(number_of_modules),
                                             on_delete)


class GroupCommand(UnmanagedObject):
  """
  Command objects have various fields that can be set; when sent to the
  module, these fields control internal properties and setpoints.
  """

  def __initialize(self):
    self._commands = [ None ] * self._number_of_modules
    for i in range(self._number_of_modules):
      self._commands[i] = Command(hebiGroupCommandGetModuleCommand(self, i))

  def __init__(self, number_of_modules, shared=None):
    if (shared):
      if not (isinstance(shared, GroupCommand)):
        raise RuntimeError('Parameter shared must be a GroupCommand')
      elif(number_of_modules != shared.size):
        raise RuntimeError('Requested number of modules does not match shared parameter')
      super(GroupCommand, self).__init__(shared._internal)
      self._ref = shared._ref.add_ref()
    else:
      self._ref = SharedGroupMessage(number_of_modules,
                                     hebiGroupCommandCreate,
                                     hebiGroupCommandRelease)
      super(GroupCommand, self).__init__(self._ref._internal)

    self._number_of_modules = number_of_modules
    self.__initialize()
    self._io = GroupMessageIoFieldContainer(self, 'Command', mutable=True)
    self._debug = MutableGroupNumberedFloatFieldContainer(self, 'Command', CommandNumberedFloatDebug, 9)
    self._led = MutableGroupMessageLEDFieldContainer(self, 'Command', CommandLedLed)

  def __getitem__(self, key):
    return self._commands[key]

  def read_gains(self, file):
    """
    Import the gains from a file into this object.

    :param file:
    :raises: IOError is the file could not be opened
    """
    from os.path import isfile
    if not (isfile(file)):
      raise IOError('{0} is not a file'.format(file))

    res = hebiGroupCommandReadGains(self, create_str(file))
    if (res != StatusSuccess):
      from hebi._internal.errors import HEBI_Exception
      raise HEBI_Exception(res, 'hebiGroupCommandReadGains failed')

  def write_gains(self, file):
    """
    Export the gains from this object into a file, creating it if necessary.

    :param file:
    """
    res = hebiGroupCommandWriteGains(self, create_str(file))
    if (res != StatusSuccess):
      from hebi._internal.errors import HEBI_Exception
      raise HEBI_Exception(res, 'hebiGroupCommandWriteGains failed')

  @property
  def modules(self):
    return self._commands[:]

  @property
  def size(self):
    """
    The number of modules in this group message.
    """
    return self._number_of_modules

  @property
  def velocity(self):
    """
    Velocity of the module output (post-spring), in radians/second.
    """
    return get_group_command_float(self, CommandFloatVelocity)

  @velocity.setter
  def velocity(self, value):
    """
    Setter for velocity
    """
    set_group_command_float(self, CommandFloatVelocity, value)

  @property
  def effort(self):
    """
    Effort at the module output; units vary (*e.g.*, :math:`N \cdot m` for rotational joints and *N* for linear stages).
    """
    return get_group_command_float(self, CommandFloatEffort)

  @effort.setter
  def effort(self, value):
    """
    Setter for effort
    """
    set_group_command_float(self, CommandFloatEffort, value)

  @property
  def position_kp(self):
    """
    Proportional PID gain for position
    """
    return get_group_command_float(self, CommandFloatPositionKp)

  @position_kp.setter
  def position_kp(self, value):
    """
    Setter for position_kp
    """
    set_group_command_float(self, CommandFloatPositionKp, value)

  @property
  def position_ki(self):
    """
    Integral PID gain for position
    """
    return get_group_command_float(self, CommandFloatPositionKi)

  @position_ki.setter
  def position_ki(self, value):
    """
    Setter for position_ki
    """
    set_group_command_float(self, CommandFloatPositionKi, value)

  @property
  def position_kd(self):
    """
    Derivative PID gain for position
    """
    return get_group_command_float(self, CommandFloatPositionKd)

  @position_kd.setter
  def position_kd(self, value):
    """
    Setter for position_kd
    """
    set_group_command_float(self, CommandFloatPositionKd, value)

  @property
  def position_feed_forward(self):
    """
    Feed forward term for position (this term is multiplied by the target and added to the output).
    """
    return get_group_command_float(self, CommandFloatPositionFeedForward)

  @position_feed_forward.setter
  def position_feed_forward(self, value):
    """
    Setter for position_feed_forward
    """
    set_group_command_float(self, CommandFloatPositionFeedForward, value)

  @property
  def position_dead_zone(self):
    """
    Error values within +/- this value from zero are treated as zero (in terms of computed proportional output, input to numerical derivative, and accumulated integral error).
    """
    return get_group_command_float(self, CommandFloatPositionDeadZone)

  @position_dead_zone.setter
  def position_dead_zone(self, value):
    """
    Setter for position_dead_zone
    """
    set_group_command_float(self, CommandFloatPositionDeadZone, value)

  @property
  def position_i_clamp(self):
    """
    Maximum allowed value for the output of the integral component of the PID loop; the integrated error is not allowed to exceed value that will generate this number.
    """
    return get_group_command_float(self, CommandFloatPositionIClamp)

  @position_i_clamp.setter
  def position_i_clamp(self, value):
    """
    Setter for position_i_clamp
    """
    set_group_command_float(self, CommandFloatPositionIClamp, value)

  @property
  def position_punch(self):
    """
    Constant offset to the position PID output outside of the deadzone; it is added when the error is positive and subtracted when it is negative.
    """
    return get_group_command_float(self, CommandFloatPositionPunch)

  @position_punch.setter
  def position_punch(self, value):
    """
    Setter for position_punch
    """
    set_group_command_float(self, CommandFloatPositionPunch, value)

  @property
  def position_min_target(self):
    """
    Minimum allowed value for input to the PID controller
    """
    return get_group_command_float(self, CommandFloatPositionMinTarget)

  @position_min_target.setter
  def position_min_target(self, value):
    """
    Setter for position_min_target
    """
    set_group_command_float(self, CommandFloatPositionMinTarget, value)

  @property
  def position_max_target(self):
    """
    Maximum allowed value for input to the PID controller
    """
    return get_group_command_float(self, CommandFloatPositionMaxTarget)

  @position_max_target.setter
  def position_max_target(self, value):
    """
    Setter for position_max_target
    """
    set_group_command_float(self, CommandFloatPositionMaxTarget, value)

  @property
  def position_target_lowpass(self):
    """
    A simple lowpass filter applied to the target set point; needs to be between 0 and 1. At each timestep: :math:`x_t = x_t * a + x_{t-1} * (1 - a)`.
    """
    return get_group_command_float(self, CommandFloatPositionTargetLowpass)

  @position_target_lowpass.setter
  def position_target_lowpass(self, value):
    """
    Setter for position_target_lowpass
    """
    set_group_command_float(self, CommandFloatPositionTargetLowpass, value)

  @property
  def position_min_output(self):
    """
    Output from the PID controller is limited to a minimum of this value.
    """
    return get_group_command_float(self, CommandFloatPositionMinOutput)

  @position_min_output.setter
  def position_min_output(self, value):
    """
    Setter for position_min_output
    """
    set_group_command_float(self, CommandFloatPositionMinOutput, value)

  @property
  def position_max_output(self):
    """
    Output from the PID controller is limited to a maximum of this value.
    """
    return get_group_command_float(self, CommandFloatPositionMaxOutput)

  @position_max_output.setter
  def position_max_output(self, value):
    """
    Setter for position_max_output
    """
    set_group_command_float(self, CommandFloatPositionMaxOutput, value)

  @property
  def position_output_lowpass(self):
    """
    A simple lowpass filter applied to the controller output; needs to be between 0 and 1. At each timestep: :math:`x_t = x_t * a + x_{t-1} * (1 - a)`.
    """
    return get_group_command_float(self, CommandFloatPositionOutputLowpass)

  @position_output_lowpass.setter
  def position_output_lowpass(self, value):
    """
    Setter for position_output_lowpass
    """
    set_group_command_float(self, CommandFloatPositionOutputLowpass, value)

  @property
  def velocity_kp(self):
    """
    Proportional PID gain for velocity
    """
    return get_group_command_float(self, CommandFloatVelocityKp)

  @velocity_kp.setter
  def velocity_kp(self, value):
    """
    Setter for velocity_kp
    """
    set_group_command_float(self, CommandFloatVelocityKp, value)

  @property
  def velocity_ki(self):
    """
    Integral PID gain for velocity
    """
    return get_group_command_float(self, CommandFloatVelocityKi)

  @velocity_ki.setter
  def velocity_ki(self, value):
    """
    Setter for velocity_ki
    """
    set_group_command_float(self, CommandFloatVelocityKi, value)

  @property
  def velocity_kd(self):
    """
    Derivative PID gain for velocity
    """
    return get_group_command_float(self, CommandFloatVelocityKd)

  @velocity_kd.setter
  def velocity_kd(self, value):
    """
    Setter for velocity_kd
    """
    set_group_command_float(self, CommandFloatVelocityKd, value)

  @property
  def velocity_feed_forward(self):
    """
    Feed forward term for velocity (this term is multiplied by the target and added to the output).
    """
    return get_group_command_float(self, CommandFloatVelocityFeedForward)

  @velocity_feed_forward.setter
  def velocity_feed_forward(self, value):
    """
    Setter for velocity_feed_forward
    """
    set_group_command_float(self, CommandFloatVelocityFeedForward, value)

  @property
  def velocity_dead_zone(self):
    """
    Error values within +/- this value from zero are treated as zero (in terms of computed proportional output, input to numerical derivative, and accumulated integral error).
    """
    return get_group_command_float(self, CommandFloatVelocityDeadZone)

  @velocity_dead_zone.setter
  def velocity_dead_zone(self, value):
    """
    Setter for velocity_dead_zone
    """
    set_group_command_float(self, CommandFloatVelocityDeadZone, value)

  @property
  def velocity_i_clamp(self):
    """
    Maximum allowed value for the output of the integral component of the PID loop; the integrated error is not allowed to exceed value that will generate this number.
    """
    return get_group_command_float(self, CommandFloatVelocityIClamp)

  @velocity_i_clamp.setter
  def velocity_i_clamp(self, value):
    """
    Setter for velocity_i_clamp
    """
    set_group_command_float(self, CommandFloatVelocityIClamp, value)

  @property
  def velocity_punch(self):
    """
    Constant offset to the velocity PID output outside of the deadzone; it is added when the error is positive and subtracted when it is negative.
    """
    return get_group_command_float(self, CommandFloatVelocityPunch)

  @velocity_punch.setter
  def velocity_punch(self, value):
    """
    Setter for velocity_punch
    """
    set_group_command_float(self, CommandFloatVelocityPunch, value)

  @property
  def velocity_min_target(self):
    """
    Minimum allowed value for input to the PID controller
    """
    return get_group_command_float(self, CommandFloatVelocityMinTarget)

  @velocity_min_target.setter
  def velocity_min_target(self, value):
    """
    Setter for velocity_min_target
    """
    set_group_command_float(self, CommandFloatVelocityMinTarget, value)

  @property
  def velocity_max_target(self):
    """
    Maximum allowed value for input to the PID controller
    """
    return get_group_command_float(self, CommandFloatVelocityMaxTarget)

  @velocity_max_target.setter
  def velocity_max_target(self, value):
    """
    Setter for velocity_max_target
    """
    set_group_command_float(self, CommandFloatVelocityMaxTarget, value)

  @property
  def velocity_target_lowpass(self):
    """
    A simple lowpass filter applied to the target set point; needs to be between 0 and 1. At each timestep: :math:`x_t = x_t * a + x_{t-1} * (1 - a)`.
    """
    return get_group_command_float(self, CommandFloatVelocityTargetLowpass)

  @velocity_target_lowpass.setter
  def velocity_target_lowpass(self, value):
    """
    Setter for velocity_target_lowpass
    """
    set_group_command_float(self, CommandFloatVelocityTargetLowpass, value)

  @property
  def velocity_min_output(self):
    """
    Output from the PID controller is limited to a minimum of this value.
    """
    return get_group_command_float(self, CommandFloatVelocityMinOutput)

  @velocity_min_output.setter
  def velocity_min_output(self, value):
    """
    Setter for velocity_min_output
    """
    set_group_command_float(self, CommandFloatVelocityMinOutput, value)

  @property
  def velocity_max_output(self):
    """
    Output from the PID controller is limited to a maximum of this value.
    """
    return get_group_command_float(self, CommandFloatVelocityMaxOutput)

  @velocity_max_output.setter
  def velocity_max_output(self, value):
    """
    Setter for velocity_max_output
    """
    set_group_command_float(self, CommandFloatVelocityMaxOutput, value)

  @property
  def velocity_output_lowpass(self):
    """
    A simple lowpass filter applied to the controller output; needs to be between 0 and 1. At each timestep: :math:`x_t = x_t * a + x_{t-1} * (1 - a)`.
    """
    return get_group_command_float(self, CommandFloatVelocityOutputLowpass)

  @velocity_output_lowpass.setter
  def velocity_output_lowpass(self, value):
    """
    Setter for velocity_output_lowpass
    """
    set_group_command_float(self, CommandFloatVelocityOutputLowpass, value)

  @property
  def effort_kp(self):
    """
    Proportional PID gain for effort
    """
    return get_group_command_float(self, CommandFloatEffortKp)

  @effort_kp.setter
  def effort_kp(self, value):
    """
    Setter for effort_kp
    """
    set_group_command_float(self, CommandFloatEffortKp, value)

  @property
  def effort_ki(self):
    """
    Integral PID gain for effort
    """
    return get_group_command_float(self, CommandFloatEffortKi)

  @effort_ki.setter
  def effort_ki(self, value):
    """
    Setter for effort_ki
    """
    set_group_command_float(self, CommandFloatEffortKi, value)

  @property
  def effort_kd(self):
    """
    Derivative PID gain for effort
    """
    return get_group_command_float(self, CommandFloatEffortKd)

  @effort_kd.setter
  def effort_kd(self, value):
    """
    Setter for effort_kd
    """
    set_group_command_float(self, CommandFloatEffortKd, value)

  @property
  def effort_feed_forward(self):
    """
    Feed forward term for effort (this term is multiplied by the target and added to the output).
    """
    return get_group_command_float(self, CommandFloatEffortFeedForward)

  @effort_feed_forward.setter
  def effort_feed_forward(self, value):
    """
    Setter for effort_feed_forward
    """
    set_group_command_float(self, CommandFloatEffortFeedForward, value)

  @property
  def effort_dead_zone(self):
    """
    Error values within +/- this value from zero are treated as zero (in terms of computed proportional output, input to numerical derivative, and accumulated integral error).
    """
    return get_group_command_float(self, CommandFloatEffortDeadZone)

  @effort_dead_zone.setter
  def effort_dead_zone(self, value):
    """
    Setter for effort_dead_zone
    """
    set_group_command_float(self, CommandFloatEffortDeadZone, value)

  @property
  def effort_i_clamp(self):
    """
    Maximum allowed value for the output of the integral component of the PID loop; the integrated error is not allowed to exceed value that will generate this number.
    """
    return get_group_command_float(self, CommandFloatEffortIClamp)

  @effort_i_clamp.setter
  def effort_i_clamp(self, value):
    """
    Setter for effort_i_clamp
    """
    set_group_command_float(self, CommandFloatEffortIClamp, value)

  @property
  def effort_punch(self):
    """
    Constant offset to the effort PID output outside of the deadzone; it is added when the error is positive and subtracted when it is negative.
    """
    return get_group_command_float(self, CommandFloatEffortPunch)

  @effort_punch.setter
  def effort_punch(self, value):
    """
    Setter for effort_punch
    """
    set_group_command_float(self, CommandFloatEffortPunch, value)

  @property
  def effort_min_target(self):
    """
    Minimum allowed value for input to the PID controller
    """
    return get_group_command_float(self, CommandFloatEffortMinTarget)

  @effort_min_target.setter
  def effort_min_target(self, value):
    """
    Setter for effort_min_target
    """
    set_group_command_float(self, CommandFloatEffortMinTarget, value)

  @property
  def effort_max_target(self):
    """
    Maximum allowed value for input to the PID controller
    """
    return get_group_command_float(self, CommandFloatEffortMaxTarget)

  @effort_max_target.setter
  def effort_max_target(self, value):
    """
    Setter for effort_max_target
    """
    set_group_command_float(self, CommandFloatEffortMaxTarget, value)

  @property
  def effort_target_lowpass(self):
    """
    A simple lowpass filter applied to the target set point; needs to be between 0 and 1. At each timestep: :math:`x_t = x_t * a + x_{t-1} * (1 - a)`.
    """
    return get_group_command_float(self, CommandFloatEffortTargetLowpass)

  @effort_target_lowpass.setter
  def effort_target_lowpass(self, value):
    """
    Setter for effort_target_lowpass
    """
    set_group_command_float(self, CommandFloatEffortTargetLowpass, value)

  @property
  def effort_min_output(self):
    """
    Output from the PID controller is limited to a minimum of this value.
    """
    return get_group_command_float(self, CommandFloatEffortMinOutput)

  @effort_min_output.setter
  def effort_min_output(self, value):
    """
    Setter for effort_min_output
    """
    set_group_command_float(self, CommandFloatEffortMinOutput, value)

  @property
  def effort_max_output(self):
    """
    Output from the PID controller is limited to a maximum of this value.
    """
    return get_group_command_float(self, CommandFloatEffortMaxOutput)

  @effort_max_output.setter
  def effort_max_output(self, value):
    """
    Setter for effort_max_output
    """
    set_group_command_float(self, CommandFloatEffortMaxOutput, value)

  @property
  def effort_output_lowpass(self):
    """
    A simple lowpass filter applied to the controller output; needs to be between 0 and 1. At each timestep: :math:`x_t = x_t * a + x_{t-1} * (1 - a)`.
    """
    return get_group_command_float(self, CommandFloatEffortOutputLowpass)

  @effort_output_lowpass.setter
  def effort_output_lowpass(self, value):
    """
    Setter for effort_output_lowpass
    """
    set_group_command_float(self, CommandFloatEffortOutputLowpass, value)

  @property
  def spring_constant(self):
    """
    The spring constant of the module.
    """
    return get_group_command_float(self, CommandFloatSpringConstant)

  @spring_constant.setter
  def spring_constant(self, value):
    """
    Setter for spring_constant
    """
    set_group_command_float(self, CommandFloatSpringConstant, value)

  @property
  def reference_position(self):
    """
    Set the internal encoder reference offset so that the current position matches the given reference command
    """
    return get_group_command_float(self, CommandFloatReferencePosition)

  @reference_position.setter
  def reference_position(self, value):
    """
    Setter for reference_position
    """
    set_group_command_float(self, CommandFloatReferencePosition, value)

  @property
  def reference_effort(self):
    """
    Set the internal effort reference offset so that the current effort matches the given reference command
    """
    return get_group_command_float(self, CommandFloatReferenceEffort)

  @reference_effort.setter
  def reference_effort(self, value):
    """
    Setter for reference_effort
    """
    set_group_command_float(self, CommandFloatReferenceEffort, value)

  @property
  def position(self):
    """
    Position of the module output (post-spring), in radians.
    """
    return get_group_command_highresangle(self, CommandHighResAnglePosition)

  @position.setter
  def position(self, value):
    """
    Setter for position
    """
    set_group_command_highresangle(self, CommandHighResAnglePosition, value)

  @property
  def debug(self):
    return self._debug

  @property
  def position_d_on_error(self):
    """
    Controls whether the Kd term uses the "derivative of error" or "derivative of measurement." When the setpoints have step inputs or are noisy, setting this to :code:`False` can eliminate corresponding spikes or noise in the output.
    """
    return get_group_command_bool(self, CommandBoolPositionDOnError)

  @position_d_on_error.setter
  def position_d_on_error(self, value):
    """
    Setter for position_d_on_error
    """
    set_group_command_bool(self, CommandBoolPositionDOnError, value)

  @property
  def velocity_d_on_error(self):
    """
    Controls whether the Kd term uses the "derivative of error" or "derivative of measurement." When the setpoints have step inputs or are noisy, setting this to :code:`False` can eliminate corresponding spikes or noise in the output.
    """
    return get_group_command_bool(self, CommandBoolVelocityDOnError)

  @velocity_d_on_error.setter
  def velocity_d_on_error(self, value):
    """
    Setter for velocity_d_on_error
    """
    set_group_command_bool(self, CommandBoolVelocityDOnError, value)

  @property
  def effort_d_on_error(self):
    """
    Controls whether the Kd term uses the "derivative of error" or "derivative of measurement." When the setpoints have step inputs or are noisy, setting this to :code:`False` can eliminate corresponding spikes or noise in the output.
    """
    return get_group_command_bool(self, CommandBoolEffortDOnError)

  @effort_d_on_error.setter
  def effort_d_on_error(self, value):
    """
    Setter for effort_d_on_error
    """
    set_group_command_bool(self, CommandBoolEffortDOnError, value)

  @property
  def name(self):
    """
    Sets the name for this module.
    """
    return get_group_command_string(self, CommandStringName)

  @name.setter
  def name(self, value):
    """
    Setter for name
    """
    set_group_command_string(self, CommandStringName, value)

  @property
  def family(self):
    """
    Sets the family for this module.
    """
    return get_group_command_string(self, CommandStringFamily)

  @family.setter
  def family(self, value):
    """
    Setter for family
    """
    set_group_command_string(self, CommandStringFamily, value)

  @property
  def save_current_settings(self):
    """
    Indicates if the module should save the current values of all of its settings.
    """
    return get_group_command_flag(self, CommandFlagSaveCurrentSettings)

  @save_current_settings.setter
  def save_current_settings(self, value):
    """
    Setter for save_current_settings
    """
    set_group_command_flag(self, CommandFlagSaveCurrentSettings, value)

  @property
  def control_strategy(self):
    """
    How the position, velocity, and effort PID loops are connected in order to control motor PWM.
    """
    return get_group_command_enum(self, CommandEnumControlStrategy)

  @control_strategy.setter
  def control_strategy(self, value):
    """
    Setter for control_strategy
    """
    set_group_command_enum(self, CommandEnumControlStrategy, value)

  @property
  def io(self):
    return self._io

  @property
  def led(self):
    """
    The module's LED.
    """
    return self._led


class GroupFeedback(UnmanagedObject):
  """
  Feedback objects have various fields representing feedback from modules;
  which fields are populated depends on the module type and various other settings.
  """

  def __initialize(self):
    self._feedbacks = [None] * self._number_of_modules
    for i in range(self._number_of_modules):
      self._feedbacks[i] = Feedback(hebiGroupFeedbackGetModuleFeedback(self, i))

  def __init__(self, number_of_modules, shared=None):
    if (shared):
      if not (isinstance(shared, GroupFeedback)):
        raise RuntimeError('Parameter shared must be a GroupFeedback')
      elif(number_of_modules != shared.size):
        raise RuntimeError('Requested number of modules does not match shared parameter')
      super(GroupFeedback, self).__init__(shared._internal)
      self._ref = shared._ref.add_ref()
    else:
      self._ref = SharedGroupMessage(number_of_modules,
                                     hebiGroupFeedbackCreate,
                                     hebiGroupFeedbackRelease)
      super(GroupFeedback, self).__init__(self._ref._internal)

    self._number_of_modules = number_of_modules
    self.__initialize()
    self._io = GroupMessageIoFieldContainer(self, 'Feedback')
    self._debug = GroupNumberedFloatFieldContainer(self, 'Feedback', FeedbackNumberedFloatDebug, 9)
    self._led = GroupMessageLEDFieldContainer(self, 'Feedback', FeedbackLedLed)

  def __getitem__(self, key):
    return self._feedbacks[key]

  @property
  def modules(self):
    return self._feedbacks[:]

  @property
  def size(self):
    """
    The number of modules in this group message.
    """
    return self._number_of_modules

  @property
  def board_temperature(self):
    """
    Ambient temperature inside the module (measured at the IMU chip), in degrees Celsius.
    """
    return get_group_feedback_float(self, FeedbackFloatBoardTemperature)

  @property
  def processor_temperature(self):
    """
    Temperature of the processor chip, in degrees Celsius.
    """
    return get_group_feedback_float(self, FeedbackFloatProcessorTemperature)

  @property
  def voltage(self):
    """
    Bus voltage that the module is running at (in Volts).
    """
    return get_group_feedback_float(self, FeedbackFloatVoltage)

  @property
  def velocity(self):
    """
    Velocity of the module output (post-spring), in radians/second.
    """
    return get_group_feedback_float(self, FeedbackFloatVelocity)

  @property
  def effort(self):
    """
    Effort at the module output; units vary (*e.g.*, :math:`N \cdot m` for rotational joints and *N* for linear stages).
    """
    return get_group_feedback_float(self, FeedbackFloatEffort)

  @property
  def velocity_command(self):
    """
    Commanded velocity of the module output (post-spring), in radians/second.
    """
    return get_group_feedback_float(self, FeedbackFloatVelocityCommand)

  @property
  def effort_command(self):
    """
    Commanded effort at the module output; units vary (*e.g.*, :math:`N \cdot m` for rotational joints and *N* for linear stages).
    """
    return get_group_feedback_float(self, FeedbackFloatEffortCommand)

  @property
  def deflection(self):
    """
    Difference (in radians) between the pre-spring and post-spring output position.
    """
    return get_group_feedback_float(self, FeedbackFloatDeflection)

  @property
  def deflection_velocity(self):
    """
    Velocity (in radians/second) of the difference between the pre-spring and post-spring output position.
    """
    return get_group_feedback_float(self, FeedbackFloatDeflectionVelocity)

  @property
  def motor_velocity(self):
    """
    The velocity (in radians/second) of the motor shaft.
    """
    return get_group_feedback_float(self, FeedbackFloatMotorVelocity)

  @property
  def motor_current(self):
    """
    Current supplied to the motor.
    """
    return get_group_feedback_float(self, FeedbackFloatMotorCurrent)

  @property
  def motor_sensor_temperature(self):
    """
    The temperature from a sensor near the motor housing.
    """
    return get_group_feedback_float(self, FeedbackFloatMotorSensorTemperature)

  @property
  def motor_winding_current(self):
    """
    The estimated current in the motor windings.
    """
    return get_group_feedback_float(self, FeedbackFloatMotorWindingCurrent)

  @property
  def motor_winding_temperature(self):
    """
    The estimated temperature of the motor windings.
    """
    return get_group_feedback_float(self, FeedbackFloatMotorWindingTemperature)

  @property
  def motor_housing_temperature(self):
    """
    The estimated temperature of the motor housing.
    """
    return get_group_feedback_float(self, FeedbackFloatMotorHousingTemperature)

  @property
  def position(self):
    """
    Position of the module output (post-spring), in radians.
    """
    return get_group_feedback_highresangle(self, FeedbackHighResAnglePosition)

  @property
  def position_command(self):
    """
    Commanded position of the module output (post-spring), in radians.
    """
    return get_group_feedback_highresangle(self, FeedbackHighResAnglePositionCommand)

  @property
  def debug(self):
    return self._debug

  @property
  def sequence_number(self):
    """
    Sequence number going to module (local)
    """
    return get_group_feedback_uint64(self, FeedbackUInt64SequenceNumber)

  @property
  def receive_time(self):
    """
    Timestamp of when message was received from module (local)
    """
    return get_group_feedback_uint64(self, FeedbackUInt64ReceiveTime)

  @property
  def transmit_time(self):
    """
    Timestamp of when message was transmitted to module (local)
    """
    return get_group_feedback_uint64(self, FeedbackUInt64TransmitTime)

  @property
  def hardware_receive_time(self):
    """
    Timestamp of when message was received by module (remote)
    """
    return get_group_feedback_uint64(self, FeedbackUInt64HardwareReceiveTime)

  @property
  def hardware_transmit_time(self):
    """
    Timestamp of when message was transmitted from module (remote)
    """
    return get_group_feedback_uint64(self, FeedbackUInt64HardwareTransmitTime)

  @property
  def sender_id(self):
    """
    Unique ID of the module transmitting this feedback
    """
    return get_group_feedback_uint64(self, FeedbackUInt64SenderId)

  @property
  def accelerometer(self):
    """
    Accelerometer data, in m/s^2.
    """
    return get_group_feedback_vector3f(self, FeedbackVector3fAccelerometer)

  @property
  def gyro(self):
    """
    Gyro data, in radians/second.
    """
    return get_group_feedback_vector3f(self, FeedbackVector3fGyro)

  @property
  def io(self):
    return self._io

  @property
  def led(self):
    """
    The module's LED.
    """
    return self._led


class GroupInfo(UnmanagedObject):
  """
  Info objects have various fields representing the module state;
  which fields are populated depends on the module type and various other settings.
  """

  def __initialize(self):
    self._infos = [None] * self._number_of_modules
    for i in range(self._number_of_modules):
      self._infos[i] = Info(hebiGroupInfoGetModuleInfo(self, i))

  def __init__(self, number_of_modules, shared=None):
    if (shared):
      if not (isinstance(shared, GroupInfo)):
        raise RuntimeError('Parameter shared must be a GroupInfo')
      elif(number_of_modules != shared.size):
        raise RuntimeError('Requested number of modules does not match shared parameter')
      super(GroupInfo, self).__init__(shared._internal)
      self._ref = shared._ref.add_ref()
    else:
      self._ref = SharedGroupMessage(number_of_modules,
                                     hebiGroupInfoCreate,
                                     hebiGroupInfoRelease)
      super(GroupInfo, self).__init__(self._ref._internal)

    self._number_of_modules = number_of_modules
    self.__initialize()
    self._led = GroupMessageLEDFieldContainer(self, 'Info', InfoLedLed)

  def __getitem__(self, key):
    return self._infos[key]

  def write_gains(self, file):
    """
    Export the gains from this object into a file, creating it if necessary.

    :param file:
    """
    res = hebiGroupInfoWriteGains(self, create_str(file))
    if (res != StatusSuccess):
      from hebi._internal.errors import HEBI_Exception
      raise HEBI_Exception(res, 'hebiGroupInfoWriteGains failed')

  @property
  def modules(self):
    return self._infos[:]

  @property
  def size(self):
    """
    The number of modules in this group message.
    """
    return self._number_of_modules

  @property
  def position_kp(self):
    """
    Proportional PID gain for position
    """
    return get_group_info_float(self, InfoFloatPositionKp)

  @property
  def position_ki(self):
    """
    Integral PID gain for position
    """
    return get_group_info_float(self, InfoFloatPositionKi)

  @property
  def position_kd(self):
    """
    Derivative PID gain for position
    """
    return get_group_info_float(self, InfoFloatPositionKd)

  @property
  def position_feed_forward(self):
    """
    Feed forward term for position (this term is multiplied by the target and added to the output).
    """
    return get_group_info_float(self, InfoFloatPositionFeedForward)

  @property
  def position_dead_zone(self):
    """
    Error values within +/- this value from zero are treated as zero (in terms of computed proportional output, input to numerical derivative, and accumulated integral error).
    """
    return get_group_info_float(self, InfoFloatPositionDeadZone)

  @property
  def position_i_clamp(self):
    """
    Maximum allowed value for the output of the integral component of the PID loop; the integrated error is not allowed to exceed value that will generate this number.
    """
    return get_group_info_float(self, InfoFloatPositionIClamp)

  @property
  def position_punch(self):
    """
    Constant offset to the position PID output outside of the deadzone; it is added when the error is positive and subtracted when it is negative.
    """
    return get_group_info_float(self, InfoFloatPositionPunch)

  @property
  def position_min_target(self):
    """
    Minimum allowed value for input to the PID controller
    """
    return get_group_info_float(self, InfoFloatPositionMinTarget)

  @property
  def position_max_target(self):
    """
    Maximum allowed value for input to the PID controller
    """
    return get_group_info_float(self, InfoFloatPositionMaxTarget)

  @property
  def position_target_lowpass(self):
    """
    A simple lowpass filter applied to the target set point; needs to be between 0 and 1. At each timestep: :math:`x_t = x_t * a + x_{t-1} * (1 - a)`.
    """
    return get_group_info_float(self, InfoFloatPositionTargetLowpass)

  @property
  def position_min_output(self):
    """
    Output from the PID controller is limited to a minimum of this value.
    """
    return get_group_info_float(self, InfoFloatPositionMinOutput)

  @property
  def position_max_output(self):
    """
    Output from the PID controller is limited to a maximum of this value.
    """
    return get_group_info_float(self, InfoFloatPositionMaxOutput)

  @property
  def position_output_lowpass(self):
    """
    A simple lowpass filter applied to the controller output; needs to be between 0 and 1. At each timestep: :math:`x_t = x_t * a + x_{t-1} * (1 - a)`.
    """
    return get_group_info_float(self, InfoFloatPositionOutputLowpass)

  @property
  def velocity_kp(self):
    """
    Proportional PID gain for velocity
    """
    return get_group_info_float(self, InfoFloatVelocityKp)

  @property
  def velocity_ki(self):
    """
    Integral PID gain for velocity
    """
    return get_group_info_float(self, InfoFloatVelocityKi)

  @property
  def velocity_kd(self):
    """
    Derivative PID gain for velocity
    """
    return get_group_info_float(self, InfoFloatVelocityKd)

  @property
  def velocity_feed_forward(self):
    """
    Feed forward term for velocity (this term is multiplied by the target and added to the output).
    """
    return get_group_info_float(self, InfoFloatVelocityFeedForward)

  @property
  def velocity_dead_zone(self):
    """
    Error values within +/- this value from zero are treated as zero (in terms of computed proportional output, input to numerical derivative, and accumulated integral error).
    """
    return get_group_info_float(self, InfoFloatVelocityDeadZone)

  @property
  def velocity_i_clamp(self):
    """
    Maximum allowed value for the output of the integral component of the PID loop; the integrated error is not allowed to exceed value that will generate this number.
    """
    return get_group_info_float(self, InfoFloatVelocityIClamp)

  @property
  def velocity_punch(self):
    """
    Constant offset to the velocity PID output outside of the deadzone; it is added when the error is positive and subtracted when it is negative.
    """
    return get_group_info_float(self, InfoFloatVelocityPunch)

  @property
  def velocity_min_target(self):
    """
    Minimum allowed value for input to the PID controller
    """
    return get_group_info_float(self, InfoFloatVelocityMinTarget)

  @property
  def velocity_max_target(self):
    """
    Maximum allowed value for input to the PID controller
    """
    return get_group_info_float(self, InfoFloatVelocityMaxTarget)

  @property
  def velocity_target_lowpass(self):
    """
    A simple lowpass filter applied to the target set point; needs to be between 0 and 1. At each timestep: :math:`x_t = x_t * a + x_{t-1} * (1 - a)`.
    """
    return get_group_info_float(self, InfoFloatVelocityTargetLowpass)

  @property
  def velocity_min_output(self):
    """
    Output from the PID controller is limited to a minimum of this value.
    """
    return get_group_info_float(self, InfoFloatVelocityMinOutput)

  @property
  def velocity_max_output(self):
    """
    Output from the PID controller is limited to a maximum of this value.
    """
    return get_group_info_float(self, InfoFloatVelocityMaxOutput)

  @property
  def velocity_output_lowpass(self):
    """
    A simple lowpass filter applied to the controller output; needs to be between 0 and 1. At each timestep: :math:`x_t = x_t * a + x_{t-1} * (1 - a)`.
    """
    return get_group_info_float(self, InfoFloatVelocityOutputLowpass)

  @property
  def effort_kp(self):
    """
    Proportional PID gain for effort
    """
    return get_group_info_float(self, InfoFloatEffortKp)

  @property
  def effort_ki(self):
    """
    Integral PID gain for effort
    """
    return get_group_info_float(self, InfoFloatEffortKi)

  @property
  def effort_kd(self):
    """
    Derivative PID gain for effort
    """
    return get_group_info_float(self, InfoFloatEffortKd)

  @property
  def effort_feed_forward(self):
    """
    Feed forward term for effort (this term is multiplied by the target and added to the output).
    """
    return get_group_info_float(self, InfoFloatEffortFeedForward)

  @property
  def effort_dead_zone(self):
    """
    Error values within +/- this value from zero are treated as zero (in terms of computed proportional output, input to numerical derivative, and accumulated integral error).
    """
    return get_group_info_float(self, InfoFloatEffortDeadZone)

  @property
  def effort_i_clamp(self):
    """
    Maximum allowed value for the output of the integral component of the PID loop; the integrated error is not allowed to exceed value that will generate this number.
    """
    return get_group_info_float(self, InfoFloatEffortIClamp)

  @property
  def effort_punch(self):
    """
    Constant offset to the effort PID output outside of the deadzone; it is added when the error is positive and subtracted when it is negative.
    """
    return get_group_info_float(self, InfoFloatEffortPunch)

  @property
  def effort_min_target(self):
    """
    Minimum allowed value for input to the PID controller
    """
    return get_group_info_float(self, InfoFloatEffortMinTarget)

  @property
  def effort_max_target(self):
    """
    Maximum allowed value for input to the PID controller
    """
    return get_group_info_float(self, InfoFloatEffortMaxTarget)

  @property
  def effort_target_lowpass(self):
    """
    A simple lowpass filter applied to the target set point; needs to be between 0 and 1. At each timestep: :math:`x_t = x_t * a + x_{t-1} * (1 - a)`.
    """
    return get_group_info_float(self, InfoFloatEffortTargetLowpass)

  @property
  def effort_min_output(self):
    """
    Output from the PID controller is limited to a minimum of this value.
    """
    return get_group_info_float(self, InfoFloatEffortMinOutput)

  @property
  def effort_max_output(self):
    """
    Output from the PID controller is limited to a maximum of this value.
    """
    return get_group_info_float(self, InfoFloatEffortMaxOutput)

  @property
  def effort_output_lowpass(self):
    """
    A simple lowpass filter applied to the controller output; needs to be between 0 and 1. At each timestep: :math:`x_t = x_t * a + x_{t-1} * (1 - a)`.
    """
    return get_group_info_float(self, InfoFloatEffortOutputLowpass)

  @property
  def spring_constant(self):
    """
    The spring constant of the module.
    """
    return get_group_info_float(self, InfoFloatSpringConstant)

  @property
  def position_d_on_error(self):
    """
    Controls whether the Kd term uses the "derivative of error" or "derivative of measurement." When the setpoints have step inputs or are noisy, setting this to :code:`False` can eliminate corresponding spikes or noise in the output.
    """
    return get_group_info_bool(self, InfoBoolPositionDOnError)

  @property
  def velocity_d_on_error(self):
    """
    Controls whether the Kd term uses the "derivative of error" or "derivative of measurement." When the setpoints have step inputs or are noisy, setting this to :code:`False` can eliminate corresponding spikes or noise in the output.
    """
    return get_group_info_bool(self, InfoBoolVelocityDOnError)

  @property
  def effort_d_on_error(self):
    """
    Controls whether the Kd term uses the "derivative of error" or "derivative of measurement." When the setpoints have step inputs or are noisy, setting this to :code:`False` can eliminate corresponding spikes or noise in the output.
    """
    return get_group_info_bool(self, InfoBoolEffortDOnError)

  @property
  def name(self):
    """
    Sets the name for this module.
    """
    return get_group_info_string(self, InfoStringName)

  @property
  def family(self):
    """
    Sets the family for this module.
    """
    return get_group_info_string(self, InfoStringFamily)

  @property
  def serial(self):
    """
    Gets the serial number for this module (*e.g.*, X5-0001).
    """
    return get_group_info_string(self, InfoStringSerial)

  @property
  def save_current_settings(self):
    """
    Indicates if the module should save the current values of all of its settings.
    """
    return get_group_info_flag(self, InfoFlagSaveCurrentSettings)

  @property
  def control_strategy(self):
    """
    How the position, velocity, and effort PID loops are connected in order to control motor PWM.
    """
    return get_group_info_enum(self, InfoEnumControlStrategy)

  @property
  def led(self):
    """
    The module's LED.
    """
    return self._led


