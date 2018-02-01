from functools import wraps
from datetime import datetime, timedelta

from anji_orm import process_functions
from errbot import arg_botcmd, botcmd

from ..types import MessageType, Reaction
from ..signals import MessageReactionSignal
from ..security import guard


class AdditionalFunctionalityException(Exception):
    pass


def required_configuration(function):
    @wraps(function)
    def wrapped_function(self, mess, args):
        self.load()
        if self.configuration_check():
            execution_result = function(self, mess, args)
            if execution_result:
                if isinstance(execution_result, str):
                    yield execution_result
                else:
                    for result in execution_result:
                        yield result
        else:
            yield f"Хм ... а вот картридж {self.technical_name} не очень то настроен, пожалуйста, запустите {self.base_command_prefix} init, пожалуйста"

    for attr_name in dir(function):
        if attr_name.startswith('_err'):
            setattr(wrapped_function, attr_name, getattr(function, attr_name))
    return wrapped_function


def provide_configuration(cls):

    def configuration_function(self, mess, **kwargs):
        self.update(kwargs)
        self.shared.signals.fire(
            MessageReactionSignal(
                mess,
                Reaction.confirm,
                alternative_text="Настройки успешно обновлены!"
            )
        )

    def init_function(self, mess, **kwargs):
        self.update(kwargs)
        self.shared.signals.fire(
            MessageReactionSignal(
                mess,
                Reaction.confirm,
                alternative_text="Настройки успешно установлены!"
            )
        )

    def info_function(self, mess, _):
        field_list = {}
        for field_name, field_describe in self._fields.items():
            if field_describe.service:
                continue
            field_list[field_describe.description] = getattr(self, field_name)
        with self.shared.render as r:
            r.message_type(MessageType.info)
            r.title(f'Настройки картриджа {self.name}')
            r.reply_to(mess)
            with r.field_list() as lst:
                for key, value in field_list.items():
                    lst.add(key, value)

    configuration_function.__name__ = f'{cls.base_command_prefix}_configure'
    configuration_function.__errdoc__ = f'Команда для настройки картриджа {cls.name}'
    init_function.__name__ = f'{cls.base_command_prefix}_init'
    init_function.__errdoc__ = f'Команда для базовой настройки картриджа {cls.name}'
    init_function, configuration_function = process_functions(
        cls._fields,
        init_function,
        configuration_function,
        definer_ignore=True
    )
    configuration_function = guard.admin_only_command(configuration_function)
    init_function = guard.admin_only_command(init_function)
    cls._inject_new_command(required_configuration(configuration_function))
    cls._inject_new_command(init_function)
    info_function.__name__ = f'{cls.base_command_prefix}_info'
    info_function.__errdoc__ = f'Команда для вывода информации про картридж {cls.name}'
    cls._inject_new_command(required_configuration(botcmd()(info_function)))
    cls._anji_provide_configuration = True
    return cls


def provide_service_configuration(cls):

    service_configuration = getattr(cls, 'service_configuration', None)
    if not service_configuration:
        raise AdditionalFunctionalityException('You can\'t use provide_service_configuration decorator without defining service_configuration dict in class')

    def configuration_function(self, mess, service_name=None, **kwargs):
        service = self.shared.bot.manager_env['services'].get_by_technical_name(service_name, mess.frm.person)
        if service:
            if not service.cartridges.get(self.technical_name):
                self.shared.render.send(
                    f"Service {service_name} not configured to use this cartridge, please init it instead"
                )
            service.apply_cartridge_configuration(self.technical_name, kwargs)
            self.shared.signals.fire(
                MessageReactionSignal(
                    mess,
                    Reaction.confirm,
                    alternative_text=f"Настройки сервиса {service_name} успешно обновлены!"
                )
            )
        else:
            self.shared.render.send(
                f"Well ... i can't find service {service_name}, what's wrong desu?"
            )

    def init_function(self, mess, service_name=None, **kwargs):
        service = self.shared.bot.manager_env['services'].get_by_technical_name(service_name, mess.frm.person)
        if service:
            if service.cartridges.get(self.technical_name):
                self.shared.render.send(
                    f"Service {service_name} already configured for this cartridge, please, use config command instead"
                )
            service.apply_cartridge_configuration(self.technical_name, kwargs)
            self.shared.signals.fire(
                MessageReactionSignal(
                    mess,
                    Reaction.confirm,
                    alternative_text=f"Настройки сервиса {service_name} успешно обновлены!"
                )
            )
        else:
            self.shared.render.send(
                f"Well ... i can't find service {service_name}, what's wrong desu?"
            )

    configuration_function.__name__ = f'{cls.base_command_prefix}_configure_service'
    configuration_function.__errdoc__ = f'Command to reconfigure service setting for cartridge {cls.name}'
    configuration_function = arg_botcmd('service_name', help='Target service')(configuration_function)

    init_function.__name__ = f'{cls.base_command_prefix}_init_service'
    init_function.__errdoc__ = f'Command to init service setting for cartridge {cls.name}'
    init_function = arg_botcmd('service_name', help='Target service')(init_function)
    init_function, configuration_function = process_functions(
        service_configuration,
        init_function,
        configuration_function,
        definer_ignore=True
    )
    configuration_function = guard.admin_only_command(configuration_function)
    init_function = guard.admin_only_command(init_function)
    cls._anji_provide_service_configuration = True
    cls._inject_new_command(configuration_function)
    cls._inject_new_command(init_function)
    return cls


