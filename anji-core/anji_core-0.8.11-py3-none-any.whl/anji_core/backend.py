import logging
from abc import abstractmethod
from typing import Type, Callable, Dict, Any, List
import traceback
from multiprocessing.connection import Connection
from threading import Thread
from datetime import datetime
import sys
import time

from anji_orm import Model, register
from anji_orm.model import fetch
from errbot.core import ErrBot, Message, Identifier
from errbot import cmdfilter
import trafaret as T
import rethinkdb as R
from trafaret_config import read_and_validate
import coloredlogs
import consul

from .cartridges import CartridgeRegistry
from .render import get_render_engine
from .types import NodeState, NodeType, TaskType, TaskStatus, InternalMessageType, CronWorkerCommandType
from .nodes import Node
from .report import ReportEngine
from .manager import ManagerMetaclass
from .flow import FlowManager
from .signals import SignalBus, TaskDoneSignal, FlowNextSignal, TaskStartedSignal, TaskFailedSignal
from .security import guard
from .internal import InternalBus, InternalMessage, INTERNAL_BUS_LABEL
from .statistic import StatisticEngine
from .tasks import RegularTask

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.8.11"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"


MAGIC_SLEEP_CONSTANT = 5
BORDER_SYMBOL_COUNT = 50


log = logging.getLogger('anji.backend.tasks')


class HealthyCheckThread(Thread):

    def __init__(
            self, bot: 'AnjiBackendMixin') -> None:
        super().__init__(daemon=True)
        self.bot = bot

    def run(self) -> None:
        while True:
            try:
                self.bot.activity_report()
                time.sleep(30)
            # use board exception to make sure that thread will not stop
            except Exception as e:  # pylint: disable=broad-except
                log.error(e)


class MessageProcesser(Thread):

    def __init__(
            self, supervisor_connection: Connection, bot: 'AnjiBackendMixin') -> None:
        super().__init__(daemon=True)
        self.supervisor_connection = supervisor_connection
        self.bot = bot

    def run(self) -> None:
        while True:
            try:
                self.bot.supervisor_connection_check(None)
            # use board exception to make sure that thread will not stop
            except Exception as e:  # pylint: disable=broad-except
                log.error(e)


class DelayedTaskProcesser(Thread):

    def __init__(
            self, bot: 'AnjiBackendMixin') -> None:
        super().__init__(daemon=True)
        self.bot = bot

    def run(self) -> None:
        self.bot.log_config()
        self.bot.delayed_tasks += RegularTask.query(RegularTask.status == TaskStatus.delayed)
        log.info('Fetched %d tasks from database', len(self.bot.delayed_tasks))
        while True:
            try:
                already_started_tasks: List[RegularTask] = []
                current_time = datetime.now(R.make_timezone("00:00"))
                for delayed_task in self.bot.delayed_tasks:
                    if delayed_task.execute_timestamp <= current_time:
                        log.info('Undelay regular task %s with delayed task processer', delayed_task.name)
                        delayed_task.status = TaskStatus.pending
                        delayed_task.send()
                        already_started_tasks.append(delayed_task)
                for already_started_task in already_started_tasks:
                    self.bot.delayed_tasks.remove(already_started_task)
                time.sleep(MAGIC_SLEEP_CONSTANT)
            # use board exception to make sure that thread will not stop
            except Exception as e:  # pylint: disable=broad-except
                log.error(e)


