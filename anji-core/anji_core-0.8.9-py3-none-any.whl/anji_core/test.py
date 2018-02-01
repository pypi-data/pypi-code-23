import time
import random
import uuid

from anji_orm import StringField, IntField
from errbot import botcmd, arg_botcmd

from .tasks import RegularTask, anji_delayed_task, TestTask, SimpleArgument
from .cartridges import AbstractCartridge
from .events import AbstractEvent, AbstractEventCollector, AbstractEventConsumer

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.8.9"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"


class TestEvent(AbstractEvent):

    message = StringField(description='Simple message')


class TestEventCollector(AbstractEventCollector):

    model_subtype = 'test'

    def collect_events(self):
        for _ in range(0, 10):
            TestEvent(message=f'New message with uuid {uuid.uuid4()}', type='test_event').send()


class TestEventConsumer(AbstractEventConsumer):

    model_subtype = 'test'
    consume_event_types = ['test_event']

    def _consume_events(self, events):
        with self.shared.render as r:
            with r.bulleted_list() as lst:
                for event in events:
                    lst.add(event.message)


class TestErrorTask(RegularTask):

    task_delay = IntField(description='Task sleep time', definer=True)

    def task_execute(self):
        time.sleep(self.task_delay)
        raise Exception('Exception!')

    def generate_name(self):
        return "Test task with exception"


class TestCartridge(AbstractCartridge):

    __errdoc__ = 'Test class for basic logic check'
    name = 'Test Commands'
    technical_name = 'base_test'
    base_command_prefix = 'test'

    @anji_delayed_task(
        arguments=[
            SimpleArgument('task_delay', int, 'Task delay before finish')
        ]
    )
    def test_error(self, _, task_delay=None):  # pylint: disable=no-self-use
        """
        Command that used for testing delayed task with exception instead of result
        """
        return TestErrorTask(task_delay=task_delay)

    @anji_delayed_task
    def test_chain(self, _):  # pylint: disable=no-self-use
        return TestTask(task_delay=6, after_task_command_list=['test normal 6', 'test normal 6'])

    @botcmd
    def test_echo(self, _mess, _args):  # pylint: disable=no-self-use
        return "Echo worked!"

    @anji_delayed_task(
        arguments=[
            SimpleArgument('task_delay', int, 'Task delay before finish')
        ]
    )
    def test_normal(self, _, task_delay=None):  # pylint: disable=no-self-use
        """
        Command that used for testing delayed task with normal result
        """
        return TestTask(task_delay=task_delay)

    @arg_botcmd('count', type=int)
    @arg_botcmd('--task-delay', dest='task_delay', type=int, default=6)
    @arg_botcmd('--delay', dest='delay', type=int, default=0)
    @arg_botcmd('--mixed', default=False, action='store_true')
    def test_task(self, _, count=None, delay=None, mixed=None, task_delay=None):
        for _ in range(0, count):
            if mixed and random.random() > 0.5:
                task = TestErrorTask(task_delay=task_delay)
            else:
                task = TestTask(task_delay=task_delay)
            task.set_delay(delay)
            task.send()
