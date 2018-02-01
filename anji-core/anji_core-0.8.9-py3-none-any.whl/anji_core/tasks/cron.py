import abc
from datetime import datetime, timedelta
import random
from typing import Iterator

from anji_orm import StringField, DatetimeField, FloatField, EnumField, QueryAst
import humanize
from errbot import arg_botcmd
import rethinkdb as R
from croniter import croniter

from ..cartridges import AbstractCartridge, provide_confirmation_logic
from ..types import TaskStatus, MessageType, Reaction, CronWorkerCommandType, ManagerRecordModifyType
from ..utils import command_reaction_decorator
from ..statistic import TimeSeriesCompressModel
from ..manager import SecurityManager
from ..signals import MessageReactionSignal
from .base import BaseTask

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.8.9"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"


class CronTaskStatistic(TimeSeriesCompressModel):

    _table = 'cron_tasks_stat'


class CronTask(BaseTask):  # pylint: disable=too-many-instance-attributes,abstract-method

    cron_expression = StringField(reconfigurable=True, description='Cron Expression')
    last_execute_status = EnumField(TaskStatus, service=True, description='Result of last execution')
    last_compete_timestamp = DatetimeField(service=True, description='Time of last exectuion')
    average_execution_time = FloatField(compute_function='root_mean_square', description='Average execution time', cacheable=False, service=True)

    _table = 'cron_tasks'
    _compressed_stat_model = CronTaskStatistic
    display_name = 'cron task'

    def __init__(self, id_=None, **kwargs):
        super().__init__(id_=id_, **kwargs)
        if not id_:
            assert self.technical_name is not None, "technical_name must be defined!"
            assert self.cron_expression is not None, "cron_expression must be defined!"
            self.execute_timestamp = croniter(self.cron_expression, self.created_timestamp).get_next(datetime)

    def run(self):
        self.start_timestamp = datetime.now(R.make_timezone("00:00"))
        self.send()
        return self.task_execute()

    @abc.abstractmethod
    def task_execute(self):
        pass

    def generate_next(self):
        self.execute_timestamp = croniter(self.cron_expression, datetime.now(R.make_timezone("00:00"))).get_next(datetime)
        self.worker_name = None
        self.worker_uuid = None
        self.last_execute_status = self.status
        self.status = TaskStatus.pending
        self.result = None
        self.complete_timestamp = None
        self.id = None
        self.send()

    def to_describe_dict(self, definer_skip=False):
        base_dict = super().to_describe_dict(definer_skip=definer_skip)
        if self.status == TaskStatus.in_progress:
            base_dict.update({
                'Anji node, that execute task': self.worker_name,
                'Execution start time': humanize.naturaltime(datetime.now(R.make_timezone("00:00")) - self.start_timestamp)
            })
        return base_dict

    def describe_status(self):
        if self.status in [TaskStatus.exception, TaskStatus.canceled]:
            return MessageType.error
        elif self.status in [TaskStatus.in_progress]:
            return MessageType.info
        return MessageType.good

    def done(self, task_exception=False, task_result=None):
        super().done(task_exception=task_exception, task_result=task_result)
        self.last_compete_timestamp = self.complete_timestamp
        self.generate_next()

    def is_stuck(self, rms_coef):
        if self.status != TaskStatus.in_progress:
            return False
        if not self.start_timestamp and self.status == TaskStatus.in_progress:
            return True
        current_execution_time = (datetime.now(R.make_timezone("00:00")) - self.start_timestamp).total_seconds()
        return rms_coef * self.root_mean_square() < current_execution_time

    def merge_configuration(self, cron_expression, target_hostname, execute_args, execute_kwargs):
        self.cron_expression = cron_expression
        self.execute_args = execute_args
        self.execute_kwargs = execute_kwargs
        self.worker_hostname = target_hostname
        self.send()


class FakeCronTask(CronTask):

    def task_execute(self):
        pass

    def generate_name(self):
        return self.technical_name


