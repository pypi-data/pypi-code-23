from typing import List, Optional
import importlib
import inspect
from abc import ABCMeta, abstractmethod

from anji_orm import Model, process_functions, StringField, register, QueryAst
from errbot import botcmd, Message, arg_botcmd
import rethinkdb as R

from ..types import Reaction, ManagerRecordModifyType
from ..cartridges import AbstractCartridge, require_confirmation_logic
from ..signals import MessageReactionSignal
from ..security import guard

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.8.9"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"


class ManagedModel(Model):

    name = StringField(description='Name', displayed=False)
    technical_name = StringField(description='Technical name', secondary_index=True, definer=True)

    model_subtype = None
    display_name = ''

    def __str__(self):
        return f"{self.display_name.title()} {self.name}"


class ManagerMetaclass(ABCMeta):

    manager_classes_list = []
    manager_env = {}

    def __new__(mcs, name, bases, namespace, **kwargs):
        result = super().__new__(mcs, name, bases, namespace, **kwargs)
        if not inspect.isabstract(result):
            mcs.manager_classes_list.append(result)
        return result

    @classmethod
    def init_managers(mcs, bot):
        for manager in mcs.manager_classes_list:
            if manager.is_required(bot):
                manager_object = manager(bot)
                mcs.manager_env[manager_object.manager_short_name] = manager_object

    @classmethod
    def load_managers(mcs):
        for manager in mcs.manager_env.values():
            manager.load()


