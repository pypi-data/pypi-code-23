from functools import wraps, partial
import itertools
import argparse
import abc
from typing import List, Callable

from errbot import arg_botcmd
import rethinkdb as R

from .regular import RegularTask
from ..messages import Message
from ..types import MessageType, Reaction
from ..signals import TaskCreatedSignal, AbstractSignalProducer, ServiceWillBeUnavailableSignal, MessageReactionSignal
from ..types import TaskStatus

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.8.9"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"


class AbstractIteratorArgument(abc.ABC):

    def __init__(self, sequence=10):
        self.sequence = sequence

    @abc.abstractmethod
    def __call__(self, bot, cartridge, kwargs, message):
        pass

    @abc.abstractmethod
    def wrap(self, func):
        pass


class ServiceIteratorArgument(AbstractIteratorArgument):

    def __init__(
            self,
            description='Services technical name',
            object_instead_cartridge_config=False,
            services_variable_name='services',
            sequence=100
    ):
        super().__init__(sequence=sequence)
        self.description = description
        self.object_instead_cartridge_config = object_instead_cartridge_config
        self.services_variable_name = services_variable_name

    def wrap(self, func):
        return arg_botcmd(self.services_variable_name, nargs='+', help=self.description)(func)

    def __call__(self, bot, cartridge, kwargs, message):
        bot.manager_env['services'].load()
        service_list = kwargs.pop(self.services_variable_name)
        result_list = []
        for service_name in service_list:
            service_object = bot.manager_env['services'].get_by_technical_name(service_name, message.frm.person)
            if service_object:
                service_object.load()
                base_dict = dict(
                    service_technical_name=service_name,
                    worker_hostname=service_object.hostname
                )
                if self.object_instead_cartridge_config:
                    base_dict['service_object'] = service_object
                    result_list.append(base_dict)
                else:
                    service_configuration = service_object.get_cartridge_configuration(cartridge.technical_name)
                    if service_configuration:
                        base_dict['service_configuration'] = service_configuration
                        result_list.append(base_dict)
        return result_list


class ParameterIteratorArgument(AbstractIteratorArgument):

    def __init__(self, param_name, param_type, single_param_name, param_dest=None, nargs='+', unpack_prehook=None, description='', sequence=10):
        super().__init__(sequence=sequence)
        self.param_name = param_name
        self.param_type = param_type
        self.single_param_name = single_param_name
        self.nargs = nargs
        self.param_dest = param_dest
        self.unpack_prehook = unpack_prehook
        self.description = description

    def wrap(self, func):
        base_dict = dict(
            nargs=self.nargs,
            type=self.param_type,
            help=self.description
        )
        if self.param_dest:
            base_dict['dest'] = self.param_dest
        return arg_botcmd(self.param_name, **base_dict)(func)

    def __call__(self, bot, cartridge, kwargs, message):
        if self.unpack_prehook:
            kwargs.update(self.unpack_prehook(self, kwargs))
        params_list = kwargs.pop(self.param_dest if self.param_dest else self.param_name)
        result_list = []
        for single_param in params_list:
            result_list.append({self.single_param_name: single_param})
        return result_list


class AbstractTaskSignalProducer(AbstractSignalProducer):

    @abc.abstractmethod
    def produce_condition(self, iterators):  # pylint: disable=W0221
        pass

    @abc.abstractmethod
    def produce(self, params, task, delay):  # pylint: disable=W0221
        pass


class ServiceTaskSignalProducer(AbstractTaskSignalProducer):

    def __init__(self, unavailable_type):
        self.unavailable_type = unavailable_type

    def produce_condition(self, iterators):
        return any(filter(lambda x: isinstance(x, ServiceIteratorArgument), iterators))

    def produce(self, params, task, delay):
        return ServiceWillBeUnavailableSignal(
            params['service_technical_name'],
            self.unavailable_type,
            delay,
            task
        )


class SimpleArgument(object):

    def __init__(self, name, arg_type, help=''):  # pylint: disable=redefined-builtin
        self.name = name
        self.arg_type = arg_type
        self.help = help

    def wrap(self, func):
        return arg_botcmd(self.name, type=self.arg_type, help=self.help)(func)


def _base_task_decoration(func):
    """
    Task decorators for base anji task logic
    """
    func = arg_botcmd('--delay', type=int, default=-1, help='Delay in minutes before task execution')(func)
    func = arg_botcmd('--message-link', type=str, dest='external_message_link', help=argparse.SUPPRESS)(func)
    func = arg_botcmd('--prev-task-uuid', dest='prev_task_uuids', type=str, nargs='*', default=(), help=argparse.SUPPRESS)(func)
    func = arg_botcmd('--next-task-command', dest='next_task_commands', type=str, nargs='*', default=(), help=argparse.SUPPRESS)(func)
    return func


class TaskExecutionMode(object):  # pylint: disable=too-few-public-methods

    normal = 'normal'
    detailed = 'detailed'
    last_result = 'last_result'


def _statistic_task_decoration(func):
    """
    Task decorators for statistic analyze
    """
    func = arg_botcmd(
        '--detailed',
        action='store_const',
        dest='_task_mode',
        const=TaskExecutionMode.detailed,
        default=TaskExecutionMode.normal,
        help='Just print task stat'
    )(func)
    func = arg_botcmd(
        '--last-result',
        action='store_const',
        dest='_task_mode',
        const=TaskExecutionMode.last_result,
        default=TaskExecutionMode.normal,
        help='Just print last execution result'
    )(func)
    return func


