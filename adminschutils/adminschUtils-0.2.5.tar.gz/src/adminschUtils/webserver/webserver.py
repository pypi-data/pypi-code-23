"""
Webserver helper
"""
import asyncio
import logging
from typing import Dict, Tuple, Optional

from sanic import Sanic
from sanic.router import RouteExists
from sanic.config import LOGGING
from sanic.blueprints import Blueprint
from sanic_openapi import swagger_blueprint, openapi_blueprint
import recursive_dictionary_update

from ..config.Config import Config
from ..connections.base import create_connections


class Webserver(Sanic):
    """
    Webserver helper class
    """
    __instance = None

    def __new__(cls, *args, **kwargs):  # pylint: disable=unused-argument
        if Webserver.__instance is None:
            Webserver.__instance = Sanic.__new__(cls)
        return Webserver.__instance

    def __init__(self, config_dir: str = None, testing: bool = False):
        """
        Wrapper over Sanic to handle Sanic and url endpoint configurations

        Args:
            config(dict): Use this config instead of the config file. It's required for testing
        Attributes:
              self.config (Config): configuration object
        """
        # Configs
        self._config = Config(config_dir=config_dir).config
        super().__init__(name=self._config['service']['name'])
        self.__blueprints: Dict[Tuple[str, Optional[str]], Blueprint] = {}

        self.logger = logging.getLogger()
        self._testing = testing
        self.connections = {}

        self.logger.info("Webserver is initialized")

    def pre_run_configure(self):
        """
        Add configuration to the app but not start Sanic
        Returns:

        """
        log_conf = self._config['logging']
        service_conf = self._config['service']
        if log_conf:
            recursive_dictionary_update.update(LOGGING, log_conf)

        # blueprints (URL endpoints)
        self.blueprint(openapi_blueprint)
        self.blueprint(swagger_blueprint)

        # config
        self.config.API_VERSION = service_conf['api_version']
        self.config.API_TITLE = "{0} API".format(service_conf['name'])
        self.config.API_DESCRIPTION = "It's a API for admin.sch's {} microservice".format(service_conf['name'])
        self.config.API_TERMS_OF_SERVICE = 'Use with caution!'
        self.config.API_PRODUCES_CONTENT_TYPES = ['application/json']
        self.config.API_CONTACT_EMAIL = 'schacccc@sch.bme.hu'

        self.logger.debug("Webserver is configured")

        # Endpoints
        endpoints = {}
        for blueprint in self.__blueprints.values():
            try:
                self.blueprint(blueprint)
                for route in blueprint.routes:
                    endpoints[route.uri] = route.methods
            except RouteExists as rex:
                self.logger.warning('%s is already added (exists) to the webserver', rex)

        if not self.testing:
            # Start connecections
            self.connections = create_connections()

            self.connections['microservice_token_provider'] = self.connections['oauthclient'][0]

            loop = asyncio.get_event_loop()
            task = asyncio.ensure_future(self.connections['zookeeper'][0].cleanup_endpoints(service_conf['name'], endpoints.keys()))
            loop.run_until_complete(task)
            task = asyncio.ensure_future(self.connections['zookeeper'][0].create_endpoints(endpoints))
            loop.run_until_complete(task)

    @property
    def service_token(self):
        return self.connections['microservice_token_provider'].token

    def run(self, **kwargs):
        """
        It start the Sanic app. Binding to Sanic.run()
        Returns:

        """
        service_conf = self._config['service']
        if not self.testing:
            self.pre_run_configure()
            kwargs['host'] = service_conf['listen']['address']
            kwargs['port'] = service_conf['listen']['port']
            kwargs['log_config'] = LOGGING
            kwargs['debug'] = service_conf['debug']
        try:
            super().run(**kwargs)
        except KeyboardInterrupt:
            loop = asyncio.get_event_loop()
            task = asyncio.ensure_future(self.connections['zookeeper'][0].close())
            loop.run_until_complete(task)
            loop.close()

    def base_url(self,
                 api_ver: str = None,
                 url_base: str = None,
                 config: dict = False,
                 **kwargs
                ) -> Blueprint:
        r"""
        Get an URL root. Every added route will available under this root.
        Schema: <ip>:port/v<api_ver>/<url_base>/
        Args:
            config: If it's set than use this instead of the Config(). It's required for testing
            api_ver (str): API version. Default came from config
            url_base (str): Prefix for the custom url.
            **kwargs: pass to authentication and/or authorization methods

        Returns:
            Returns a Sanic Blueprint object
        """
        config = Config(config=config).config
        service_conf = config['service']

        if api_ver is None:
            api_ver = str(service_conf['api_version'])

        url = '/v' + api_ver

        if url_base is not None:
            url += url_base

        if (api_ver, url_base) not in self.__blueprints.keys():
            self.__blueprints[(api_ver, url_base)] = Blueprint(service_conf['name'], url)
            blueprint = self.__blueprints[(api_ver, url_base)]

            async def prevent_xss(request, response):  # pylint: disable=unused-argument
                """
                Add xss prevention to every respose
                Args:
                    request: HTTP request
                    response: HTTP response

                Returns:

                """
                response.headers["x-xss-protection"] = "1; mode=block"

            blueprint.middleware('response')(prevent_xss)

        return self.__blueprints[(api_ver, url_base)]

    get_blueprint = base_url

    @property
    def testing(self) -> bool:
        return self._testing

    @testing.setter
    def testing(self, value: bool):
        self._testing = value