@provide_confirmation_logic
class CronCartridge(AbstractCartridge):

    __errdoc__ = 'Core commands to control cron tasks'
    name = 'Core cron tasks commands'
    technical_name = 'core_cron'
    base_command_prefix = 'cron'

    @arg_botcmd('technical_names', type=str, nargs='*', help='Cron task technical name')
    @arg_botcmd('--auto', dest='auto', action='store_true', help='Try to find stuck fron tasks')
    def cron_reset(self, mess, technical_names=None, auto=None):
        """
        Command to force rerun cron tasks
        """
        cron_task_list = []
        if auto:
            cron_task_list.extend(self.manager.get_stuck_cron_tasks())
        if technical_names:
            cron_tasks = CronTask.query(
                (CronTask.status == TaskStatus.in_progress) &
                CronTask.technical_name.one_of(*technical_names)
            )
            cron_task_list.extend(cron_tasks)
        if not cron_task_list:
            self.shared.signals.fire(
                MessageReactionSignal(
                    mess,
                    Reaction.empty,
                    alternative_text='Unfortunately, I have nothing to run :('
                )
            )
        else:
            for cron_task in cron_task_list:
                cron_task.free()
            with self.shared.render as r:
                r.title('List of reseted cron tasks')
                r.reply_to(mess)
                with r.bulleted_list() as lst:
                    for cron_task in cron_task_list:
                        lst.add(cron_task.technical_name)
            self.shared.internal_bus.cron_broadcast(CronWorkerCommandType.refresh, self.shared.bot.manager_env['node'])

    @arg_botcmd('--days-before', dest='days_before', help='Days offset to target data', type=int, default=1)
    @arg_botcmd('--offset', dest='offset', help='Skip offset to target data', type=int, default=3)
    @command_reaction_decorator
    def cron_stat_compress(self, _mess, days_before=None, offset=None):
        CronTaskStatistic.automatic_original_data_compress(days_before, offset)
        CronTaskStatistic.automatic_compressed_data_compress(self.shared.statistic)

    @arg_botcmd('--count', dest='count', type=int, default=100, help='Fake records count')
    @arg_botcmd('--days-offset', dest='days_offset', help='Fake records days shift', type=int, default=2)
    @arg_botcmd('--execution-time', dest='execution_time', help='Average execution time', type=float, default=9.1)
    @arg_botcmd('technical_name', type=str, help='Task technical name')
    @command_reaction_decorator
    def cron_stat_generate_fake(self, _mess, technical_name=None, days_offset=None, count=None, execution_time=None):
        start_execution = datetime.now(R.make_timezone("00:00")) - timedelta(days=days_offset)
        for _ in range(0, count):
            task_execution_time = random.gauss(execution_time, 1)
            fake_cron_data = FakeCronTask(
                complete_timestamp=start_execution + timedelta(seconds=task_execution_time),
                created_timestamp=start_execution,
                cron_expression='*/1 * * * *',
                technical_name=technical_name,
                execute_timestamp=start_execution,
                execution_time=task_execution_time,
                start_timestamp=start_execution,
                status=TaskStatus.done
            )
            fake_cron_data.send()
            start_execution -= 3 * timedelta(seconds=task_execution_time)


class CronManager(SecurityManager):

    controlled_model = CronTask
    controlled_cartridge = CronCartridge
    control_prefix = 'cron'
    autoload_enabled = False

    @classmethod
    def active_record_filter(cls) -> QueryAst:
        return CronTask.status.one_of(TaskStatus.in_progress, TaskStatus.pending)

    @property
    def manager_short_name(self) -> str:
        return "cron"

    def process_cartridge(self, cartridge):
        if getattr(cartridge, 'cron_tasks'):
            for cron_type, cron_class in cartridge.cron_tasks.items():
                cron_class.model_subtype = cron_type
                self.add_model_subtype(cron_class)

    def get_stuck_cron_tasks(self, rms_coef=2):
        cron_tasks = CronTask.query(CronTask.status == TaskStatus.in_progress)
        return filter(lambda x: x.is_stuck(rms_coef), cron_tasks)

    def next_tasks(self) -> Iterator[CronTask]:
        now = datetime.now(R.make_timezone("00:00"))
        return filter(lambda task: task.execute_timestamp <= now, self.get_record_list(self.bot.sudo))

    def post_modify_hook(self, modify_type: ManagerRecordModifyType, record: CronTask) -> None:
        self.bot.shared.internal_bus.cron_broadcast(CronWorkerCommandType.refresh, self.bot.manager_env['node'])
