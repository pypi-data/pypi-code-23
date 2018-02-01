import logging
import abc
import inspect

from ..types import RenderFeatures, Reaction, ServiceUnavailableType, MessageType

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.8.10"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"


_log = logging.getLogger(__name__)


class SignalRegister(object):

    def __init__(self):
        self._register = {}
        self._subscribable_signals = {}

    def register_signal(self, signal_cls):
        self._register[signal_cls.type] = signal_cls
        if signal_cls.is_subscribable:
            self._subscribable_signals[signal_cls.type] = signal_cls

    def get_subscribable_list(self):
        return self._subscribable_signals.keys()


signal_register = SignalRegister()


class SignalMetaclass(abc.ABCMeta):

    @property
    def type(cls):
        return cls._type

    @property
    def is_subscribable(cls):
        return cls._is_subscribable

    def __new__(mcs, name, bases, namespace, **kwargs):
        result = super().__new__(mcs, name, bases, namespace, **kwargs)
        if not inspect.isabstract(result):
            signal_register.register_signal(result)
        return result


class AbstractSignal(metaclass=SignalMetaclass):

    _is_subscribable = False

    @abc.abstractmethod
    def process(self, bot, render):
        pass

    @property
    def type(self):
        return self._type  # pylint: disable=no-member

    @property
    def is_subscribable(self):
        return self._is_subscribable

    def build_subscribe_notify_message(self, _bot):  # pylint: disable=no-self-use
        return ""


class MessageReactionSignal(AbstractSignal):

    _type = "message_reaction"

    def __init__(self, message, reaction, remove_reaction=False, alternative_text=False):
        self.message = message
        self.reaction = reaction
        self.remove_reaction = remove_reaction
        self.alternative_text = alternative_text

    def process(self, bot, render):
        if render.is_support(RenderFeatures.reaction):
            if self.remove_reaction:
                render.remove_reaction(self.message, self.reaction)
            else:
                render.add_reaction(self.message, self.reaction)
        else:
            render.reply(self.alternative_text, self.message)


class MessageResponseSignal(AbstractSignal):

    _type = "message_response"

    def __init__(self, message, response):
        self.message = message
        self.response = response

    def process(self, bot, render):
        render.reply(self.response, self.message)


class TaskCreatedSignal(AbstractSignal):

    _type = "task_create"

    def __init__(self, task):
        self.task = task

    def process(self, bot, render):
        message_template = 'Task {} was queued'
        if self.task.predicted_execution_time:
            message_template += ', estimed execution time {}'
        else:
            message_template += '.'
        if self.task.message_link:
            task_message = self.task.message_link.to_errbot_message()
            if render.is_support(RenderFeatures.reaction):
                render.add_reaction(task_message, Reaction.accepted)
            else:
                render.reply(message_template.format(self.task.name, self.task.predicted_execution_time), task_message)
        else:
            render.send(message_template.format(self.task.name, self.task.predicted_execution_time))


class TaskStartedSignal(AbstractSignal):

    _type = "task_started"

    def __init__(self, task):
        self.task = task

    def process(self, bot, render):
        if self.task.message_link and render.is_support(RenderFeatures.reaction):
            task_message = self.task.message_link.to_errbot_message()
            render.remove_reaction(task_message, Reaction.processing_next)
            render.add_reaction(task_message, Reaction.processing)


class TaskDoneSignal(AbstractSignal):

    _type = "task_done"

    def __init__(self, task, task_result):
        self.task = task
        self.task_result = task_result

    def process(self, bot, render):
        if self.task.message_link:
            self.task_result = dict(**self.task_result)
            task_message = self.task.message_link.to_errbot_message()
            self.task_result['in_reply_to'] = task_message
            render.auto_task_result(**self.task_result)
            if not self.task.after_task_command_list:
                if render.is_support(RenderFeatures.reaction):
                    render.add_reaction(task_message, Reaction.confirm)
                    render.remove_reaction(task_message, Reaction.processing)
            else:
                if render.is_support(RenderFeatures.reaction):
                    render.add_reaction(task_message, Reaction.processing_next)
                else:
                    render.reply(f"Soon command {self.task.after_task_command_list[0]} will be executed", task_message)
        else:
            render.auto_task_result(**self.task_result)


