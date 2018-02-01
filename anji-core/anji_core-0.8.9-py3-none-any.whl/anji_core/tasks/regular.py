import abc
import random
from datetime import datetime, timedelta
import time
from typing import List

from anji_orm import IntField, LinkField, QueryAst
import humanize
from errbot import arg_botcmd
import rethinkdb as R

from ..cartridges import AbstractCartridge, provide_confirmation_logic
from ..types import TaskStatus, Reaction, RenderFeatures, TimeseriesCompressPolicy, MessageType, ManagerRecordModifyType
from ..messages import Message
from ..statistic import TimeSeriesCompressModel
from ..utils import command_reaction_decorator
from ..manager import SecurityManager
from .base import BaseTask

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.8.9"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"


class RegularTaskStatistic(TimeSeriesCompressModel):

    _table = 'tasks_stat'
    compress_policy = TimeseriesCompressPolicy.class_search


class RegularTask(BaseTask):  # pylint: disable=abstract-method

    _table = 'tasks'
    _compressed_stat_model = RegularTaskStatistic

    technical_name = IntField(description='Task number', definer=False)
    message_link = LinkField(Message, service=True, displayed=False)

    def __init__(self, id_=None, technical_name=None, **kwargs):
        if not technical_name:
            technical_name = self.generate_technical_name()
        super().__init__(id_=id_, technical_name=technical_name, **kwargs)

    def set_delay(self, delay: int) -> None:
        self.execute_timestamp = datetime.now(R.make_timezone("00:00")) + timedelta(minutes=delay)
        if delay > 0:
            self.status = TaskStatus.delayed
            self.shared.bot.track_delayed_task(self)
        else:
            self.status = TaskStatus.pending

    @staticmethod
    def generate_technical_name() -> int:
        base_query = RegularTask.db_query(RegularTask.status.one_of(TaskStatus.pending, TaskStatus.in_progress, TaskStatus.delayed))
        if RegularTask.execute(base_query.count()) == 0:
            return 1
        min_number = RegularTask.execute(base_query.pluck('technical_name').min())['technical_name']
        max_number = RegularTask.execute(base_query.pluck('technical_name').max())['technical_name']
        return (min_number - 1) if min_number > 1 else (max_number + 1)

    def done(self, task_exception=False, task_result=None):
        self.technical_name = -1
        super().done(task_exception=task_exception, task_result=task_result)
        self.result['title'] = f"{self.name} execution result"

    def run(self):
        self.start_timestamp = datetime.now(R.make_timezone("00:00"))
        self.send()
        return self.task_execute()

    @abc.abstractmethod
    def task_execute(self):
        pass

    def to_describe_dict(self, definer_skip=False):
        base_dict = super().to_describe_dict(definer_skip=definer_skip)
        if self.status == TaskStatus.in_progress:
            now = datetime.now(R.make_timezone("00:00"))
            if self.start_timestamp:
                end_time = self.start_timestamp + timedelta(seconds=self.predicted_execution_time)
                base_dict['Will be finished'] = 'soon' if end_time < now else humanize.naturaltime(now - end_time)
                base_dict['Exection started'] = humanize.naturaltime(now - self.start_timestamp)
                base_dict['Worker name'] = self.worker_name
        return base_dict


class TestTask(RegularTask):

    task_delay = IntField(description='Task sleep time', definer=True)

    def task_execute(self):
        time.sleep(self.task_delay)
        return dict(
            body='Test task result',
            message_type=MessageType.info
        )

    def generate_name(self):
        return "Test task"


