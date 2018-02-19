"""Initialization and finalization of dataClay client API.

The `init` and `finish` functions are availble through the
dataclay.api package.
"""

import importlib
import logging
import random
import uuid

from dataclay.commonruntime.ExecutionGateway import ExecutionGateway
from dataclay.commonruntime.Settings import settings
from dataclay.communication.grpc.clients.ExecutionEnvGrpcClient import EEClient
from dataclay.communication.grpc.messages.common.common_messages_pb2 import LANG_PYTHON
from dataclay.exceptions.exceptions import DataclayException
from dataclay.serialization.lib.DeserializationLibUtils import deserialize_return
from dataclay.serialization.lib.SerializationLibUtils import serialize_params_or_return, serialize_dcobj_with_data
from dataclay.commonruntime.DataClayRuntime import DataClayRuntime
from dataclay.commonruntime.RuntimeType import RuntimeType
from dataclay.heap.ClientHeapManager import ClientHeapManager
from dataclay.loader.ClientObjectLoader import ClientObjectLoader

# Sentinel-like object to catch some typical mistakes
UNDEFINED_LOCAL = object()


class ClientRuntime(DataClayRuntime):
    
    current_type = RuntimeType.client

    def __init__(self):
        
        DataClayRuntime.__init__(self)
        
    def initialize_runtime_aux(self):
        self.dataclay_heap_manager = ClientHeapManager(self)
        self.dataclay_object_loader = ClientObjectLoader(self)
        
    def is_exec_env(self):
        return False

    def get_object_by_id(self, object_id):
        # Note that this method requires several calls to the LogicModule
        # (getObjectInfo). If the class_id is available, like the typical response
        # or parameter serialization, it is better to use the new_instance method.
        o = self.get_from_heap(object_id)
        if o is not None:
            return o
    
        full_name, namespace = self.ready_clients["@LM"].get_object_info(
            settings.current_session_id, object_id)
        self.logger.debug("Trying to import full_name: %s from namespace %s",
                     full_name, namespace)
    
        # Rearrange the division, full_name may include dots (and be nested)
        prefix, class_name = ("%s.%s" % (namespace, full_name)).rsplit('.', 1)
        m = importlib.import_module(prefix)
        klass = getattr(m, class_name)
    
        dataset_id = self.ready_clients["@LM"].get_object_dataset_id(
            settings.current_session_id, object_id)
        
        o = self.get_or_new_persistent_instance(object_id, klass.get_class_extradata().class_id, None)
        o.set_dataset_id(dataset_id)
        return o
    
    def get_or_new_persistent_instance(self, object_id, metaclass_id, hint):
        """
        @postcondition: Check if object with ID provided exists in dataClay heap. If so, return it. Otherwise, create it.
        @param object_id: ID of object to get or create 
        @param metaclass_id: ID of class of the object (needed for creating it) 
        @param hint: Hint of the object, can be None. 
        """ 
        # TODO: if class id is null, look in metadata 
        
        return self.dataclay_object_loader.get_or_new_persistent_instance(metaclass_id, object_id, hint)
    
    def new_replica(self, object_id, backend_id, recursive):
        self.logger.debug("Starting new replica")
        session_id = settings.current_session_id
        return self.ready_clients["@LM"].new_replica(session_id, object_id, backend_id, recursive)
    
    def new_version(self, object_id, backend_id):
        self.logger.debug("Starting new version")
        session_id = settings.current_session_id
        return self.ready_clients["@LM"].new_version(session_id, object_id, backend_id)
    
    def consolidate_version(self, version_info):
        self.logger.debug("Starting consolidate version")
        session_id = settings.current_session_id
        return self.ready_clients["@LM"].consolidate_version(session_id, version_info)
    
    def get_execution_environment_by_oid(self, object_id):
        metadata = self.ready_clients["@LM"].get_metadata_by_oid(
            settings.current_session_id, object_id)
    
        self.logger.debug("Received the following MetaDataInfo for object %s: %s",
                     object_id, metadata)
        return iter(metadata.locations).next()
    
    def get_all_execution_environments_by_oid(self, object_id):
        metadata = self.ready_clients["@LM"].get_metadata_by_oid(
            settings.current_session_id, object_id)
    
        self.logger.debug("Received the following MetaDataInfo for object %s: %s",
                     object_id, metadata)
        return metadata.locations
    
    def get_execution_environments_info(self):
        return self.ready_clients["@LM"].get_execution_environments_info(settings.current_session_id,
                                                                         LANG_PYTHON)
    
    def get_by_alias(self, dclay_cls, alias):
        class_id = ExecutionGateway.get_class_extradata(dclay_cls).class_id
    
        oid, hint = self.ready_clients["@LM"].get_object_from_alias(
            settings.current_session_id, class_id, alias)

        # ToDo: Use get_or_new_persistent_instance instead of get_object_by_id??
        return self.get_object_by_id(oid)
    
    def delete_alias(self, dclay_cls, alias):
        class_id = ExecutionGateway.get_class_extradata(dclay_cls).class_id
    
        self.ready_clients["@LM"].delete_alias(settings.current_session_id, class_id, alias)
    
    def store_object(self, instance):
        raise RuntimeError("StoreObject can only be used from the ExecutionEnvironment")
    
    def move_object(self, instance, source_backend_id, dest_backend_id):
        client = self.ready_clients["@LM"]
        self.logger.debug("Moving object %r from %s to %s",
                     instance, source_backend_id, dest_backend_id)
    
        object_id = instance.get_object_id()
    
        client.move_objects(settings.current_session_id, object_id,
                            source_backend_id, dest_backend_id)
    
    def make_persistent(self, instance, alias, backend_id, recursive):
        client = self.ready_clients["@LM"]
        self.logger.debug("Starting make persistent object for instance %s with id %s", instance,
                     instance.get_object_id())
    
        reg_infos = list()
        only_register = False
    
        if instance.is_persistent():
            # ToDo: current type is always Client
            if self.current_type == RuntimeType.exe_env:
                only_register = True
                self.logger.debug("Object need to be only registered")
            else:
                self.logger.verbose("Trying to make persistent %r, which already is persistent. Ignoring", self)
                return
    
        if backend_id is UNDEFINED_LOCAL:
            # This is a commonruntime end user pitfall,
            # @abarcelo thinks that it is nice
            # (and exceptionally detailed) error
            raise RuntimeError("""
    You are trying to use dataclay.api.LOCAL but either:
      - dataClay has not been initialized properly
      - LOCAL has been wrongly imported.
    
    Be sure to use LOCAL with:
    
    from dataclay import api
    
    and reference it with `api.LOCAL`
    
    Refusing the temptation to guess.""")
    
        if backend_id is None:
            # If no execution environment specified select it randomly
            backend_id = random.choice(self.get_execution_environments_info().keys())
    
        self.logger.verbose("ExecutionEnvironment chosen for MakePersistent is: %s", backend_id)
    
        hint = backend_id
    
        ignore_user_types = not recursive
        serialized_objs = list()
        persisted_object = list()
        pending_objs = list()
        datasets_specified = dict()
    
        # OidsCreated: OIDS created while serializing metadata or the objects found
        # objs_already_persistent: All objects that are already persistent
        objs_already_persistent = list()
    
        pending_objs.append(instance)
    
        while pending_objs:
            current_obj = pending_objs.pop()
    
            object_id = current_obj.get_object_id()
            dataset_id = current_obj.get_dataset_id()
    
            dcc_extradata = current_obj.get_class_extradata()
            class_id = dcc_extradata.class_id
    
            if class_id is None:
                raise RuntimeError("ClassID is None. Stubs are not used properly.")
    
            # Registration Info
            # ToDo: current type is always Client
            if only_register and self.current_type == RuntimeType.exe_env:
                infos = [object_id, class_id,
                         settings.current_session_id, dataset_id]
                reg_infos.append(infos)
    
            # Ignore already persistent objects
            if current_obj.is_persistent() or object_id in objs_already_persistent:
                continue
    
            # ToDo: Check it
            # This object will soon be persistent
            current_obj.set_persistent(True)
            current_obj.set_loaded(False)
    
            # First store since others OIDs are recursively created while creating MetaData
            if not object_id:
                object_id = uuid.uuid4()
                current_obj.set_object_id(object_id)
    
            # Store dataset id in the datasets dict
            if dataset_id is not None:
                datasets_specified[object_id] = dataset_id
            else:
                # And assume that it will be put to the dataset_for_store accordingly to the session
                dataset_id = client.get_dataset_id(settings.current_id,
                                                   settings.current_credential,
                                                   settings.dataset_for_store)
                datasets_specified[object_id] = dataset_id
                
            objs_already_persistent.append(object_id)
    
            # During serialization, ObjectIDs of found objects can be set since it is
            # necessary for serializing MetaData of each object!
            # Serialize the objects to make persistent
            self.logger.verbose("Adding object to make persistent call: instance %s", current_obj)
    
            serialized_objs.append(
                serialize_dcobj_with_data(current_obj, pending_objs,
                                          ignore_user_types, hint, self, False)
            )
            persisted_object.append(object_id)
    
            infos = [object_id, class_id,
                     settings.current_session_id, dataset_id]
    
            if infos not in reg_infos:
                reg_infos.append(infos)
    
        # Cache the (object_id, hint) tuple with alias as key
        object_id_to_have_alias = None
        if alias is not None:
            object_id_to_have_alias = instance.get_object_id()
            self.logger.debug("Adding to cache object with alias %s and oid %s",
                         alias, object_id_to_have_alias)
            self.alias_cache[alias] = (object_id_to_have_alias, hint)
    
        if only_register:
            # Register them
            objs_to_register = list()
            for reg_info in serialized_objs:
                objs_to_register.append(reg_info[0])
            self.logger.debug("[==DS MakePersistent==] Registering objects %s with location %s", objs_to_register, hint)
    
            client.register_objects(reg_infos, backend_id,
                                    object_id_to_have_alias, alias,
                                    LANG_PYTHON)
    
            for reg_obj in reg_infos:
                obj = self.get_object_by_id(reg_obj[0])
                if obj is not None:
                    self.logger.debug(
                        "[==MakePersistent==] Setting flag persistent from registerObjects: %s", reg_obj)
                    instance.set_persistent(True)
    
        else:
    
            objs_to_register = list()
            for reg_info in serialized_objs:
                objs_to_register.append(reg_info[0])
    
            for reg_obj in reg_infos:
                # ToDo: Check it
                if reg_obj[0] == instance.get_object_id():
                    self.logger.debug(
                        "[==MakePersistent==] Setting flag persistent from registerObjects: %s", reg_obj)
                    instance.set_persistent(True)
    
            if alias is not None:
                self.logger.debug("Making persistent object %s with alias %s and associated objects: %s",
                             instance.get_object_id(),
                             alias, objs_to_register)
    
            else:
                self.logger.debug("Making persistent object %s and associated objects: %s",
                             instance.get_object_id(),
                             objs_to_register)
    
            client.make_persistent(session_id=settings.current_session_id,
                                   dest_backend_id=backend_id,
                                   serialized_objects=serialized_objs,
                                   ds_specified=datasets_specified,
                                   object_to_have_alias=object_id_to_have_alias,
                                   alias=alias)
    
        self.logger.verbose("[==MakePersistent==] Make Persistent finished of object = %s", instance)
    
    def execute_implementation_aux(self, operation_name, instance, parameters, exeenv_id=None):
        stub_info = instance.get_class_extradata().stub_info
        implementation_stub_infos = stub_info.implementations
        object_id = instance.get_object_id()
        
        self.logger.verbose("Calling operation '%s' in object with ID %s", operation_name, object_id)
        self.logger.debug("Call is being done into %r with #%d parameters",
                     instance, len(parameters))
        
        # # Check if object is being deserialized (params/returns)
        # ToDo: volatiles under deserialization, needed in Python? (dgasull)
        
        # // === HINT === //
        if exeenv_id is None and instance.get_hint() is not None:
            exeenv_id = instance.get_hint()
            self.logger.verbose("Using hint = %s", exeenv_id)
        
        # // === DEFAULT EXECUTION LOCATION === // CURRENTLY NOT SUPPORTED 
        # ToDo: remove in java (dgasull)
        
        # // === HASHCODE EXECUTION LOCATION === //
        # ToDo: modify make persistent to use hashcode instead of random
        if exeenv_id is None:
            exeenv_id = self.get_execution_environment_by_oid(object_id)
            self.logger.verbose("Obtaining location for execution = %s", exeenv_id)
    
        # // === SERIALIZE PARAMETERS === //
        serialized_params = serialize_params_or_return(
            params=parameters,
            iface_bitmaps=None,
            params_spec=implementation_stub_infos[operation_name].parameters,
            params_order=implementation_stub_infos[operation_name].paramsOrder,
            hint_volatiles=exeenv_id,
            runtime=self)
        
        remote_impl = [implementation_stub_infos[operation_name].remoteImplID,
                       implementation_stub_infos[operation_name].contractID,
                       implementation_stub_infos[operation_name].interfaceID]
    
        # // === EXECUTE === //
        max_retry = 3
        executed = False
        last_exception = None
        for k in range(max_retry):
            try:
                self.logger.verbose("Obtaining API for remote execution in %s ", exeenv_id)
                execution_client = self.ready_clients[exeenv_id]
            except KeyError:
                exeenv = self.get_execution_environments_info()[exeenv_id] 
                self.logger.debug("Not found in cache ExecutionEnvironment {%s}! Starting it at %s:%d",
                               exeenv_id, exeenv.hostname, exeenv.port)
                execution_client = EEClient(exeenv.hostname, exeenv.port)
                self.ready_clients[exeenv_id] = execution_client
    
            try:
                self.logger.verbose("Calling remote EE %s ", exeenv_id)
                ret = execution_client.ds_execute_implementation(
                    object_id,
                    remote_impl[0],
                    settings.current_session_id,
                    serialized_params)
                executed = True
                break
            
            except DataclayException as dce: 
                last_exception = dce
                self.logger.debug("Exception dataclay during execution. Retrying...")
                self.logger.debug(str(dce))
                exeenv_id = self.get_execution_environment_by_oid(object_id)
                if self.logger.isEnabledFor(logging.DEBUG):
                    self.logger.debug("MetaDataInfo received for object: %s", object_id)
                
        if not executed:
            raise last_exception
    
        self.logger.verbose("Result of operation named '%s' received", operation_name)
    
        if ret is None:
            return None
        else:
            return deserialize_return(ret,
                                      None,
                                      implementation_stub_infos[operation_name].returnType, self)

    def run_remote(self, object_id, backend_id, operation_name, value):
        try:
            execution_client = self.ready_clients[backend_id]
        except KeyError:
            exeenv = self.get_execution_environments_info()[backend_id]
            execution_client = EEClient(exeenv.hostname, exeenv.port)
            self.ready_clients[backend_id] = execution_client
        dcc_extradata = self.get_object_by_id(object_id).get_class_extradata()
        stub_info = dcc_extradata.stub_info
        implementation_stub_infos = stub_info.implementations
        operation = implementation_stub_infos[operation_name]

        value = serialize_params_or_return(
            params=(value,),
            iface_bitmaps=None,
            params_spec=operation.parameters,
            params_order=operation.paramsOrder,
            hint_volatiles=None,
            runtime=self
        )

        ret = execution_client.ds_execute_implementation(object_id, operation.remoteImplID, settings.current_session_id, value)

        if ret is not None:
            return deserialize_return(ret, None, operation.returnType, self)