def provide_confirmation_logic(cls):

    def confirm_function(self, mess, _):
        delayed_command_data = self._confirmation_dict.pop(str(mess.frm), None)
        if delayed_command_data:
            current_time = datetime.now()
            if current_time > delayed_command_data['confirmation_expire']:
                self.shared.signals.fire(
                    MessageReactionSignal(
                        mess,
                        Reaction.empty,
                        'Confirmation time expired, sempai!'
                    )
                )
            else:
                self._apply_delayed_commands(mess, delayed_command_data)

    def _apply_delayed_commands(self, mess, delayed_command_data):
        func = self._delayed_commands.get(delayed_command_data['type'], None)
        if func:
            func(
                self,
                mess,
                **delayed_command_data.get('kwargs', {})
            )

    def _build_delayed_command(self, chat_message, command_type, force=None, command_args=None, command_kwargs=None):
        if command_args is None:
            command_args = []
        if command_kwargs is None:
            command_kwargs = dict()
        delayed_command_data = {
            'type': command_type,
            'kwargs': command_kwargs,
            'confirmation_expire': datetime.now() + timedelta(seconds=self.shared.bot.bot_config.CONFIRM_DURATION)
        }
        if force:
            self._apply_delayed_commands(chat_message, delayed_command_data)
        else:
            self._confirmation_dict[str(chat_message.frm)] = delayed_command_data
            self.shared.render.send(
                "Для подтверждения команды введите {prefix}{base_command_prefix} confirm\nЭто будет актуально еще {confirm_duration} секунд".format(
                    base_command_prefix=self.base_command_prefix,
                    prefix=self.shared.bot.bot_config.BOT_PREFIX,
                    confirm_duration=self.shared.bot.bot_config.CONFIRM_DURATION
                )
            )

    confirm_function.__name__ = f'{cls.base_command_prefix}_confirm'
    confirm_function.__errdoc__ = f'Подтверждает последние действие пользователя с картриджем {cls.technical_name}'
    confirm_function = botcmd(split_args_with=None)(confirm_function)
    cls._confirmation_dict = dict()
    cls._inject_new_command(confirm_function)
    cls._inject_new_command(_apply_delayed_commands)
    cls._inject_new_command(_build_delayed_command)
    return cls


def require_confirmation_logic(function):
    if hasattr(function, '_err_command'):
        raise AttributeError("Function must be not initialized like errbot command!")
    function_name = function.__name__

    def wrapper(self, mess, force=None, **kwargs):
        self._build_delayed_command(
            mess,
            function_name,
            force=force,
            command_kwargs=kwargs
        )

    wrapper.__name__ = function_name
    wrapper.__doc__ = function.__doc__

    wrapper = arg_botcmd('--force', dest='force', default=False, help='Проведение удаление без подтверждения', action='store_true')(wrapper)

    wrapper._anji_required_confirmation = True
    wrapper._anji_original_confirmation_function = function

    return wrapper