class AnjiBackendMixin(ErrBot):  # pylint: disable=too-many-instance-attributes,too-many-public-methods

    def __init__(self, config: object) -> None:
        super().__init__(config)
        self.log = log
        self.supervisor_connection: Connection = None
        self.message_processer: MessageProcesser = None
        self.node_type = config.ANJI_BOT_TYPE
        self.register = register
        register.init(
            dict(
                db=self.bot_config.ANJI_RETHINK_DB,
                host=self.bot_config.ANJI_RETHINK_DB_HOST,
                port=self.bot_config.ANJI_RETHINK_DB_PORT,
                user=self.bot_config.ANJI_RETHINK_DB_USER,
                password=self.bot_config.ANJI_RETHINK_DB_PASSWORD
            ),
            pool_size=10
        )
        register.load(database_setup=self.node_type == NodeType.master)
        self.pool = register.pool
        guard.init_with_bot(self)
        # Bot initialization
        self.type = self.bot_config.ANJI_BOT_TYPE
        self.bot_name = self.bot_config.ANJI_BOT_NAME
        self.sudo = self.bot_config.BOT_ADMINS[0]
        self.state = NodeState.free
        self.node = Node.create_node_from_bot(self)
        self.uuid = self.node.id
        # Load configuration
        self.flow = FlowManager(self)
        self.configuration = read_and_validate('services.yml', self.build_trafaret())
        # Load managers
        ManagerMetaclass.init_managers(self)
        self.cartridge_registry = CartridgeRegistry(self)
        # First run service initialization
        # to get patched cartridges, like ServiceCartridge
        self.cartridge_registry.load_cartridges()
        ManagerMetaclass.load_managers()
        self.cartridge_registry.inject_commands()
        self.shared = Model.shared
        # Load backend specified parts
        Model.shared.share('bot', self)
        Model.shared.share('render', get_render_engine(self))
        Model.shared.share('report', ReportEngine(self, self.configuration['report']))
        Model.shared.share('signals', SignalBus(self))
        Model.shared.share('internal_bus', InternalBus())
        Model.shared.share('statistic', StatisticEngine(self.bot_config.ANJI_CUTOFF_COEF))
        Model.shared.share('consul', consul.Consul(
            host=self.bot_config.ANJI_CONSUL_AGENT_HOST,
            port=self.bot_config.ANJI_CONSUL_AGENT_PORT,
            scheme=self.bot_config.ANJI_CONSUL_AGENT_SCHEME
        ))
        # Load flows
        for flow in self.configuration.get('flow', []):
            self.flow.load_flow(flow)
        # Load signal bus
        self.command_filters.append(self.global_security_filter)
        if self.node.type == NodeType.master:
            self.delayed_tasks: List[RegularTask] = []
            self.delayed_task_processor = DelayedTaskProcesser(self)
            self.delayed_task_processor.start()
        self.healthy_check_thread = HealthyCheckThread(self)
        self.healthy_check_thread.start()

    def multiprocess_mode(self, supervisor_connection: Connection) -> None:
        self.supervisor_connection = supervisor_connection
        if self.node_type in [NodeType.master, NodeType.worker]:
            self.message_processer = MessageProcesser(self.supervisor_connection, self)
            self.message_processer.start()

    def log_config(self) -> None:
        if self.supervisor_connection is not None:
            coloredlogs.install(logging.INFO, fmt=f'[%(asctime)s] ({self.node.name}) %(name)s:%(levelname)s: %(message)s')
        else:
            coloredlogs.install(logging.INFO, fmt='[%(asctime)s] %(name)s:%(levelname)s: %(message)s')

    @property
    def manager_env(self) -> Dict:
        return ManagerMetaclass.manager_env

    def warn_admins(self, warning: str) -> None:
        """
        Send a warning to the administrators of the bot.
        Override to patch warning
        :param warning: The markdown-formatted text of the message to send.
        """

        border = "=" * BORDER_SYMBOL_COUNT
        warning = f"{border}\nHostname {self.bot_config.ANJI_HOSTNAME} and node name {self.bot_config.ANJI_BOT_NAME} \n{border}\n{warning}"
        for admin in self._admins_to_notify():
            self.send(self.build_identifier(admin), warning)

    def is_from_self(self, msg: Message, disable_command_check: bool = False) -> bool:  # pylint: disable=arguments-differ
        if msg.body.startswith(self.bot_config.BOT_PREFIX) and not disable_command_check:
            return False
        return super().is_from_self(msg)

    def connect_callback(self) -> None:
        super().connect_callback()
        self.set_default_values(self.configuration.get('default', {}))
        guard.update_from_storage()
        guard.process_command_from_cartridges()
        self.state = NodeState.free
        self.activity_report()

    def disconnect_callback(self) -> None:
        self.state = NodeState.deactivated
        self.activity_report()
        super().disconnect_callback()

    def activity_report(self):
        self.node.update_last_activity(self.state)
        self.log.info('Update activity with state %s', self.state)

    def track_delayed_task(self, task: RegularTask) -> None:
        self.delayed_tasks.append(task)

    def serve_forever_function(self, function: Callable) -> None:
        # Copied from serve_forever in errbot
        while True:
            try:
                if function():
                    break  # Truth-y exit from function means shutdown was requested
            except KeyboardInterrupt:
                log.info("Interrupt received, shutting down..")
                break
            except Exception:  # pylint: disable=broad-except
                log.exception("Exception occurred in serve_once:")

            log.info(
                "Reconnecting in %d seconds (%d attempted reconnections so far)",
                self._reconnection_delay,
                self._reconnection_count
            )
            try:
                self._delay_reconnect()
                self._reconnection_count += 1
            except KeyboardInterrupt:
                log.info("Interrupt received, shutting down..")
                break

        log.info("Trigger shutdown")
        self.shutdown()

    def supervisor_connection_check(self, timeout) -> None:
        if self.supervisor_connection.poll(timeout):
            message: InternalMessage = self.supervisor_connection.recv()
            if message.consume():
                if message.type == InternalMessageType.fake_message:
                    self.process_message(
                        Message(
                            body=message.message,
                            frm=self.build_identifier(message.source_user_technical_name),
                            to=self.bot_identifier,
                            extras={INTERNAL_BUS_LABEL: True}
                        )
                    )
                if message.type == InternalMessageType.cron_worker_command and self.bot.node.type == NodeType.cron_worker:
                    cron_message = CronWorkerCommandType.search(message.message)
                    if cron_message == CronWorkerCommandType.refresh:
                        self.bot.manager_env['cron'].update_record_list()

    def supervisor_connection_check_or_sleep(self, timeout) -> None:
        if self.supervisor_connection:
            self.supervisor_connection_check(timeout)
        else:
            time.sleep(timeout)

    def serve_worker(self) -> Any:
        init_result = self.serve_once_required()
        if init_result is not None:
            return init_result
        while True:
            with self.pool.connect() as conn:
                for change in self.manager_env['task'].subscribe_query().changes(include_types=True, include_initial=True).run(conn):
                    if change['type'] not in ['add', 'initial']:  # To avoid problems after remove
                        continue
                    task = fetch(change['new_val'])
                    self.task_execution(task, task_type=TaskType.regular)
        return True

    def serve_cron_worker(self) -> Any:
        init_result = self.serve_once_required()
        if init_result is not None:
            return init_result
        while True:
            for task in self.manager_env['cron'].next_tasks():
                self.task_execution(task, task_type=TaskType.cron)
            self.supervisor_connection_check_or_sleep(MAGIC_SLEEP_CONSTANT)
        return True

    def serve_system_analyze(self) -> Any:
        init_result = self.serve_once_required()
        if init_result is not None:
            return init_result
        services = self.manager_env['services']
        services.global_healthy_check(force_registration=True)
        while True:
            services.global_healthy_check()
            self.supervisor_connection_check_or_sleep(self.bot.bot_config.ANJI_HEALTHY_CHECK_TIMEOUT)
        return True

    @classmethod
    def get_plugin_class_from_method(cls, meth: Callable) -> Type:
        if hasattr(meth, '_anji_class_link'):
            return meth._anji_class_link
        return super().get_plugin_class_from_method(meth)

    def serve_once_required(self) -> None:
        """
        This function will be called before run serve_once for worker and cron-worker
        If function return something, this will be returned from serve_once function
        """
        pass

    def build_identifier(self, txtrep, message_extras=None):  # pylint: disable=arguments-differ
        if message_extras:
            return self.build_message_identifier(txtrep, message_extras)
        return super().build_identifier(txtrep)

    @abstractmethod
    def build_message_identifier(self, txtrep: str, message_extras: Dict) -> Identifier:
        pass

    def task_execution(self, task, task_type=TaskType.regular):
        if task.book(self.bot_name, self.uuid):
            if task_type == TaskType.regular:
                self.signals.fire(TaskStartedSignal(task))
            self.state = NodeState.working
            self.activity_report()
            self.log.info('Running task %s with name %s', task.id, task.name)
            task_exception = None
            task_result = None
            self.bot.manager_env['services'].update_record_list()
            try:
                task_result = task.run()
            # Due to code logic, disable check.
            # This code must catch any exception and log it
            # to chat
            # pylint: disable=broad-except
            except Exception as exception:
                _, _, traceback_ = sys.exc_info()
                task_exception = '{}: {}\n{}'.format(
                    exception.__class__.__name__,
                    str(exception),
                    "".join(traceback.format_tb(traceback_))
                )
                if task_type == TaskType.regular:
                    self.signals.fire(TaskFailedSignal(task, task_exception))
            task.done(
                task_exception=task_exception,
                task_result=task_result
            )
            if task_result and TaskType.regular == task_type:
                self.signals.fire(TaskDoneSignal(task, task_result))
            if task.after_task_command_list:
                self.signals.fire(FlowNextSignal(task))
            self.state = NodeState.free
            self.activity_report()

    def build_trafaret(self):
        extra_dict = T.Dict({})
        extra_dict.allow_extra('*')
        default_dict = T.Dict({
            'delay': T.Int(),
            'channel': T.String()
        })
        default_dict.make_optional('*')
        core_dict = T.Dict({
            'service_validation_delay': T.Int()
        })
        validation_dict = T.Dict({
            'default': default_dict,
            'core': core_dict,
            'flow': self.flow.build_flow_trafaret(),
            'report': ReportEngine.generate_trafater(),
        })
        validation_dict.make_optional('flow')
        return validation_dict

    def set_default_values(self, default_configuration):
        default_channel = None
        if self.bot_config.BACKEND == 'AnjiSlack' and default_configuration.get('channel', None):
            default_channel = default_configuration['channel']
        elif self.bot_config.BACKEND == 'AnjiTelegram' or not default_configuration.get('channel', None):
            # If telegram backend, ignore service settings and take default_channel from admin settings
            # And, if default don't exists, use bot admin users as a default channel
            default_channel = self.bot_config.BOT_ADMINS[0]
        self['default_channel'] = default_channel
        self['default_delay'] = default_configuration.get('delay', 2)

    @cmdfilter
    def global_security_filter(self, msg, cmd, args, _dry_run):  # pylint: disable=no-self-use
        return guard.validate_command(msg, cmd, args)

    def __getattr__(self, key: str) -> Any:
        return getattr(Model.shared, key)