class TaskFailedSignal(AbstractSignal):

    _type = "task_failed"

    def __init__(self, task, task_exception):
        self.task = task
        self.task_exception = task_exception

    def process(self, bot, render):
        errbot_message = None
        if self.task.message_link:
            errbot_message = self.task.message_link.to_errbot_message()
            render.add_reaction(errbot_message, Reaction.problem)
            render.remove_reaction(errbot_message, Reaction.processing)
        with render as r:
            r.title(f'Error on task {self.task.name} execution')
            r.message_type(MessageType.error)
            r.traceback(self.task_exception)
            if errbot_message:
                r.reply_to(errbot_message)


class FlowNextSignal(AbstractSignal):

    _type = "flow_next"

    def __init__(self, task):
        self.task = task

    def process(self, bot, render):
        base_command = bot.bot_config.BOT_PREFIX + self.task.after_task_command_list.pop(0)  # pylint: disable=no-member
        # Build next command list
        if self.task.after_task_command_list:
            next_commands = self.task.after_task_command_list
            next_commands = " ".join(['"{}"'.format(x) for x in next_commands])
            base_command += ' --next-task-command ' + next_commands
        # Build prev_task_uuids
        prev_task_uuids = self.task.before_task_uuid_list
        if prev_task_uuids is None:
            prev_task_uuids = []
        prev_task_uuids.append(self.task.id)
        prev_task_uuids = " ".join(['"{}"'.format(x) for x in prev_task_uuids])
        base_command += ' --prev-task-uuid ' + prev_task_uuids
        if self.task.message_link:
            base_command += f' --message-link "{self.task.message_link.id}"'
        bot.internal_bus.post_fake_message(
            base_command,
            source_user_technical_name=self.task.message_link.frm
        )


class FlowStartSignal(AbstractSignal):

    _type = "flow_start"

    def __init__(self, command, message):
        self.command = command
        self.message = message

    def process(self, bot, render):
        bot.internal_bus.post_fake_message(
            self.command,
            self.message.frm.person
        )


class ServiceWillBeUnavailableSignal(AbstractSignal):

    _type = "service_will_be_unavailable"
    _is_subscribable = True

    def __init__(self, service_technical_name, unavailable_type, change_delay, task):
        self.service_technical_name = service_technical_name
        self.unavailable_type = unavailable_type
        self.change_delay = change_delay
        self.task = task

    def process(self, bot, render):
        pass

    def build_subscribe_notify_message(self, bot):
        service = bot.manager_env['services'].get_by_technical_name(self.service_technical_name, bot.sudo)
        if self.unavailable_type == ServiceUnavailableType.temporary:
            message = f"Service {service.name} will be temporary unavailable\n"
        elif self.unavailable_type == ServiceUnavailableType.taskwide:
            message = f"Service {service.name} will be unavailable in time of task {self.task.name} execution\n"
            if self.task.predicted_execution_time:
                message += f'Estimated task execution time (in seconds): {self.task.predicted_execution_time}\n'
        else:
            message = f"Service {service.name} will be unavailable some time. How much? Only kami-sama knows!\n"
        if self.change_delay == 0:
            message += "You have not chance to stop it, at least you know about thi"
        else:
            message += f"You have {self.change_delay} minut to stop! If you want it, execute {bot.bot_config.BOT_PREFIX}task cancel {self.task.technical_name} --force"
        return message


class SignalBus(object):  # pylint: disable=too-few-public-methods

    def __init__(self, bot):
        self.bot = bot
        self.render = bot.render

    def fire(self, signal):
        from ..users import User

        signal.process(self.bot, self.render)
        subscribers = User.query(User.signal_types.contains(signal.type))
        if subscribers:
            message = signal.build_subscribe_notify_message(self.bot)
            for subscribe in subscribers:
                self.bot.render.send(message, channel=subscribe.username)
