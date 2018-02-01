from anji_orm import Model, ModelMetaclass, StringField, register

from ..types import SecurityModel


__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.8.11"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"


class CartridgeDefinitionException(Exception):

    pass


class CartridgeMetaclass(ModelMetaclass):

    cartridge_classes = []

    def __new__(mcs, name, bases, namespace, **kwargs):
        # Base cartridge validation
        if name != 'AbstractCartridge':
            for field in ('technical_name', 'name', '__errdoc__', 'base_command_prefix'):
                if namespace.get(field) == 'abstract':
                    raise CartridgeDefinitionException("You must redefine {} in cartridge class {}!".format(field, name))
        return super().__new__(mcs, name, bases, namespace, **kwargs)


class AbstractCartridge(Model, metaclass=CartridgeMetaclass):
    """
    Abstract Cartridge class
    Used to define custom cartridges
    """

    __errdoc__ = 'abstract'

    name = 'abstract'

    technical_name = 'abstract'
    base_command_prefix = 'abstract'
    _delayed_commands = {}

    cron_tasks = None
    default_command_security_policy = SecurityModel.free_for_anyone

    cartridge_indentity = StringField(definer=True, description='Технический идентификатор картриджа')

    _table = 'cartridges'

    def __init__(self, *args, id_=None, **kwargs):
        super().__init__(*args, id_=id_, **kwargs)
        self.cartridge_indentity = self.technical_name
        self.manager = None  # Will be filled on manager cartridge load

    def configuration_check(self):
        for field_name, field_data in self._fields.items():
            if not (field_data.optional or field_data.service) and getattr(self, field_name, None) is None:
                return False
        return True

    def desribe_service(self, cartridge_config):
        """
        Method, that used to add additional information to service description

        :param cartridge_config: service configuration for this cartridge
        """
        pass

    @classmethod
    def _inject_new_command(cls, function):
        function._anji_class_link = cls  # For errbot support
        if hasattr(function, '_anji_required_confirmation'):
            cls._delayed_commands[function.__name__] = function._anji_original_confirmation_function
        setattr(cls, function.__name__, function.__get__(None, cls))


class CartridgeRegistry:

    """
    Utility class to hold information about cartridge in one place
    """

    def __init__(self, bot):
        """
        Simple init method, store bot link (that actually link to AnjiBot object) for later usage.
        And create dict to store cartridge objects.
        """
        self.registry = {}
        self.bot = bot

    def get(self, key, default=None):
        """
        Utility method to get cartridge by technical name

        :param key: cartridge technical name
        :param default: custom default value for return, if required
        """
        return self.registry.get(key, default)

    def load_cartridges(self) -> None:
        """
        Method, that load all cartridges to Anji system
        :raise Exception: cartridge load problems
        """
        for cartridge_class in filter(lambda x: x != AbstractCartridge, register.tables_model_link.get(AbstractCartridge._table)):
            cartridge_object = AbstractCartridge.query(AbstractCartridge.cartridge_indentity == cartridge_class.technical_name)
            if not cartridge_object:
                cartridge_object = cartridge_class()
                cartridge_object.send()
            else:
                cartridge_object = cartridge_object[0]
            if self.registry.get(cartridge_object.technical_name, None):
                self.bot.log.info('Cartridge {} already loaded, skip'.format(cartridge_object.technical_name))
            else:
                self.registry[cartridge_object.technical_name] = cartridge_object
            self.bot.manager_env['cron'].process_cartridge(cartridge_object)

    def inject_commands(self):
        for cartridge_technical_name, cartridge_object in self.registry.items():
            self.bot.log.info('Load commands from cartirdge %s', cartridge_technical_name)
            self.bot.inject_commands_from(cartridge_object)

    def search_by_class(self, cartridge_class):
        return next(filter(lambda x: x.__class__ == cartridge_class, self.registry.values()), None)
