
import json
import sys
import socket
import threading
import time
import six
import importlib

from grpc import insecure_channel, RpcError, StatusCode

from rook.lib.logger import logger

from ..services.bdb_location_service import BdbLocationService

from rook.interfaces.protobuf import rook_pb2_grpc
from rook.interfaces.protobuf import rook_pb2

from rook.interfaces.config import AgentComConfiguration

from rook.exceptions import RookCommunicationException


class AgentCom(object):
    """This class handles the communication itself."""

    def __init__(self, aug_manager, trigger_services, output, agent_host, agent_port):
        self._aug_manager = aug_manager
        self._bdb = trigger_services.get_service(BdbLocationService.NAME)
        self._output = output

        self.agent_host = agent_host
        self.agent_port = agent_port

        self._channel = None
        self._client = None

        self._retries = 0

    def connect_to_agent(self):
        logger.debug("Attempting connection to agent")

        self.disable_gevent_for_grpc()
        self._build_client()

        try:
            self._start_new_connnection()
        except RookCommunicationException:
            logger.warn("Failed to connect to agent. Will keep trying")
            self._start_retry_thread()
            raise

    def send_rule_status_update(self, status_update):
        self._client.send_rule_status_update(status_update)

    def send_rook_messages(self, messages):
        self._client.send_messages(messages)

    def _build_client(self):
        if self._client:
            return

        # Build gRPC client
        logger.debug("Connecting to agent-\t%s:%d", self.agent_host, self.agent_port)
        options = [('grpc.max_receive_message_length', AgentComConfiguration.MAX_MESSAGE_LENGTH)]
        logger.debug("Creating channel")
        self._channel = insecure_channel(self.agent_host + ':' + str(self.agent_port), options=options)
        logger.debug("Creating client")
        self._client = rook_pb2_grpc.AgentManagementServiceStub(self._channel)

    def _start_new_connnection(self):
        logger.debug("Starting a new connection")

        logger.debug("Getting rook info")
        info = self._output.get_rook_info()

        logger.debug("Pinging")
        ping_message = rook_pb2.PingMessage()
        ping_message.value = 1
        try:
            self._client.ping(ping_message, timeout=AgentComConfiguration.GRPC_TIMEOUT)
        except Exception as e:
            message = "Failed to ping agent"
            logger.info(message, exc_info=1)
            six.raise_from(RookCommunicationException(message), e)

        logger.debug("Creating request")
        command_request = self._client.new_rook_notification(info)

        # Get initial augs
        success = self._command_loop(command_request)
        if not success:
            raise RookCommunicationException("Failed to connect to agent")

        # Setup update/retry channel in the background
        logger.info("Creating commands thread")
        thread = threading.Thread(target=self._command_thread, args=(command_request, ),
                                  name=AgentComConfiguration.COMMAND_THREAD_NAME)
        thread.daemon = True
        thread.start()

    def _command_loop(self, commands_request):
        logger.debug("Entering command loop")

        try:
            for command in commands_request:
                self._retries = 0

                if command.command_type == rook_pb2.RookCommand.COMMAND_ADD_AUG:
                    logger.info("Got an add aug command")
                    try:
                        self._aug_manager.add_aug(json.loads(command.aug_json))
                    except:
                        logger.exception("Error processing new aug")

                elif command.command_type == rook_pb2.RookCommand.COMMAND_REMOVE_AUG:
                    logger.info("Got a remove aug command")
                    try:
                        self._aug_manager.remove_aug(command.aug_id)
                    except:
                        logger.exception("Error removing aug")

                elif command.command_type == rook_pb2.RookCommand.COMAND_INIT_FINISHED:
                    logger.info("Finished initialization")
                    self._output.start_sending_messages()
                    return "Init Finished"

                elif command.command_type == rook_pb2.RookCommand.COMMAND_CLEAR_AUGS:
                    logger.info("Got clear augs command")
                    try:
                        self._aug_manager.clear_augs()
                    except:
                        logger.exception("Error in clearing augs")

                elif command.command_type == rook_pb2.RookCommand.COMMAND_SET_ROOK_ID:
                    logger.info("Got set rook_id command- %s", command.rook_id)
                    self._output.set_rook_id(command.rook_id)

                else:
                    logger.error("Unknown command %s", command)
        except RpcError as exc:
            # This exception can occur during process shutdown
            if StatusCode.CANCELLED == exc.code():
                self._output.stop_sending_messages()
                return "Process Exiting"

            if self._retries:
                logger.info("Error in command loop", exc_info=1)
            else:
                logger.exception("Error in command loop")
        except:
            if self._retries:
                logger.info("Error in command loop", exc_info=1)
            else:
                logger.exception("Error in command loop")

        self._output.stop_sending_messages()
        logger.warn("Exiting with failure")
        return None

    def _command_thread(self, command_request):
        logger.info("Command thread started")

        # Disable bdb monitoring of this thread
        self._bdb.ignore_current_thread()

        if command_request:
            ret = self._command_loop(command_request)
            # True here means the process is exiting
            if ret:
                return

        self._start_retry_thread()

    def _start_retry_thread(self):
        logger.info("Retry thread started")
        thread = threading.Thread(target=self._retry_thread,
                                  name=AgentComConfiguration.COMMAND_THREAD_NAME)
        thread.daemon = True
        thread.start()

    def _retry_thread(self):
        logger.info("Starting retry thread")

        # Disable bdb monitoring of this thread
        self._bdb.ignore_current_thread()

        self._retries = 0

        while True:
            try:
                self._start_new_connnection()
                break
            except:
                # Interpreter shutdown
                if not logger:
                    return

                if self._retries > 0:
                    backoff = AgentComConfiguration.BACK_OFF * (2 ** (self._retries - 1))
                    sleep_time = min((backoff, AgentComConfiguration.MAX_SLEEP))
                    logger.info("Sleeping for- %f", sleep_time)
                    time.sleep(sleep_time)
                self._retries += 1

    def disable_gevent_for_grpc(self):
        try:
            import gevent.monkey
        except ImportError:
            return

        if not gevent.monkey.is_module_patched('threading'):
            return

        # Rebuild a clean module based on a bundled copy of threading
        from . import threading as clean_threading
        clean_threading._start_new_thread = gevent.monkey.get_original('thread', 'start_new_thread')
        clean_threading._allocate_lock = gevent.monkey.get_original('thread', 'allocate_lock')
        clean_threading._get_ident = gevent.monkey.get_original('thread', 'get_ident')
        clean_threading.stack_size = gevent.monkey.get_original('thread', 'stack_size')
        clean_threading.local = gevent.monkey.get_original('thread', '_local')

        MODULE_LIST = [
            'grpc.beta.implementations',
            'grpc.beta.utilities',
            'grpc.beta._server_adaptations',
            'grpc.framework.foundation.stream_util',
            'grpc.framework.interfaces.base.base',
            'grpc._channel',
            'grpc._common',
            'grpc._plugin_wrapping',
            'grpc._server',
            'grpc._utilities'
        ]

        for module_name in MODULE_LIST:
            module = importlib.import_module(module_name)
            module.threading = clean_threading

        # CleanupThread has already inherited, so we override it
        # Copied from gRPC in order to build a clean version of the class
        class CleanupThread(clean_threading.Thread):
            """A threading.Thread subclass supporting custom behavior on join().

            On Python Interpreter exit, Python will attempt to join outstanding threads
            prior to garbage collection.  We may need to do additional cleanup, and
            we accomplish this by overriding the join() method.
            """

            def __init__(self, behavior, *args, **kwargs):
                """Constructor.

                Args:
                    behavior (function): Function called on join() with a single
                        argument, timeout, indicating the maximum duration of
                        `behavior`, or None indicating `behavior` has no deadline.
                        `behavior` must be idempotent.
                    args: Positional arguments passed to threading.Thread constructor.
                    kwargs: Keyword arguments passed to threading.Thread constructor.
                """
                super(CleanupThread, self).__init__(*args, **kwargs)
                self._behavior = behavior

            def join(self, timeout=None):
                start_time = time.time()
                self._behavior(timeout)
                end_time = time.time()
                if timeout is not None:
                    timeout -= end_time - start_time
                    timeout = max(timeout, 0)
                super(CleanupThread, self).join(timeout)

        # Restore threading for _common
        import grpc._common
        grpc._common.CleanupThread = CleanupThread
