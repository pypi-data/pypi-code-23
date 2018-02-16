import re
from typing import Tuple, List, Type, Set, Callable, Union, Any
from logging import getLogger, Logger
import socket
import camel_case_switcher.dict_processor
import copy

from http_server_base import BasicResponder, HandlerController
from http_server_base.empty_request_handler import Empty_RequestHandler
from http_server_base.health_check_request_handler import HealthCheck_RequestHandler
from http_server_base.tools.config_loader import ConfigLoader

from tornado.httpserver import HTTPServer
from tornado.web import Application, RequestHandler
from tornado.ioloop import IOLoop

class _Protocols:
    __http = 'http'
    __https = 'https'
    
    http = __http
    HTTP = __http
    
    https = __https
    HTTPS = __https

class ApplicationBase(Application):
    """
    ApplicationBase class.
    
    The following attributes can be overrided:
    :attribute logger_name
    :attribute handlers
    List of handlers those are passed to the to tornado.web.Application class during the initialisation.
    If untouched (None or missing), default handlers will be used.
    """
    name: str
    logger_name:str = 'http_server'
    handlers:List[Tuple[str, Type[RequestHandler]]]
    handler_controllers: List[HandlerController]
    hosts:List[str]
    responder_class: BasicResponder = BasicResponder
    
    default_handlers = \
    [
        (r"^/?$", Empty_RequestHandler, dict(redirect_page='/static/index.html')),
        (r"^/healthcheck(|(/.*))$", HealthCheck_RequestHandler),
    ]
    
    __logger: Logger = None
    __server: HTTPServer = None
    
    __self_addr: str = None
    __listen_port: int = None
    __protocol:str = None
    
    #region Initialization
    def __init__(self, *,
            name:str = None,
            config_name:str='main', config_prefix='HTTP', config_priority=False,
            hosts:List[str]=None,
            handler_controllers:List[HandlerController]=None,
            **settings):
        """
        Initializes a new instance of tornado.web.Application and prepares tornado.httpserver.HTTPServer to be run.
        :param name:
        str. Name of server used in serveral log records.
        
        :param config_name:
        Name of config in the ConfigLoader class, where the settings are loaded from.
        By default, settings are loaded from the main config.
        :param config_prefix:
        Prefix part of the config path to the server's settings. Path keys are '/'-separated.
        Note that due to the implementation's restrictions, server settings could not be in the top-level of the config.
        :param config_priority:
        By default, arguments passed directly to the initializer, have more priority.
        By setting config_config_priority=True, you are prioritising config over the keyword arguments.
        
        :param hosts
        List of str.
        :param handler_controllers
        List of HandlerController initialized objects
        
        :param settings:
        Keyword arguments. Partially parsed by ApplicationBase, partially passed to the tornado.web.Application
        All ApplicationBase optional parameters are listed below.
        Note that all CamelCase parameters loaded from the config would be morphed into the underscore_style,
            so `selfAddress` and `ListenPort` are completely legal.
        
        :param static_files:
        Same as `static_path`.
        If both are presented, `static_path` has priority.
        
        :param self_address:
        str. Hardcoded server uri. Used only for the info message about server start and several responses based on the `self_address` property.
        Should contain protocol.
        :param listen_ip:
        str. Used only if `self_address` is not set up for the `self_address` calculation.
        If missing as well, server will try to self-discover.
        The resulting self_address will have protocol - http or https, ip-address and, if custom, a port.
        :param ip:
        Same as `listen_ip`.
        If both are presented, `listen_ip` has priority.
        :param listen_port:
        int value of port, which server is uses to listen requests.
        By default 80 or 443 port is used - according to the SSL configuration
        :param port:
        Same as `listen_port`.
        If both are presented, `listen_port` has priority.
        
        :param SSL
        NOT IMPLEMENTED YET
        
        dict. Group of parameters required for SSL.
        Any of them can be passed directly as an argument as well.
        """
        
        # TODO: SSL
        # TODO: Hosts description
        # TODO: Handler Controllers description
        
        if (not name is None):
            self.name = name
        if (not hasattr(self, 'name') or self.name is None):
            self.name = type(self).__name__
        if (not handler_controllers is None):
            self.handler_controllers = handler_controllers
        if (not hasattr(self, 'handler_controllers') or self.handler_controllers is None):
            self.handler_controllers = list()
            
        if (not hosts is None):
            self.hosts = hosts
        if (not hasattr(self, 'hosts') or self.hosts is None):
            self.hosts = [ 'self' ]

        self.__logger = getLogger(self.logger_name)
        
        if ((not hasattr(self, 'handlers')) or (self.handlers is None)):
            self.handlers = ApplicationBase.default_handlers
            self.logger.debug(f"{self.name}: Using default handlers")
        else:
            self.logger.debug(f"{self.name}: List of handlers: {self.handlers}")
        
        _settings = camel_case_switcher.dict_processor.dict_keys_camel_case_to_underscope(ConfigLoader.get_from_config(config_prefix, config_name=config_name, default=lambda: dict()))
        if (config_priority):
            settings_deep_copy = copy.deepcopy(settings)
            settings_deep_copy.update(_settings)
            _settings = settings_deep_copy
        else:
            _settings.update(settings)
        
        if (_settings.get('static_files') and not _settings.get('static_path')):
            _settings['static_path'] = _settings['static_files']
        
        extra = self.initialize_host(_settings)
        super().__init__(handlers=self.handlers, **_settings)
        self.attach_controllers(_settings, **extra)
    
    def initialize_host(self, settings):
        _ssl = None
        # _ssl = _settings.get('SSL')
        if (_ssl):
            protocol = _Protocols.HTTPS
        else:
            protocol = _Protocols.HTTP
    
        listen_port = settings.get('listen_port') or settings.get('port')
        if (listen_port is None):
            if (protocol == _Protocols.HTTP):
                listen_port = 80
            elif (protocol == _Protocols.HTTPS):
                listen_port = 443
            listen_port_part = ""
        else:
            listen_port_part = f":{listen_port}"
    
        self.__listen_port = listen_port
        
        return dict(protocol=protocol, listen_port_part=listen_port_part)
    
    def attach_controllers(self, settings:dict, *, protocol, listen_port_part, **kwargs):
        for host in self.hosts:
            host_address = settings.get(f'{host}_address')
            host_pattern = None
            
            if (host_address):
                listen_address = None
            else:
                if (hasattr(self, f'get_{host}_host') and callable(getattr(self, f'get_{host}_host'))):
                    _host = getattr(self, f'get_{host}_host')()
                    if (isinstance(_host, tuple) and len(_host) == 2):
                        listen_address, host_pattern = _host
                    else:
                        listen_address = result
                else:
                    listen_address = \
                        settings.get('listen_address') \
                        or settings.get('listen_ip') \
                        or settings.get('ip') \
                        or socket.gethostbyname(socket.gethostname()) \
                    ;
                host_address = f"{protocol}://{listen_address}{listen_port_part}"
        
            setattr(self, f'_{type(self).__name__}__{host}_addr', host_address)
            if (not hasattr(self, f'{host}_address')):
                setattr(type(self), f'{host}_address', host_address)
            
            if (host_pattern is None):
                if (listen_address is None):
                    host_pattern = '.*'
                else:
                    host_pattern = re.escape(listen_address)

            host_handlers = list()
            for _handler_controller in self.handler_controllers:
                getter = getattr(_handler_controller, f'get_{host}_handlers')
                _handlers = getter()
                host_handlers += _handlers

            self.add_handlers(re.compile(host_pattern, re.IGNORECASE), host_handlers)
    def initialize_settings(self):
        pass
    #endregion
    
    @property
    def logger(self) -> Logger:
        return self.__logger
    
    #region Discovery
    @classmethod
    def __self_discover_generator(cls):
        names = \
        [
            'localhost',
            socket.getfqdn(),
        ]
        for name in names:
            try:
                for _value in cls.__self_discover_generator_per_interface(name=name):
                    yield _value
            except socket.herror:
                continue
        
        local_addr = cls.get_public_ip()
        try:
            for _value in cls.__self_discover_generator_per_interface(addr=local_addr):
                yield _value
        except socket.herror:
            pass
    
    @classmethod
    def __self_discover_generator_per_interface(cls, name=None, addr=None):
        if (addr is None):
            assert not name is None, "Either name or addr is required"
            addr = socket.gethostbyname(name)
        yield addr
        _name, _alias_list, _address_list = socket.gethostbyaddr(addr)
        yield _name
        for _alias in _alias_list:
            yield _alias
        for addr in _address_list:
            yield addr
            yield socket.getfqdn(_name)
            yield socket.gethostbyname(_name)
    
    @classmethod
    def get_public_ip(cls):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            local_addr = s.getsockname()[0]
            s.close()
            return local_addr
        except OSError:
            return socket.gethostbyname(socket.gethostname())
            
    @classmethod
    def self_discover(cls) -> Set[str]:
        """
        Server will try to do some self-discovery job.
        Not used in the distributed version.
        
        :return:
        The result is non-sorted set of unique items which could be associated with the local host.
        Usually it looks like:
        { '127.0.0.1', '127.0.1.1', 'localhost', 'MyComputer', '192.168.0.14' }
        """
        
        return set(cls.__self_discover_generator())

    @property
    def listen_port(self) -> int:
        return self.__listen_port
    #endregion
    
    def get_self_host(self) -> Tuple[str, str]:
        return self.get_public_ip(), '.*'
    
    @property
    def self_address(self) -> str:
        """
        Returns the self_address value, which was calculated during the initialisation process.
        :return:
        Returns self_address value.
        """
        
        return getattr(self, f"_{type(self).__name__}__self_addr")
    
    #region Start server
    def run(self, blocking=True):
        """
        Runs the server on the port specified earlier.
        Server blocks the IO.
        """
        
        self.logger.info(f"{self.name}: Starting HTTP service...")

        self.__server = HTTPServer(self)
        self.__server.listen(self.__listen_port)
        # self.__server.bind(self.__listen_port)
        # self.__server.start(0)
        self.logger.info(f"{self.name}: Service started")
        for host in self.hosts:
            host_address = getattr(self, f'{host}_address')
            self.logger.info(f"{self.name}: Listnening on the {host} host: {host_address}")
        
        if (blocking):
            IOLoop.current().start()
    
    @classmethod
    def simple_start_decorator_with_settings(cls, **settings):
        """
        Decorator creator with settings.
        
        Resulting decorator turns function into the simple server start method.
        It initializes logging and ConfigLoader in the soft-mode,
        than initializes the class instance, runs this function and starts the server.

        :param settings:
        Settings used for the server initialization
        :return:
        The decorator to the function to start the server
        
        Example usage:
        @ApplicationBase.simple_start_decorator_with_settings(port=8123, static_files='static', debug=True)
        def my_func(server_app):
            server_app.logger.debug(f"{self.name}: I am going to be run")
        
        """
        return lambda func: cls.simple_start_decorator(func, **settings)
        
    @classmethod
    def simple_start_decorator(cls, pre_run_func:Callable[['ApplicationBase', Any], None], **settings) -> Callable[[Any], None]:
        """
        Decorator that turn function into the simple server start method.
        It initializes logging and ConfigLoader in the soft-mode,
        than initializes the class instance, runs this function and starts the server.
        
        :param pre_run_func:
        Function to be run after the server initialization but before actual start.
        Any arguments are allowed.
        :param settings:
        Settings used for the server initialization
        :return:
        The function to start the server
        """
        
        def wrapper(*args, **kwargs):
            cls.simple_start_server(lambda server_application: pre_run_func(server_application, *args, **kwargs), **settings)
        return wrapper
    
    @classmethod
    def __simple_start_prepare(cls):
        from logging import getLogger
        from http_server_base.tools import setup_logging
    
        # Configure logger
        setup_logging()
        logger = getLogger(cls.logger_name)
        logger.info("Logger started")
        ConfigLoader.load_configs(soft_mode=True)
        
        return logger

    @classmethod
    def __simple_start_func(cls, pre_run_func:Union[Callable[['ApplicationBase'], None], None], **settings) -> Tuple[Union['ApplicationBase', None], Union[Exception, None]]:
        """
        If any expected error occurs, returns the instance of initialized class (if any) and the exception
        
        :param pre_run_func:
        Function to be run after the server initialization but before actual start.
        Must take only one argument - the server instance.
        :param settings:
        Settings used for the server initialization
        :return:
        Tuple:
         - instance of initialized object (if any)
         - exception info
        """
        
        server_application:ApplicationBase = cls(**settings)
        if (callable(pre_run_func)):
            pre_run_func(server_application)
    
        try:
            server_application.run()
        except KeyboardInterrupt:
            server_application.logger.info("Keyboard interrupt. Exiting now.")
        except PermissionError as e:
            return server_application, e
        
        return None, None

    @classmethod
    def simple_start_server(cls, pre_run_func:Union[Callable[['ApplicationBase'], None], None] = None, **settings):
        """
        Initializes logging and ConfigLoader in the soft-mode,
        than initializes the class instance, runs this function and starts the server.

        :param pre_run_func:
        Function to be run after the server initialization but before actual start.
        Must take only one argument - the server instance.
        :param settings:
        Settings used for the server initialization
        :return:
        """
        
        logger = cls.__simple_start_prepare()
        
        try:
            server_application, exception = cls.__simple_start_func(pre_run_func, **settings)
            
            if (isinstance(exception, PermissionError)):
                server_application.logger.error("Permission error. Restarting server with the port of range 8xxx.")
                new_port = server_application.listen_port + 8000
                del server_application
                settings['listen_port'] = new_port
                logger.info(f"Restarting server on the port {new_port}.")
                cls.__simple_start_func(pre_run_func, **settings)
                
                
        except Exception:
            logger.exception(msg="Unhandled exception while starting server:")
            raise
    #endregion