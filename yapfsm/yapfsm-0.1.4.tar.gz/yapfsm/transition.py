"""All classes that implement transitions."""
# coding=utf-8

import abc
import typing
from functools import total_ordering

from .exceptions import ConfigurationError, StateTransitionError


if typing.TYPE_CHECKING:  # pragma: no cover
  from . import engine  # pylint: disable=unused-import

__all__ = [
  'TransitionOption',
  'SimpleTransition',
  'Transition',
  'StateType',
  'ContextType',
  'DescribedTransition',
  'SimpleDescribedTransition',
]

StateType = typing.TypeVar('StateType')
ContextType = typing.TypeVar('ContextType')

TransitionOption = typing.NamedTuple(
  'TransitionOption',
  (
    ("transition", "Transition"),
    ("transition_name", str),
    ("from_state", StateType),
    ("to_state", StateType),
    ("allowed", bool),
    # If transition is disallowed this should tell you why
    ("reason", typing.Optional[str]),
  )
)


class Transition(typing.Generic[StateType, ContextType]):
  """Transition base class."""

  def __init__(  # pylint: disable=unused-argument
      self,
      transition_name: str,
      from_state: typing.Optional[StateType],
      to_state: typing.Optional[StateType],
      **kwargs
  ):
    """

    :param transition_name: Name of transition, this name must be unique.
    :param from_state: Initial state. None means "from any state".
    :param to_state: Final state.
    :param kwargs: This class ignores any extra kwargs.
    """
    self.from_state = from_state
    self.to_state = to_state
    self.transition_name = transition_name

  @abc.abstractmethod
  def can_transition(
      self,
      machine: 'engine.MachineConfiguration',
      from_state: typing.Optional[StateType],
      context: ContextType = None,
      extra_args: dict = None
  ) -> TransitionOption:
    """Return object that describes whether this transition is currently legal. """
    raise NotImplementedError

  def transition(
      self,
      machine: 'engine.MachineConfiguration',
      from_state: typing.Optional[StateType],
      context: ContextType = None,
      extra_args: dict = None
  ) -> StateType:
    """Perform the transition. """
    option = self.can_transition(
      machine=machine,
      from_state=from_state,
      context=context,
      extra_args=extra_args
    )
    if not option.allowed:
      raise StateTransitionError(
        "Illegal transition '{}'".format(option.reason)
      )
    return option.to_state

  def __eq__(self, other):
    return self.transition_name == other.transition_name

  def __hash__(self):
    return hash(self.transition_name)


@total_ordering
class DescribedTransition(Transition[StateType, ContextType]):
  """
  Transition with label, description and priority.

  Priority is used to sort transitions
  """

  def __init__(
      self,
      transition_name: str,
      from_state: typing.Optional[StateType],
      to_state: typing.Optional[StateType],
      label: str,
      priority: int = None,
      description: str = None,
      **kwargs
  ):
    super().__init__(transition_name, from_state, to_state, **kwargs)
    self.label = label
    self.description = description
    if priority is None:
      priority = to_state
    self.priority = priority

  def __ge__(self, other):
    return (
      (self.priority, self.label, self.transition_name) >
      (other.priority, other.label, other.transition_name)
    )


class SimpleTransition(Transition[StateType, ContextType]):
  """Transition that can be performed always."""

  def __init__(self, transition_name: str, from_state: typing.Optional[StateType],
               to_state: typing.Optional[StateType], **kwargs):
    super().__init__(transition_name, from_state, to_state, **kwargs)
    if to_state is None:
      raise ConfigurationError("Need to set to_state for simple transition")

  def _on_successful_transition(
      self,
      machine: 'engine.MachineConfiguration',
      from_state: typing.Optional[StateType],
      to_state: typing.Optional[StateType],
      context: ContextType = None,
      extra_args: dict = None
  ):
    """
    Callback called from ``transition`` on a valid transition.

    Called after ``can_transition``` allowed transition.
    """

  def _make_transition_option(  # pylint: disable=unused-argument
      self,
      allowed: bool,
      **kwargs
  ):
    """Create transition option object, setting sane defaults."""

    def get(name):
      """Read field from kwargs and if None get from self."""
      value = kwargs.get(name, getattr(self, name, None))
      if value is None:
        raise ValueError("Transition property {} is undefined".format(name))
      return value

    if not (allowed or kwargs.get('reason')):
      raise ValueError("Please specify reason if transition is not allowed.")

    return TransitionOption(
      transition_name=self.transition_name,
      from_state=get('from_state'),
      to_state=get('to_state'),
      allowed=allowed,
      reason=kwargs.get('reason'),
      transition=self
    )

  def can_transition(  # pylint: disable=unused-argument
      self,
      machine: 'engine.MachineConfiguration',
      from_state: typing.Optional[StateType],
      context: ContextType = None,
      extra_args: dict = None
  ) -> TransitionOption:
    """Always allow transition."""

    if extra_args is None:
      extra_args = {}

    return self._make_transition_option(
      allowed=True,
      from_state=from_state,
      context=context,
      **extra_args
    )

  def transition(
      self,
      machine: 'engine.MachineConfiguration',
      from_state: typing.Optional[StateType],
      context: ContextType = None,
      extra_args: dict = None
  ) -> StateType:
    """Perform the transition. """
    to_state = super().transition(
      machine=machine,
      from_state=from_state,
      context=context,
      extra_args=extra_args
    )
    self._on_successful_transition(
      to_state=to_state,
      machine=machine,
      from_state=from_state,
      context=context,
      extra_args=extra_args
    )
    return to_state


class SimpleDescribedTransition(
    DescribedTransition[StateType, ContextType],
    SimpleTransition[StateType, ContextType]
):
  """Transition that can be performed always and it has a description."""
  pass
