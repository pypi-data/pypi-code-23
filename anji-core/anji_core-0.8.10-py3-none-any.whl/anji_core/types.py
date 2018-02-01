"""
Module for enumeration for types, states, statuses and another useful things to avoid using magic strings
"""

from enum import Enum, auto
from typing import Optional

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.8.10"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"


class BaseAnjiEnum(Enum):

    def __str__(self) -> str:
        return self.name

    @staticmethod
    def _generate_next_value_(name, _start, _count, _last_values):
        """
        Override default enum implementation to use field name instead of number
        """
        return name

    @classmethod
    def search(cls, name) -> Optional['BaseAnjiEnum']:
        if isinstance(name, cls):
            return name
        if name in cls.__members__:
            return cls[name]
        return None


class NodeState(BaseAnjiEnum):
    """
    Constant class for node states
    """
    free = auto()
    working = auto()
    disabled = auto()
    deactivated = auto()
    lost = auto()


class NodeType(BaseAnjiEnum):
    """
    Constant class for node types
    """
    master = auto()
    worker = auto()
    cron_worker = auto()
    system_analyze = auto()


class TaskStatus(BaseAnjiEnum):
    """
    Constant class for task statuses
    """
    pending = auto()
    in_progress = auto()
    done = auto()
    canceled = auto()
    exception = auto()
    delayed = auto()


class TaskType(BaseAnjiEnum):

    regular = auto()
    cron = auto()


class ServicesStatus(BaseAnjiEnum):
    """
    Constant class for service statuses
    """
    stopped = auto()
    absent = auto()
    running = auto()
    restarting = auto()
    unknown = auto()


class MessageType(BaseAnjiEnum):
    """
    Message types, that response for message colors and design.
    """
    info = auto()
    good = auto()
    warning = auto()
    error = auto()
    none = auto()

    @classmethod
    def slack_color(cls, message_type):
        """
        Convert message type to slack card color
        """
        if isinstance(message_type, str):
            message_type = cls.search(message_type)
        return {
            MessageType.info: '#439FE0',
            MessageType.good: 'good',
            MessageType.warning: 'warning',
            MessageType.error: 'danger',
            MessageType.none: None
        }[message_type]


class Reaction(BaseAnjiEnum):

    confirm = auto()
    waiting = auto()
    deny = auto()
    okey = auto()
    processing = auto()
    accepted = auto()
    problem = auto()
    processing_next = auto()
    empty = auto()
    blocked = auto()


class RenderFeatures(BaseAnjiEnum):

    reaction = auto()


class ServiceUnavailableType(BaseAnjiEnum):

    temporary = auto()
    taskwide = auto()


class InternalMessageType(BaseAnjiEnum):

    fake_message = auto()
    cron_worker_command = auto()


class CronWorkerCommandType(BaseAnjiEnum):

    refresh = auto()


class InternalMessageState(BaseAnjiEnum):

    posted = auto()
    consumed = auto()


class FieldMark(BaseAnjiEnum):

    timeseries_weight = auto()
    timeseries_value = auto()
    timeseries_timestamp = auto()


class TimeseriesCompressPolicy(BaseAnjiEnum):

    simple = auto()
    class_search = auto()


class EventState(BaseAnjiEnum):

    new = auto()
    consumed = auto()
    invalid = auto()


class SecurityModel(BaseAnjiEnum):

    free_for_anyone = auto()
    for_authorized_users = auto()
    admin_only = auto()

    @staticmethod
    def max(*security_models):
        if SecurityModel.admin_only in security_models:
            return SecurityModel.admin_only
        elif SecurityModel.for_authorized_users in security_models:
            return SecurityModel.for_authorized_users
        return SecurityModel.free_for_anyone


class ManagerRecordModifyType(BaseAnjiEnum):

    remove = auto()
    create = auto()
    update = auto()