@provide_confirmation_logic
class TasksCartridge(AbstractCartridge):

    __errdoc__ = 'Core commands to control tasks'
    name = 'Core tasks commands'
    technical_name = 'core_tasks'
    base_command_prefix = 'task'

    @arg_botcmd('--full', dest='full_recalculation', action='store_true', default=False, help='Use full recalculation, instead of empty field fill logic')
    def task_stat_refresh(self, mess, full_recalculation=None):
        """
        Command to recompute task execution time. Just to use for backfixes
        """
        reaction_is_supported = self.shared.render.is_support(RenderFeatures.reaction)
        if reaction_is_supported:
            self.shared.render.add_reaction(mess, Reaction.processing)
        task_search = R.table(RegularTask._table)
        if not full_recalculation:
            task_search = task_search.filter(lambda task: (~task.has_fields('execution_time')))
        tasks = RegularTask.execute(task_search)
        if tasks:
            for task in tasks:
                task.calculate_execution_time()
                task.send()
            if reaction_is_supported:
                self.shared.render.remove_reaction(mess, Reaction.processing)
                self.shared.render.add_reaction(mess, Reaction.confirm)
            else:
                self.shared.render.reply(f'For {len(tasks)} tasks execution time was recomputed!', mess)
        else:
            if reaction_is_supported:
                self.shared.render.remove_reaction(mess, Reaction.processing)
                self.shared.render.add_reaction(mess, Reaction.empty)
            else:
                self.shared.render.reply('Nothing to do ...', mess)

    @arg_botcmd('--days-before', dest='days_before', help='Days offset to target data', type=int, default=7)
    @arg_botcmd('--offset', dest='offset', help='Skip offset to target data', type=int, default=3)
    @command_reaction_decorator
    def task_stat_compress(self, _mess, days_before=None, offset=None):
        RegularTaskStatistic.automatic_original_data_compress(days_before, offset)
        RegularTaskStatistic.automatic_compressed_data_compress(self.shared.statistic)

    @arg_botcmd('--count', dest='count', type=int, default=100, help='Fake records count')
    @arg_botcmd('--days-offset', dest='days_offset', help='Fake records days shift', type=int, default=10)
    @arg_botcmd('--execution-time', dest='execution_time', help='Average execution time', type=float, default=9.1)
    @arg_botcmd('task_arg', type=int, help='Task argument')
    @command_reaction_decorator
    def task_stat_generate_fake(self, _mess, task_arg=None, days_offset=None, count=None, execution_time=None):
        start_execution = datetime.now(R.make_timezone("00:00")) - timedelta(days=days_offset)
        for _ in range(0, count):
            task_execution_time = random.gauss(execution_time, 1)
            fake_regular_data = TestTask(
                task_number=-1,
                delay=0,
                task_delay=task_arg,
                complete_timestamp=start_execution + timedelta(seconds=task_execution_time),
                created_timestamp=start_execution,
                execute_timestamp=start_execution,
                execution_time=task_execution_time,
                start_timestamp=start_execution,
                status=TaskStatus.done
            )
            fake_regular_data.send()
            start_execution -= 3 * timedelta(seconds=task_execution_time)


class TaskManager(SecurityManager):

    controlled_model = RegularTask
    controlled_cartridge = TasksCartridge
    control_prefix = 'task'
    autoload_enabled = False
    control_commands_enable = False

    @classmethod
    def active_record_filter(cls) -> QueryAst:
        return RegularTask.status.one_of(TaskStatus.in_progress, TaskStatus.pending, TaskStatus.delayed)

    def post_modify_hook(self, modify_type: ManagerRecordModifyType, record: RegularTask) -> None:
        if modify_type == ManagerRecordModifyType.remove:
            current_task = next(filter(lambda x: x.id == record.id, record.shared.bot.delayed_tasks), None)
            if current_task is not None:
                record.shared.bot.delayed_tasks.remove(current_task)

    @property
    def manager_short_name(self) -> str:
        return "task"

    def fetch_all_tasks(self) -> List[RegularTask]:
        return RegularTask.query(
            (RegularTask.status == TaskStatus.pending) &
            (RegularTask.worker_hostname.one_of(self.bot.bot_config.ANJI_HOSTNAME, '*'))
        )

    def subscribe_query(self) -> R.RqlQuery:
        return RegularTask.db_query(
            (RegularTask.status == TaskStatus.pending) &
            (RegularTask.worker_hostname.one_of(self.bot.bot_config.ANJI_HOSTNAME, '*'))
        )