def anji_delayed_task(  # pylint: disable=too-many-statements
        func: Callable = None,
        iterators: List[AbstractIteratorArgument] = None,
        producers: List[AbstractTaskSignalProducer] = None,
        arguments: List[SimpleArgument] = None,
        enable_statistic: bool = True) -> Callable:

    if func is None:
        return partial(
            anji_delayed_task,
            iterators=iterators,
            producers=producers,
            arguments=arguments,
            enable_statistic=enable_statistic
        )

    @wraps(func)
    def wrapped_func(  # pylint: disable=too-many-locals,too-many-branches,too-many-statements
            self,
            mess,
            delay=None,
            external_message_link=None,
            prev_task_uuids=None,
            next_task_commands=None,
            worker_hostname='*',
            _task_mode=TaskExecutionMode.normal,
            **kwargs
    ):
        if iterators is not None:
            iterators.sort(key=lambda x: x.sequence, reverse=True)
            command_arguments = itertools.product(*[iterator(self.shared.bot, self, kwargs, mess) for iterator in iterators])
        else:
            command_arguments = [{}]
        if producers is not None:
            enabled_producers = [x for x in producers if x.produce_condition(iterators)]
        else:
            enabled_producers = tuple()
        task_processes = False
        for command_argument in command_arguments:
            task_processes = True
            iterators_kwargs = {}
            for argument_dict in command_argument:
                iterators_kwargs.update(argument_dict)
            worker_hostname = iterators_kwargs.pop('worker_hostname', worker_hostname)
            if delay == -1:
                delay = self.shared.bot['default_delay']
            task_params = dict(**kwargs, **iterators_kwargs)
            task: RegularTask = func(self, mess, **task_params)
            if task is None:  # If nothing returned, just ignore it
                return
            before_task_uuid_list = prev_task_uuids if prev_task_uuids else []
            after_task_command_list = task.after_task_command_list
            before_task_uuid_list.extend(task.before_task_uuid_list)
            after_task_command_list.extend(next_task_commands)
            if external_message_link:
                message_link = external_message_link
            else:
                message_link = Message.from_errbot_message(mess).id
            task.set_delay(delay)
            task.worker_hostname = worker_hostname
            task.before_task_uuid_list = before_task_uuid_list
            task.after_task_command_list = after_task_command_list
            task.message_link = message_link
            if _task_mode == TaskExecutionMode.normal:
                task.predicted_execution_time = task.root_mean_square()
                task.send()
                self.shared.signals.fire(TaskCreatedSignal(task))
                if enabled_producers:
                    for producer in enabled_producers:
                        signal = producer.produce(task_params, task, delay)
                        self.shared.signals.fire(signal)
            elif _task_mode == TaskExecutionMode.last_result:
                search_query = task.build_similarity_query() & (RegularTask.status == TaskStatus.done)
                task_dict = task.execute(
                    task.db_query(search_query).order_by(R.desc('complete_timestamp')).limit(1),
                    without_fetch=True
                )
                if task_dict:
                    result = task_dict[0]['result']
                    result['title'] = f"Last {task.name} execution result"
                    self.shared.render.auto_task_result(
                        created_timestamp=task_dict[0]['created_timestamp'],
                        complete_timestamp=task_dict[0]['complete_timestamp'],
                        in_reply_to=mess,
                        **result
                    )
                else:
                    self.shared.signals.fire(
                        MessageReactionSignal(
                            mess,
                            Reaction.empty,
                            alternative_text="Unfortunately, there is no execution result for this task"
                        )
                    )
            elif _task_mode == TaskExecutionMode.detailed:
                search_query = task.build_similarity_query() & (RegularTask.status == TaskStatus.done)
                task_dicts = task.query(search_query, without_fetch=True)
                if task_dicts:
                    min_time = max_time = task_dicts[0]['execution_time']
                    average_time = 0
                    corrupted_done_task_count = 0
                    for task_dict in task_dicts:
                        if task_dict.get('execution_time'):
                            delta = task_dict.get('execution_time')
                            min_time = min(min_time, delta)
                            max_time = max(max_time, delta)
                            average_time += delta
                        else:
                            corrupted_done_task_count += 1
                    average_time /= len(task_dicts) - corrupted_done_task_count
                    with self.shared.render as r:
                        r.message_type(MessageType.info)
                        r.reply_to(mess)
                        r.title(f'Statistic for command "{task.name}"')
                        with r.field_list() as lst:
                            lst.add('Run count', str(len(task_dicts)))
                            lst.add('Average execution time (in seconds)', str(average_time))
                            lst.add('Max execution time (in seconds)', str(max_time))
                            lst.add('Min execution time (in seconds)', str(min_time))
                            lst.add('Count of damaged record', str(corrupted_done_task_count))
                else:
                    self.shared.signals.fire(
                        MessageReactionSignal(
                            mess,
                            Reaction.empty,
                            alternative_text='There is no statistic about this command'
                        )
                    )
        if not task_processes:
            if external_message_link:
                mess = Message.get(external_message_link).to_errbot_message()
            self.shared.signals.fire(
                MessageReactionSignal(
                    mess,
                    Reaction.blocked,
                    alternative_text="You command was blocked by security rules"
                )
            )

    # Apply arguments
    if arguments is not None:
        for argument in arguments:
            wrapped_func = argument.wrap(wrapped_func)

    # Apply iterators
    if iterators is not None:
        for iterator in iterators:
            wrapped_func = iterator.wrap(wrapped_func)

    # Apply base decorators
    wrapped_func = _base_task_decoration(wrapped_func)
    if enable_statistic:
        wrapped_func = _statistic_task_decoration(wrapped_func)

    return wrapped_func


def service_with_cartridge_interaction_task(func):
    return anji_delayed_task(
        iterators=[
            ServiceIteratorArgument()
        ]
    )(func)


def service_interaction_task(func):
    return anji_delayed_task(
        iterators=[
            ServiceIteratorArgument(object_instead_cartridge_config=True)
        ]
    )(func)
