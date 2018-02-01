import abc
from datetime import datetime
from typing import Dict, Any
import logging

from anji_orm import StringField, DatetimeField, ListField, DictField, FloatField, EnumField, QueryAst
import rethinkdb as R

from ..types import TaskStatus, FieldMark, MessageType
from ..statistic import TimeSeriesMixin
from ..manager import SecureModel

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.8.10"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"

_log = logging.getLogger(__name__)


class BaseTask(SecureModel, TimeSeriesMixin):  # pylint: disable=too-many-instance-attributes

    # Base variables
    status = EnumField(TaskStatus, default=TaskStatus.pending, service=True, secondary_index=True, displayed=False)

    # Data variables
    created_timestamp = DatetimeField(service=True, description='Task creation time')
    execute_timestamp = DatetimeField(service=True, description='Estimated time of arrival')
    start_timestamp = DatetimeField(service=True, default=None, description='Task execute start time')

    # Worker data
    worker_name = StringField(service=True, displayed=False)
    worker_uuid = StringField(service=True, displayed=False)
    worker_hostname = StringField(default='*', optional=True, description='Target task server hostname')

    # Before-after logic,
    before_task_uuid_list = ListField(service=True, displayed=False)
    after_task_command_list = ListField(service=True, displayed=False)

    complete_timestamp = DatetimeField(service=True, default=None, field_marks=[FieldMark.timeseries_timestamp], description='Task execution finish time')
    result = DictField(service=True, description='Task result', displayed=False)
    execution_time = FloatField(
        service=True,
        description='Execution time in seconds',
        field_marks=[FieldMark.timeseries_value]
    )
    predicted_execution_time = FloatField(service=True, description='Predicted execution time in seconds')

    def __init__(self, id_: str = None, **kwargs) -> None:
        super().__init__(id_=id_, **kwargs)
        if not id_:
            self.name = self.generate_name()

    def book(self, worker_name: str, worker_uuid: str) -> bool:
        result = self.execute(self.table.get(self.id).update(
            R.branch(
                R.row['status'] == TaskStatus.pending.value,
                {"status": TaskStatus.in_progress.value},
                None
            )
        ))
        if not result.get("replaced"):
            _log.debug('Task %s already booked by another worker, skip.', self.id)
            return False
        self.execute(self.table.get(self.id).update({
            'worker_name': worker_name,
            'worker_uuid': worker_uuid,
        }))
        self.status = TaskStatus.in_progress
        self.worker_name = worker_name
        self.worker_uuid = worker_uuid
        return True

    def calculate_execution_time(self):
        self.execution_time = (self.complete_timestamp - self.start_timestamp).total_seconds()

    def describe_status(self) -> MessageType:
        return MessageType.info

    @classmethod
    def additional_statistic_filter(cls, current_query: QueryAst) -> QueryAst:
        return current_query & (cls.status == TaskStatus.done)

    def done(self, task_exception: str = False, task_result: Dict[str, Any] = None) -> None:
        if task_exception:
            self.status = TaskStatus.exception
            self.result = {
                'traceback': task_exception
            }
        else:
            self.status = TaskStatus.done
            self.result = task_result
        self.complete_timestamp = datetime.now(R.make_timezone("00:00"))
        self.calculate_execution_time()
        self.send()

    def cancel(self) -> bool:
        result = self.execute(self.table.get(self.id).update(
            R.branch(
                R.row['status'] == TaskStatus.pending,
                {"status": TaskStatus.canceled},
                None
            )
        ))
        if not result.get("replaced"):
            _log.debug('Task %s cannot be canceled, skip.', self.id)
            return False
        self.delete()
        return True

    def free(self) -> None:
        self.status = TaskStatus.pending
        self.worker_uuid = None
        self.worker_name = None
        self.send()

    @abc.abstractmethod
    def generate_name(self):
        pass

    @abc.abstractmethod
    def run(self):
        pass

    def __str__(self) -> str:
        return self.name
