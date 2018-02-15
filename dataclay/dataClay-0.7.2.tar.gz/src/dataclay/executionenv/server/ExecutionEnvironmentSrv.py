"""The basic dataClay server features for Python Execution Environments.

This module provides the Execution Environment for Python. A basic dataClay
infrastructure is required, mainly:

  - Logic Module
  - Storage Locations
  - [optional] More Execution Environments

Note that this server must be aware of the "local" Storage Location and the
central Logic Module node.
"""
from concurrent import futures
import grpc
import logging
import os
import socket
import sys
import time
import signal
import threading 

from dataclay.commonruntime.Settings import settings
from dataclay.communication.grpc.clients.ExecutionEnvGrpcClient import EEClient
from dataclay.communication.grpc.clients.LogicModuleGrpcClient import LMClient
from dataclay.communication.grpc.generated.dataservice import dataservice_pb2_grpc as ds
from dataclay.communication.grpc.messages.common.common_messages_pb2 import LANG_PYTHON
from dataclay.communication.grpc.server.ExecutionEnvironmentService import DataServiceEE
from dataclay.paraver import trace_function
from dataclay.util.classloaders import ClassLoader  # Import after DataClayRuntime to avoid circular imports
from dataclay.util.config.CfgExecEnv import set_defaults
from dataclay.executionenv.ExecutionEnvironment import ExecutionEnvironment

__author__ = 'Alex Barcelo <alex.barcelo@bsc.es>'
__copyright__ = '2015 Barcelona Supercomputing Center (BSC-CNS)'

logger = logging.getLogger(__name__)


class ExecutionEnvironmentSrv(object):
    
    execution_environment = None

    def reset_caches(self):
        logger.info("Received SIGHUP --proceeding to reset caches")
        ClassLoader.cached_metaclass_info.clear()
        ClassLoader.cached_metaclasses.clear()
    
    def persist_and_exit(self):
        logger.info("Performing exit hook --persisting files")
        
        self.execution_environment.prepareThread()
        self.execution_environment.get_runtime().stop_gc()
        logger.info("Flushing all objects to disk")
        self.execution_environment.get_runtime().flush_all()
        logger.info("Stopping runtime")
        self.execution_environment.get_runtime().stop_runtime()

    @trace_function
    def preface_autoregister(self):
        """Perform a pre-initialization of stuff (prior to the autoregister call)."""
        self.execution_environment.prepareThread()
        # logger.info("Preface Autoregister")
    
        # Check if there is an explicit IP for autoregistering
        local_ip = os.getenv("DATASERVICE_HOST", "")
        if not local_ip:
            local_ip = socket.gethostbyname(socket.gethostname())
    
        logger.info("Starting client to LogicModule at %s:%d",
                     settings.logicmodule_host, settings.logicmodule_port)
    
        lm_client = LMClient(settings.logicmodule_host, settings.logicmodule_port)
    
        # Leave the ready client to the LogicModule globally available
        self.execution_environment.get_runtime().ready_clients["@LM"] = lm_client
    
        # logger.info("local_ip %s returned", local_ip)
        return local_ip
    
    @trace_function
    def start_autoregister(self, local_ip):
        """Start the autoregister procedure to introduce ourselves to the LogicModule."""
        self.execution_environment.prepareThread()

        logger.info("Start Autoregister with %s local_ip", local_ip)
        lm_client = self.execution_environment.get_runtime().ready_clients["@LM"]
    
        success = False
        retries = 0
        while not success:
            try:
                storage_location_id, execution_environment_id = lm_client.lm_autoregister_ds(
                    settings.dataservice_name,
                    local_ip,
                    settings.dataservice_port,
                    LANG_PYTHON)
            except Exception as e:
                logger.debug("Catched exception of type %s. Message:\n%s", type(e), e)
                if retries > 15:
                    logger.warn("Could not create channel, aborting (reraising exception)")
                    raise
                else:
                    logger.info("Could not create channel, retry #%d of 15 in 3 seconds" % retries)
                    # FIXME: Not Very performing, find a better way
                    time.sleep(3)
                    retries += 1
            else:
                success = True
    
        logger.info("Current DataService autoregistered. Associated StorageLocationID: %s",
                    storage_location_id)
        settings.storage_id = storage_location_id
        settings.environment_id = execution_environment_id
    
        # Retrieve the storage_location connection data
        storage_location = lm_client.get_storage_location_for_ds(storage_location_id)
    
        logger.debug("StorageLocation data: {name: '%s', hostname: '%s', port: %d}",
                     storage_location.name,
                     storage_location.hostname,
                     storage_location.storageTCPPort)
    
        logger.info("Starting client to StorageLocation {%s} at %s:%d",
                    storage_location_id, storage_location.hostname, storage_location.storageTCPPort)
    
        storage_client = EEClient(storage_location.hostname, storage_location.storageTCPPort)
    
        # Leave the ready client to the Storage Location globally available
        self.execution_environment.get_runtime().ready_clients["@STORAGE"] = storage_client
    
    def start(self):
        """Start the dataClay server (Execution Environment).
    
        Keep in mind that the configuration in both dataClay's global ConfigOptions
        and the server-specific one called ServerConfigOptions should be accurate.
        Furthermore, this function expects that the caller will take care of the
        dataClay library initialization.
    
        This function does not return (by itself), so feel free to spawn it inside
        a greenlet or a subprocess (typical in testing)
        """
        
        set_defaults()

        # Create the deployment folder and add it to the path
        try:
            os.makedirs(settings.deploy_path_source)
        except OSError as e:
            if e.errno != 17:
                # Not the "File exists" expected error, reraise it
                raise
        sys.path.insert(1, settings.deploy_path_source)
        
        self.execution_environment = ExecutionEnvironment(settings.dataservice_name)
        # logger.debug("Current sys.path: %s", sys.path)
    
        logger.info("Starting DataServiceEE on %s:%d", settings.server_listen_addr,
                    settings.server_listen_port)
    
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=1000),
                             options=(('grpc.max_send_message_length', 1000 * 1024 * 1024,),
                                      ('grpc.max_receive_message_length', 1000 * 1024 * 1024,),
                                      ))
    
        ee = DataServiceEE(self.execution_environment)
        ds.add_DataServiceServicer_to_server(ee, self.server)
    
        address = str(settings.server_listen_addr) + ":" + str(settings.server_listen_port)
    
        # ToDo: Better way for start server?
        self.server.add_insecure_port(address)
        self.server.start()
        self.local_ip = self.preface_autoregister()
        self.start_autoregister(self.local_ip)
        ee.ass_client()
                
        try:
            signal.pause()
        except RuntimeError:
            logger.info("Runtime Error")
            return
        finally:
            logger.info("** Finishing python Execution Environment **")
            self.exit_gracefully()
    
    def exit_gracefully(self, signum, frame):
        logger.info("** Exiting gracefully **")
        self.persist_and_exit()
        self.server.stop(0)

    def get_name(self):
        return settings.dataservice_name
