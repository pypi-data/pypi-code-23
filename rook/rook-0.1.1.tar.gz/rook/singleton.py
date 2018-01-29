"""This module is in charge of managing the rook's module state.

The external interface for the module is Rook located in rook.rook."""

import os
import struct

from rook.lib.logger import logger

from rook.interfaces.config import AgentAddress

from .augs.augs_manager import AugsManager
from .output import Output
from .com.agent_com import AgentCom
from .trigger_services import TriggerServices


class _Singleton(object):
    """This is singleton is the class managing the module.

    It should never be referred to directly, instead use obj in this module."""

    def __init__(self):
        """Initialize the object, sets member variables."""

        logger.info("Initializing Rook under process-%d", os.getpid())

        self._services_started = False

        self._trigger_services = TriggerServices()
        self._output = Output(self._trigger_services)
        self._aug_manager = None

        self._agent_com = None

    def _start_trigger_services(self):
        """Start trigger services.

        Calling this method multiple times will have no effect.
        """

        # Don't double init services
        if self._services_started:
            return

        self._trigger_services.start()
        self._aug_manager = AugsManager(self._trigger_services, self._output)
        self._services_started = True

    def _stop_trigger_services(self):
        if not self._services_started:
            return

        self._aug_manager = None
        self._trigger_services.close()

        self._services_started = False

    def set_rook_information(self, **kwargs):
        """Set the user-supplied version information for the application."""
        if self._agent_com:
            raise RookInterfaceException("Rook information must be set before connection!")

        self._output.set_user_info(kwargs)

    def collect_data(self, description, send_by_default, **kwargs):
        """Collect data based on a user triggered event."""
        raise NotImplementedError()

    def connect(self, host, port):
        """Connect to the Agent."""
        if self._agent_com:
            raise RookInterfaceException("Multiple connection attempts not supported!")

        if not host:
            try:
                host = os.environ['ROOKOUT_AGENT_HOST']
            except KeyError:
                host = AgentAddress.HOST

        if not port:
            try:
                port = os.environ['ROOKOUT_AGENT_PORT']
            except KeyError:
                port = AgentAddress.PORT

        self._start_trigger_services()

        logger.debug("Initiating AgentCom-\t%s:%d", host, port)
        self._agent_com = AgentCom(self._aug_manager, self._trigger_services, self._output, host, port)
        self._output.set_agent_com(self._agent_com)

        self._agent_com.connect_to_agent()
        logger.info("Successful connection to agent")

singleton_obj = _Singleton()
