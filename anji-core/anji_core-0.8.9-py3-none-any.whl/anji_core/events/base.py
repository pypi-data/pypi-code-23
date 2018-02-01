from abc import abstractmethod
from datetime import datetime

from anji_orm import Model, StringField, ListField, EnumField, DatetimeField
import rethinkdb as R

from ..cartridges import AbstractCartridge, provide_confirmation_logic
from ..tasks import CronTask
from ..manager import BaseManager, ManagedModel
from ..types import EventState

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.8.9"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"


class AbstractEventCollector(ManagedModel):

    _table = 'event_collector'

    display_name = 'event collector'

    last_run_time = DatetimeField(description='Time of last run', service=True, default=None)

    @abstractmethod
    def collect_events(self):
        pass


class AbstractEventConsumer(ManagedModel):

    _table = 'event_consumer'

    display_name = 'event consumer'

    consume_event_types = []

    def consume_events(self):
        events = AbstractEvent.query(
            AbstractEvent.type.one_of(*self.consume_event_types) & (AbstractEvent.state == EventState.new)
        )
        self._consume_events(events)
        for event in events:
            event.consume()

    @abstractmethod
    def _consume_events(self, events):
        pass

    def __str__(self):
        return f"Event consumer {self.name}"


class AbstractEvent(Model):

    _table = 'event'

    type = StringField(description='Event type', secondary_index=True, definer=True)
    state = EnumField(EventState, description='Event state', secondary_index=True, service=True, default=EventState.new)
    post_timestamp = DatetimeField()

    def consume(self) -> None:
        self.state = EventState.consumed
        self.send()


class EventCollectorCronTask(CronTask):

    collector_technical_names = ListField(description='Event collector technical names', reconfigurable=True)

    def task_execute(self):
        event_collectors = AbstractEventCollector.query(AbstractEventCollector.technical_name.one_of(*self.collector_technical_names))
        current_time = datetime.now(R.make_timezone("00:00"))
        for event_collector in event_collectors:
            event_collector.collect_events()
            event_collector.last_run_time = current_time
            event_collector.send()

    def generate_name(self):
        return f"Event collect task with help of {','.join(self.collector_technical_names)}"


class EventConsumerCronTask(CronTask):

    consumer_technical_names = ListField(description='Event consumer names', reconfigurable=True)

    def task_execute(self):
        event_consumers = AbstractEventConsumer.query(AbstractEventConsumer.technical_name.one_of(*self.consumer_technical_names))
        for event_consumer in event_consumers:
            event_consumer.consume_events()

    def generate_name(self):
        return f"Consume events with help of {','.join(self.consumer_technical_names)}"


@provide_confirmation_logic
class EventCartridge(AbstractCartridge):

    __errdoc__ = 'Base cartridge to work with events'
    name = 'Core Events'
    technical_name = 'core_events'
    base_command_prefix = 'event'

    cron_tasks = {
        'collect_events': EventCollectorCronTask,
        'consume_events': EventConsumerCronTask
    }


class EventCollectorManager(BaseManager):

    controlled_model = AbstractEventCollector
    controlled_cartridge = EventCartridge
    submodel_use_model_table = True
    control_prefix = 'event_collector'

    @property
    def manager_short_name(self) -> str:
        return "event_collector"


class EventConsumerManager(BaseManager):

    controlled_model = AbstractEventConsumer
    controlled_cartridge = EventCartridge
    submodel_use_model_table = True
    control_prefix = 'event_consumer'

    @property
    def manager_short_name(self) -> str:
        return "event_consumer"