class BaseManager(metaclass=ManagerMetaclass):

    controlled_model: ManagedModel = None
    controlled_cartridge: AbstractCartridge = None
    config_variable_name: str = ''
    control_prefix: str = ''
    submodel_use_model_table: bool = True
    autoload_enabled: bool = True
    remove_command_enabled: bool = True
    control_commands_enable: bool = True

    @classmethod
    def active_record_filter(cls) -> Optional[QueryAst]:
        return None

    @property
    @abstractmethod
    def manager_short_name(self) -> str:
        pass

    def __init__(self, bot):
        assert self.controlled_model
        assert self.controlled_cartridge
        assert issubclass(self.controlled_model, ManagedModel)
        assert issubclass(self.controlled_cartridge, AbstractCartridge)
        assert (self.config_variable_name or self.submodel_use_model_table) or not self.autoload_enabled
        assert self.control_prefix
        self.bot = bot
        self.r = R.table(self.controlled_model._table)
        self._models = {}
        self.model_subtypes = {}
        self.cartridge_instance = None

    @classmethod
    def create_record(cls, **kwargs):
        # Because controlled_model is link to model class
        # this is really callable one
        return cls.controlled_model(**kwargs)  # pylint: disable=not-callable

    @classmethod
    def is_required(cls, _bot) -> bool:
        return True

    def get_by_technical_name(self, technical_name: str, _user_technical_name: str) -> Optional[ManagedModel]:
        return self._models.get(technical_name, None)

    def record_list_fetcher(
            self,
            _user_technical_name: str,
            additional_filters: QueryAst = None) -> List[ManagedModel]:
        base_query = self.active_record_filter()
        if additional_filters:
            if base_query is not None:
                base_query &= additional_filters
            else:
                base_query = additional_filters
        if base_query is None:
            base_parsed_query = self.controlled_model.all()
        else:
            base_parsed_query = self.controlled_model.db_query(base_query)
        return self.controlled_model.execute(base_parsed_query)

    def update_record_list(self, with_push: bool = False) -> None:
        if with_push:
            for model in self._models.values():
                model.send()
        self._models = {}
        models = self.record_list_fetcher(self.bot.sudo)
        for model in models:
            self._models[model.technical_name] = model

    def remove_record(self, technical_name: str, message: Message) -> None:
        self.update_record_list()
        record = self.get_by_technical_name(technical_name, message.frm.person)
        if record:
            self.pre_modify_hook(ManagerRecordModifyType.remove, record)
            self.bot.signals.fire(
                MessageReactionSignal(
                    message,
                    Reaction.confirm,
                    alternative_text=f'{str(record)} remove successful'
                )
            )
            record.delete()
            self._models.pop(technical_name, None)
            self.post_modify_hook(ManagerRecordModifyType.remove, record)
        else:
            self.bot.signals.fire(
                MessageReactionSignal(
                    message,
                    Reaction.empty,
                    alternative_text='Nothing to remove'
                )
            )

    def add_record(self, record: ManagedModel) -> None:
        self._models[record.technical_name] = record

    def get_record_list(self, _user_technical_name) -> List[ManagedModel]:
        return self._models.values()

    def add_model_subtype(self, model_class: ManagedModel) -> None:
        self.model_subtypes[model_class.model_subtype] = model_class

    def pre_modify_hook(self, modify_type: ManagerRecordModifyType, record: ManagedModel) -> None:
        pass

    def post_modify_hook(self, modify_type: ManagerRecordModifyType, record: ManagedModel) -> None:
        pass

    def _extract_from_configuration_variable(self) -> None:
        for model_subtype_module_path, model_subtype_class_name in getattr(self.bot.bot_config, self.config_variable_name):
            model_subtype_module = importlib.import_module(model_subtype_module_path)
            self.add_model_subtype(getattr(model_subtype_module, model_subtype_class_name))

    def _extract_from_table_metadata(self) -> None:
        for model_subtype_class in filter(lambda x: x != self.controlled_model, register.tables_model_link.get(self.controlled_model._table)):
            self.add_model_subtype(model_subtype_class)

    def load(self) -> None:
        if self.autoload_enabled:
            if self.submodel_use_model_table:
                self._extract_from_table_metadata()
            elif self.config_variable_name:
                self._extract_from_configuration_variable()
        if self.control_commands_enable:
            for model_subtype, model_subtype_class in self.model_subtypes.items():
                self.patch_cartridge_with_control_commands(
                    model_subtype_class,
                    model_subtype
                )
        if self.remove_command_enabled:
            self.patch_cartridge_with_remove_command()
        self.patch_cartridge_with_list_command()
        self.update_record_list()
        self.cartridge_instance = self.bot.cartridge_registry.search_by_class(self.controlled_cartridge)
        self.cartridge_instance.manager = self

    def patch_cartridge_with_list_command(self) -> None:
        manager = self

        def model_list_template(self, mess, _args):
            manager.update_record_list()
            record_list = manager.get_record_list(mess.frm.person)
            if record_list:
                for model_record in record_list:
                    with self.shared.render as r:
                        r.title(str(model_record))
                        r.reply_to(mess)
                        r.message_type(model_record.describe_status())
                        with r.field_list() as lst:
                            for key, value in model_record.to_describe_dict().items():
                                lst.add(key, value)
            else:
                self.shared.render.reply("Unfortunatly, list is empty!", mess)

        model_list_template.__name__ = f'{self.control_prefix}_list'
        model_list_template.__doc__ = f'Command to print list of {self.controlled_model.display_name}'
        model_list_template = botcmd(split_args_with=None)(model_list_template)
        self.controlled_cartridge._inject_new_command(model_list_template)

    def patch_cartridge_with_remove_command(self) -> None:
        manager = self

        def model_remove_template(_self, mess, technical_name=None):
            manager.update_record_list()
            manager.remove_record(technical_name, mess)

        model_remove_template.__name__ = f'{self.control_prefix}_remove'
        model_remove_template.__doc__ = f'Command to remove {self.controlled_model.display_name}'
        model_remove_template = arg_botcmd(
            'technical_name',
            type=self.controlled_model._fields.get('technical_name').param_type,
            help=f'Technical name {self.controlled_model.display_name}'
        )(
            require_confirmation_logic(model_remove_template)
        )
        guard.admin_only_command(model_remove_template)
        self.controlled_cartridge._inject_new_command(model_remove_template)

    def patch_cartridge_with_control_commands(
            self,
            model_class: Model,
            model_subtype: str) -> None:

        manager = self

        def model_add_template(self, mess: Message, technical_name: str = None, **kwargs):
            manager.update_record_list()
            model_record = manager.get_by_technical_name(technical_name, self.shared.bot.sudo)
            if model_record:
                self.shared.signals.fire(
                    MessageReactionSignal(
                        mess,
                        Reaction.problem,
                        alternative_text=(
                            f"Unfortunatly, {manager.controlled_model.display_name} with technical name {technical_name}"
                            " already exists, you can create same one"
                        )
                    )
                )
            else:
                new_model_record = model_class(technical_name=technical_name, **kwargs)
                manager.pre_modify_hook(ManagerRecordModifyType.create, new_model_record)
                new_model_record.send()
                manager.add_record(new_model_record)
                self.shared.signals.fire(
                    MessageReactionSignal(
                        mess,
                        Reaction.confirm,
                        alternative_text=f"{manager.controlled_model.display_name} {kwargs['name']} was added to list"
                    )
                )
                manager.post_modify_hook(ManagerRecordModifyType.create, new_model_record)

        def model_edit_template(self, mess: Message, technical_name: str = None, **kwargs):
            manager.update_record_list()
            model_record = manager.get_by_technical_name(technical_name, mess.frm.person)
            if model_record:
                if model_record.model_subtype != model_subtype:
                    self.shared.signals.fire(
                        MessageReactionSignal(
                            mess,
                            Reaction.problem,
                            alternative_text=(
                                f"You try configure {manager.controlled_model.display_name} with wrong command."
                                f" Please, use {manager.control_prefix} edit {model_subtype} {technical_name}"
                            )
                        )
                    )
                manager.pre_modify_hook(ManagerRecordModifyType.update, model_record)
                model_record.update(kwargs)
                self.shared.signals.fire(
                    MessageReactionSignal(
                        mess,
                        Reaction.confirm,
                        alternative_text=f"Configuration for {manager.controlled_model.display_name} changed successfuly."
                    )
                )
                manager.post_modify_hook(ManagerRecordModifyType.update, model_record)
            else:
                self.shared.signals.fire(
                    MessageReactionSignal(
                        mess,
                        Reaction.problem,
                        alternative_text='Em ... can you type name without errors, please?'
                    )
                )

        model_add_template.__name__ = f'{self.control_prefix}_add_{model_subtype}'
        model_add_template.__errdoc__ = f'Command to create new {self.controlled_model.display_name} with subtype {model_subtype}'
        model_edit_template.__name__ = f'{self.control_prefix}_edit_{model_subtype}'
        model_edit_template.__errdoc__ = f'Command to edit {self.controlled_model.display_name} with subtype {model_subtype}'
        model_add_template, model_edit_template = process_functions(
            model_class._fields,
            model_add_template,
            model_edit_template,
        )
        model_add_template = guard.admin_only_command(model_add_template)
        model_edit_template = guard.admin_only_command(model_edit_template)
        self.controlled_cartridge._inject_new_command(model_add_template)
        self.controlled_cartridge._inject_new_command(model_edit_template)
