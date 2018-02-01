from datetime import datetime, timedelta
import logging

from anji_orm import StringField, DatetimeField, IntField, EnumField
import rethinkdb as R

from .cartridges import AbstractCartridge, provide_configuration
from .tasks import CronTask, RegularTask
from .types import NodeType, TaskStatus, NodeState, MessageType
from .manager import ManagedModel, BaseManager

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.8.11"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"


log = logging.getLogger('anji.core.nodes')


class Node(ManagedModel):

    _table = 'nodes'

    type = EnumField(NodeType, description='Node type')
    state = EnumField(NodeState, description='Node state')
    hostname = StringField(description='Node server hostname')

    last_activity_timestamp = DatetimeField(description='Node last activity data')
    first_activity_timestamp = DatetimeField(description='Node first acvtivity data')

    def update_last_activity(self, state):
        self.state = state
        self.last_activity_timestamp = datetime.now(R.make_timezone("00:00"))
        self.send()

    def state_validation(self, validation_delay):
        if self.state != NodeState.lost:
            current_time = datetime.now(R.make_timezone("00:00"))
            if not self.last_activity_timestamp or (current_time - self.last_activity_timestamp) > timedelta(minutes=validation_delay):
                self.state = NodeState.lost
                self.send()

    def describe_status(self):
        if self.state in [NodeState.lost, NodeState.deactivated, NodeState.disabled]:
            return MessageType.error
        elif self.state in [NodeState.working]:
            return MessageType.info
        return MessageType.good

    def free_node_tasks(self):
        task_class = None
        if self.type == NodeType.worker:
            task_class = RegularTask
        elif self.type == NodeType.cron_worker:
            task_class = CronTask
        else:
            return
        tasks_to_free = task_class.query(
            (task_class.status == TaskStatus.in_progress) &
            (task_class.worker_uuid == self.id)
        )
        for task in tasks_to_free:
            log.info('Free task %s from losted workek %s', task.id, self.id)
            task.free()

    @classmethod
    def create_node_from_bot(cls, bot):
        node_name = bot.bot_name
        node_record = cls.query(Node.technical_name == node_name)
        if not node_record:
            node_record = cls()
        else:
            node_record = node_record[0]
            node_record.free_node_tasks()
        node_record.technical_name = node_name
        node_record.name = node_name
        node_record.first_activity_timestamp = datetime.now(R.make_timezone("00:00"))
        node_record.type = bot.type
        node_record.state = bot.state
        node_record.last_activity_timestamp = node_record.first_activity_timestamp
        node_record.hostname = bot.bot_config.ANJI_HOSTNAME
        node_record.send()
        return node_record


@provide_configuration
class NodesCartridge(AbstractCartridge):

    __errdoc__ = 'Core commands to control nodes'
    name = 'Core nodes commands'
    technical_name = 'core_nodes'
    base_command_prefix = 'node'

    nodes_validation_delay = IntField(description='Validation delay for nodes in minutes', reconfigurable=True)


class NodeManager(BaseManager):

    controlled_model = Node
    controlled_cartridge = NodesCartridge
    control_prefix = 'node'
    autoload_enabled = False
    remove_command_enabled = False
    control_commands_enable = False

    @property
    def manager_short_name(self) -> str:
        return "node"

    @classmethod
    def is_required(cls, bot) -> bool:
        return bot.node_type == NodeType.master

    def update_record_list(self, with_push=False):
        super().update_record_list(with_push=with_push)
        if self.cartridge_instance:
            for model in self._models.values():
                model.state_validation(self.cartridge_instance.nodes_validation_delay)
