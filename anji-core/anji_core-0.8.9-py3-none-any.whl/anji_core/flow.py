import trafaret as T
from errbot import arg_botcmd

from .messages import Message
from .signals import FlowStartSignal

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.8.9"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"


class FlowStep(object):  # pylint: disable=too-few-public-methods

    def __init__(self, name, command, tags, must_be_enabled):
        self.name = name
        self.command = command
        self.tags = tags
        self.must_be_enabled = must_be_enabled

    def describe(self):
        base_dict = {
            'Command': self.command,
            'Run by default': 'No' if self.must_be_enabled else 'Yes'
        }
        if self.tags:
            base_dict['Tags'] = ", ".join(self.tags)
        return base_dict

    def __str__(self):
        return self.name


class FlowVariable(object):

    def __init__(self, name, description, type_, default_value, details):
        self.name = name
        self.description = description
        self.type = type_
        self.default_value = default_value
        self.details = details
        if self.type == 'int':
            self.default_value = int(default_value)

    def add_to_function(self, func, bot):
        params = {
            'help': self.description
        }

        if self.type == 'string':
            params['type'] = str
        elif self.type == 'int':
            params['type'] = int
        elif self.type == 'service':
            params['type'] = str
            params['choices'] = bot.manager_env['services'].get_all_service_names()
        elif self.type == 'selection':
            params['type'] = str
            params['choices'] = self.details
        param_name = self.name
        if self.default_value is not None:
            params['default'] = self.default_value
            param_name = '--' + param_name
            params['dest'] = self.name
        return arg_botcmd(
            param_name,
            **params
        )(func)

    def describe(self):
        base_dict = {
            'Type': self.type,
            'Description': self.description
        }
        return base_dict

    def __str__(self):
        return self.name


class Flow(object):

    def __init__(self, bot, name, description, technical_name):
        self.bot = bot
        self.name = name
        self.description = description
        self.technical_name = technical_name
        self.steps = []
        self.vars = []

    def add_step(self, step):
        self.steps.append(step)

    def add_var(self, flow_var):
        self.vars.append(flow_var)

    def describe(self):
        base_dict = {
            "Technical name": self.technical_name,
            'Description': self.description
        }
        return base_dict

    def inject_in_bot(self):

        class FlowCommandTemplate(object):

            def __init__(self, BOT_PREFIX, flow):
                self.BOT_PREFIX = BOT_PREFIX
                self.flow = flow

            def run_command(self, mess, **kwargs):
                flow_commands = []
                disabled_tags = kwargs.pop('disabled_tags')
                enabled_tags = kwargs.pop('enabled_tags')
                for flow_step in self.flow.steps:
                    # First, check for disable tag
                    if [tag for tag in flow_step.tags if tag in disabled_tags]:
                        continue
                    if flow_step.must_be_enabled and not [tag for tag in flow_step.tags if tag in enabled_tags]:
                        continue
                    flow_commands.append(flow_step.command.format(**kwargs))
                command = self.BOT_PREFIX + flow_commands.pop(0)
                command += ' --next-task-command ' + " ".join(['"{}"'.format(x) for x in flow_commands])
                message_link = Message.from_errbot_message(mess)
                command += f' --message-link "{message_link.id}"'
                self.flow.bot.signals.fire(FlowStartSignal(command, mess))

            def describe_command(self, _, short=None):
                with self.flow.bot.render as r:
                    r.title('Flow {} description'.format(self.flow.name))
                    if not short:
                        with r.detailed_list(title='Variables list') as lst:
                            for el in self.flow.vars:
                                lst.add(str(el), el.describe())
                    with r.detailed_list(title='Steps list') as lst:
                        for el in self.flow.steps:
                            lst.add(str(el), el.describe())

        # Prepare class to inject
        flow_class = FlowCommandTemplate
        flow_class.__name__ = self.name
        flow_class.__errdoc__ = self.description
        flow_class.name = self.name
        # Prepare run function to inject
        flow_class.run_command.__name__ = 'flow_{}_run'.format(self.technical_name)
        flow_class.run_command.__doc__ = self.description
        for flow_var in self.vars:
            flow_class.run_command = flow_var.add_to_function(flow_class.run_command, self.bot)
        flow_class.run_command = arg_botcmd(
            '--disable-tag',
            dest='disabled_tags',
            type=str,
            nargs='*',
            default=(),
            help='Tag that should be disabled. Has priority on enabled tags'
        )(flow_class.run_command)
        flow_class.run_command = arg_botcmd(
            '--enable-tag',
            dest='enabled_tags',
            type=str,
            nargs='*',
            default=(),
            help='Tag that should be enabled. Don\'t work on steps, that was disabled by tag disabling'
        )(flow_class.run_command)
        flow_class.run_command._anji_class_link = flow_class
        # Prepare describe function to inject
        flow_class.describe_command.__name__ = 'flow_{}_describe'.format(self.technical_name)
        flow_class.describe_command.__doc__ = 'Detailed flow {} description'.format(self.name)
        flow_class.describe_command = arg_botcmd(
            '--short',
            action='store_true',
            default=False,
            help='Show only steps'
        )(flow_class.describe_command)
        flow_class.describe_command._anji_class_link = flow_class
        # Inject prepared class to errbot commands
        flow_object = flow_class(self.bot.bot_config.BOT_PREFIX, self)
        self.bot.inject_commands_from(flow_object)

    def __str__(self):
        return self.name


class FlowManager(object):

    def __init__(self, bot):
        self.bot = bot
        self.flows = {}

    def load_flow(self, flow_configuration):
        flow = Flow(
            self.bot,
            flow_configuration['name'],
            flow_configuration['description'],
            flow_configuration['technical_name']
        )
        for step in flow_configuration['steps']:
            flow.add_step(
                FlowStep(
                    step['name'],
                    step['command'],
                    step.get('tags', []),
                    step.get('must_be_enabled', False)
                )
            )
        for flow_var in flow_configuration.get('vars', []):
            flow.add_var(
                FlowVariable(
                    flow_var['name'],
                    flow_var.get('description', ''),
                    flow_var['type'],
                    flow_var.get('default', None),
                    flow_var.get('details', None)
                )
            )
        self.flows[flow.technical_name] = flow
        flow.inject_in_bot()

    def get_flow_list(self):
        return list(self.flows.values())

    def get(self, name):
        flow = self.flows.get(name, None)
        if not flow:
            self.bot.render.send(f'Flow {name} does not exists')
        return flow

    def build_flow_trafaret(self):  # pylint: disable=no-self-use
        step_dict = T.Dict({
            'name': T.String(),
            'command': T.String(),
            'tags': T.List(T.String()),
            'must_be_enabled': T.Bool(),
        })
        step_dict.make_optional('tags', 'must_be_enabled')
        var_dict = T.Dict({
            'name': T.String(),
            'type': T.Enum('int', 'string', 'service', 'selection'),
            'description': T.String(),
            'default': T.String(),
            'details': T.List(T.String())
        })
        var_dict.make_optional('description', 'default', 'details')
        flow_dict = T.Dict({
            'name': T.String(),
            'description': T.String(),
            'technical_name': T.String(),
            'steps': T.List(step_dict),
            'vars': T.List(var_dict)
        })
        flow_dict.make_optional('vars')
        return T.List(flow_dict)
