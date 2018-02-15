import importlib
import logging
import uuid
from dataclay.communication.grpc.clients.ExecutionEnvGrpcClient import EEClient
from dataclay.communication.grpc.messages.common.common_messages_pb2 import LANG_PYTHON
from dataclay.exceptions.exceptions import DataclayException
from dataclay.paraver import trace_function
from dataclay.commonruntime.DataClayRuntime import DataClayRuntime
from dataclay.commonruntime.RuntimeType import RuntimeType
from dataclay.commonruntime.Settings import settings
from dataclay.serialization.lib.DeserializationLibUtils import deserialize_return  # Import after DataClayRuntime to avoid circular imports
from dataclay.serialization.lib.SerializationLibUtils import serialize_dcobj_with_data, serialize_params_or_return  # Import after DataClayRuntime to avoid circular imports
from dataclay.commonruntime.ExecutionGateway import ExecutionGateway
from dataclay.heap.ExecutionEnvironmentHeapManager import ExecutionEnvironmentHeapManager
from dataclay.loader.ExecutionObjectLoader import ExecutionObjectLoader
from dataclay.commonruntime.Runtime import threadLocal

__author__ = 'Alex Barcelo <alex.barcelo@bsc.es>'
__copyright__ = '2015 Barcelona Supercomputing Center (BSC-CNS)'

logger = logging.getLogger(__name__)


class ExecutionEnvironmentRuntime(DataClayRuntime):
    
    current_type = RuntimeType.exe_env
    
    """ Execution Environment using this runtime. """
    execution_environment = None
    
    def __init__(self, theexec_env):
        DataClayRuntime.__init__(self)
        self.execution_environment = theexec_env

    def initialize_runtime_aux(self):
        self.dataclay_heap_manager = ExecutionEnvironmentHeapManager(self)
        self.dataclay_object_loader = ExecutionObjectLoader(self)
        
    def is_exec_env(self):
        return True

    def get_or_new_persistent_instance(self, object_id, metaclass_id, hint):
        """
        @postcondition: Check if object with ID provided exists in dataClay heap. If so, return it. Otherwise, create it.
        @param object_id: ID of object to get or create 
        @param metaclass_id: ID of class of the object (needed for creating it) 
        @param hint: Hint of the object, can be None. 
        """ 
        return self.dataclay_object_loader.get_or_new_persistent_instance(metaclass_id, object_id, hint)

    def get_or_new_instance_from_db(self, object_id, retry):
        """
        @postcondition: Get object from memory or database and WAIT in case we are still waiting for it to be persisted.
        @param object_id: ID of object to get or create 
        @param retry: indicates if we should retry and wait 
        """ 
        return self.dataclay_object_loader.get_or_new_instance_from_db(object_id, retry)

    def get_or_new_volatile_instance_and_load(self, object_id, metaclass_id, hint,
                                              obj_with_data, ifacebitmaps):
        """
        @postcondition: Get from Heap or create a new volatile in EE and load data on it.
        @param object_id: ID of object to get or create 
        @param metaclass_id: ID of class of the object (needed for creating it) 
        @param hint: Hint of the object, can be None. 
        @param obj_with_data: data of the volatile instance 
        @param ifacebitmaps: interface bitmaps
        """ 
        return self.dataclay_object_loader.get_or_new_volatile_instance_and_load(metaclass_id, object_id, hint, obj_with_data, ifacebitmaps)

    def add_volatiles_under_deserialization(self, volatiles):
        """
        @postcondition: Add volatiles provided to be 'under deserialization' in case any execution in a volatile is thrown 
        before it is completely deserialized. This is needed in case any deserialization depends on another (not for race conditions)
        like hashcodes or other similar cases.
        @param volatiles: volatiles under deserialization
        """
        pass
   
    def remove_volatiles_under_deserialization(self):
        """
        @postcondition: Remove volatiles under deserialization
        """
        pass 
    
    def load_object_from_db(self, instance, retry):
        """
        @postcondition: Load DataClayObject from Database
        @param instance: DataClayObject instance to fill
        @param retry: Indicates retry loading in case it is not in db.
        """
        return self.dataclay_object_loader.load_object_from_db(instance, retry)
    
    def get_hint(self):
        """
        @postcondition: Get hint of the current EE 
        @return Hint of current EE
        """
        return settings.environment_id
    
    def retain_in_heap(self, dc_object):
        """
        @postcondition: Retain in heap
        @param dc_object: Object to retain.
        """
        self.dataclay_heap_manager.retain_in_heap(dc_object)
        
    def flush_all(self):
        """
        @postcondition: Flush all objects in memory to disk.
        """
        self.dataclay_heap_manager.flush_all()
    
    def get_session_id(self):
        """
        @postcondition: Get Session ID associated to current thread 
        @return: Session ID associated to current thread 
        """
        return threadLocal.session_id
    
    def get_execution_environment(self):
        """
        @return: Return execution environment using this runtime 
        """ 
        return self.execution_environment
    
    @trace_function
    def store_object(self, instance):
        if not instance.is_persistent():
            raise RuntimeError("StoreObject should only be called on Persistent Objects. "
                               "Ensure to call make_persistent first")
    
        self.internal_store(instance, make_persistent=False)
    
    # FixMe: For the moment is not updated
    @trace_function
    def make_persistent(self, instance, alias, dest_ee_id, recursive):
        if instance.is_persistent():
            logger.verbose("Trying to make persistent %r, which already is persistent. Ignoring", self)
            return
    
        # TODO: add support for that:
        if alias is not None:
            logger.warning("Server-side make_persistent with alias is not supported. Ignoring.")
    
        # TODO: add support for that:
        if dest_ee_id is not None:
            logger.warning("Server-side EE pinning on make_persistent is not supported. Ignoring.")
    
        self.internal_store(instance, make_persistent=True)
    
    @trace_function
    def get_object_by_id(self, object_id):
        """Obtain a (thin) PersistentObject from the ObjectID
        :param object_id: The UUID of the Object
        :return: An Execution Class instance, typically with
        ExecuteRemoteImplementation as True
        """
            
        o = self.get_from_heap(object_id)
        if o is not None:
            return o
    
        full_name, namespace = self.ready_clients["@LM"].get_object_info(
            self.execution_environment.thread_local_info.session_id, object_id)
        logger.debug("Trying to import full_name: %s from namespace %s",
                     full_name, namespace)
    
        # Rearrange the division, full_name may include dots (and be nested)
        prefix, class_name = ("%s.%s" % (namespace, full_name)).rsplit('.', 1)
        m = importlib.import_module(prefix)
        klass = getattr(m, class_name)
    
        dataset_id = self.ready_clients["@LM"].get_object_dataset_id(
            self.execution_environment.thread_local_info.session_id, object_id)

        o = self.get_or_new_persistent_instance(object_id, ExecutionGateway.get_class_extradata(klass).class_id, None)
        o.set_dataset_id(dataset_id)
        return o
    
    def new_replica(self, object_id, backend_id, recursive):
        logger.debug("Starting new replica from EE")
        session_id = self.execution_environment.thread_local_info.session_id
        return self.ready_clients["@LM"].new_replica(session_id, object_id, backend_id, recursive)

    def get_execution_environment_by_oid(self, object_id):
        # TODO: perform some cache on that, or use the local StorageLocation's cache
        metadata = self.ready_clients["@LM"].get_metadata_by_oid(
            self.execution_environment.thread_local_info.session_id, object_id)
    
        logger.debug("Received the following MetaDataInfo for object %s: %s",
                     object_id, metadata)
        return iter(metadata.locations).next()
    
    def get_all_execution_environments_by_oid(self, object_id):
        # TODO: perform some cache on that, or use the local StorageLocation's cache
        metadata = self.ready_clients["@LM"].get_metadata_by_oid(
            self.execution_environment.thread_local_info.session_id, object_id)
    
        logger.debug("Received the following MetaDataInfo for object %s: %s",
                     object_id, metadata)
        return metadata.locations
    
    def get_execution_environments_info(self):
        
        return self.ready_clients["@LM"].get_execution_environments_info(self.execution_environment.thread_local_info.session_id,
                                                                         LANG_PYTHON)
    
    # ToDo: Correct the hint use
    def get_by_alias(self, dclay_cls, alias):
        class_id = ExecutionGateway.get_class_extradata(dclay_cls).class_id
    
        oid, hint = self.ready_clients["@LM"].get_object_from_alias(
            self.execution_environment.thread_local_info.session_id, class_id, alias)
    
        return self.get_object_by_id(oid)
    
    def move_object(self, instance, source_backend_id, dest_backend_id):
        client = self.ready_clients["@LM"]
        logger.debug("Moving object %r from %s to %s",
                     instance, source_backend_id, dest_backend_id)
    
        object_id = instance.get_object_id()
    
        client.move_objects(self.execution_environment.thread_local_info.session_id,
                            object_id, source_backend_id, dest_backend_id)
    
    def execute_implementation_aux(self, operation_name, instance, parameters, exeenv_id=None):

        if instance.is_loaded():
            # Client
            raise RuntimeError("Execute Implementation Aux commonruntime helper should only be called for non-loaded")
    
        object_id = instance.get_object_id()
        
        logger.debug("Calling execute_implementation inside EE for operation %s and object id %s", operation_name, object_id)
    
        # # ============================== PARAMS/RETURNS ========================== //
        # # Check if object is being deserialized (params/returns)
        # ToDo: volatiles under deserialization, needed in Python? (dgasull)
        
        # // === HINT === //
        thisExecEnv = settings.environment_id
        if exeenv_id is None:
            if instance.get_hint() is not None:
                exeenv_id = instance.get_hint()
                logger.debug("Using hint %s for object id %s", exeenv_id, object_id)
            else:
                logger.debug("Asking for EE of object with id %s", object_id)
                exeenv_id = self.get_execution_environment_by_oid(object_id)
        
        if exeenv_id == thisExecEnv:        
            logger.debug("Object execution is local")
    
            # Note that fat_instance tend to be the same as instance...
            # *except* if it is a proxy
            fat_instance = self.execution_environment.get_local_instance(self.execution_environment.thread_local_info.session_id, object_id)
            return self.execution_environment.internal_exec_impl(operation_name, fat_instance, parameters) 
        else:
            logger.debug("Object execution is not local")
    
            object_id = instance.get_object_id()
        
            # // === SERIALIZE PARAMETERS === //
            dcc_extradata = instance.get_class_extradata()
            metaclass_container = dcc_extradata.metaclass_container
            # iface_bm = self.execution_environment.thread_local_info.iface_bm
            operation = metaclass_container.get_operation_from_name(operation_name)

            serialized_params = serialize_params_or_return(
                params=parameters,
                iface_bitmaps=None,
                params_spec=operation.params,
                params_order=operation.paramOrder,
                hint_volatiles=None,
                runtime=self)  # No volatiles inside EEs
        
            # // === EXECUTE === //
            max_retry = 3
            executed = False
            for k in range(max_retry):
                try:
                    execution_client = self.ready_clients[exeenv_id]
                except KeyError:
                    exeenv = self.get_execution_environments_info()[exeenv_id] 
                    logger.verbose("Not found in cache ExecutionEnvironment {%s}! Starting it at %s:%d",
                                   exeenv_id, exeenv.hostname, exeenv.port)
                    execution_client = EEClient(exeenv.hostname, exeenv.port)
                    self.ready_clients[exeenv_id] = execution_client
        
                try:
                    ret = execution_client.ds_execute_implementation(
                        object_id,
                        operation.implementations[0].dataClayID,
                        self.execution_environment.thread_local_info.session_id,
                        serialized_params)
                    executed = True
                    break
                
                except DataclayException: 
                    
                    exeenv_id = self.get_execution_environment_by_oid(object_id)
                    if logger.isEnabledFor(logging.DEBUG):
                        logger.debug("MetaDataInfo received for object: %s", object_id)
            
            if not executed:
                raise Exception("Server execution jump failed")
        
            # ToDo: Check it with the replicas
            logger.verbose("Result of operation named '%s' received", operation_name)
            if ret is None:
                return None
            else:
                return deserialize_return(ret,
                                            None,
                                            operation.returnType, self)
    
    #########################################
    # Helper functions, not commonruntime methods #
    #########################################
    
    def internal_store(self, instance, make_persistent=True):
        """Perform the storage (StoreObject call) for an instance.
    
        :param instance: The DataClayObject willing to be stored.
        :param make_persistent: Flag, True when DS_STORE_OBJECT should be called
        and False when DS_UPSERT_OBJECT is the method to be called.
        :return: A dictionary containing the classes for all stored objects.
    
        This function works for two main scenarios: the makePersistent one (in
        which the instance is not yet persistent) and the update (in which the
        instance is persistent).
    
        The return dictionary is the same in both cases, but note that the update
        should not use the provided instance for updating metadata to the LM.
        """
    
        client = self.ready_clients["@STORAGE"]
    
        pending_objs = [instance]
        stored_objects_classes = dict()
        serialized_objs = list()
    
        while pending_objs:
            current_obj = pending_objs.pop()
    
            # Ignore already persistent objects
            if current_obj.is_persistent() and make_persistent:
                continue
    
            dcc_extradata = current_obj.get_class_extradata()
            object_id = current_obj.get_object_id()
    
            # This object will soon be persistent
            current_obj.set_persistent(True)
            # Just in case (should have been loaded already)
            current_obj.set_loaded(True)
    
            # First store since others OIDs are recursively created while creating MetaData
            if not object_id:
                assert make_persistent, "Objects should never be uuid-less for non-make_persistent use cases"
                object_id = uuid.uuid4()
                current_obj.set_object_id(object_id)
                current_obj.set_dataset_id(self.execution_environment.thread_local_info.dataset_id)
    
            logger.debug("Ready to make persistent object {%s} of class %s {%s}" % 
                         (object_id, dcc_extradata.classname, dcc_extradata.class_id))
    
            stored_objects_classes[object_id] = dcc_extradata.class_id
    
            # If we are not in a make_persistent, the dataset_id hint is null (?)
            serialized_objs.append(serialize_dcobj_with_data(
                current_obj, pending_objs, False, None, self, False))
    
        if make_persistent:
            
            # TODO make some cache or something more intelligent here
            dataset_id = self.execution_environment.thread_local_info.dataset_id if make_persistent else None
            reg_infos = list()
            dcc_extradata = current_obj.get_class_extradata()
            infos = [object_id, dcc_extradata.class_id,
                     self.execution_environment.thread_local_info.session_id, dataset_id]
            reg_infos.append(infos)
        
            lm_client = self.ready_clients["@LM"]
    
            lm_client.register_objects(reg_infos, settings.environment_id, None, None,
                                       LANG_PYTHON)
            client.ds_store_objects(self.execution_environment.thread_local_info.session_id, serialized_objs, False, None)
        else:
            client.ds_upsert_objects(self.execution_environment.thread_local_info.session_id, serialized_objs)

    def run_remote(self, object_id, backend_id, operation_name, value):
        try:
            execution_client = self.ready_clients[backend_id]
        except KeyError:
            exeenv = self.get_execution_environments_info()[backend_id]
            execution_client = EEClient(exeenv.hostname, exeenv.port)
            self.ready_clients[backend_id] = execution_client

        dcc_extradata = self.get_object_by_id(object_id).get_class_extradata()
        metaclass_container = dcc_extradata.metaclass_container
        operation = metaclass_container.get_operation_from_name(operation_name)
        value = serialize_params_or_return(
            params=(value,),
            iface_bitmaps=None,
            params_spec=operation.params,
            params_order=operation.paramOrder,
            hint_volatiles=None,
            runtime=self
        )

        ret = execution_client.ds_execute_implementation(object_id, operation.implementations[0].dataClayID, self.execution_environment.thread_local_info.session_id, value)

        if ret is not None:
            logger.trace("Execution return %s of type %s", ret, operation.returnType)
            return deserialize_return(ret, None, operation.returnType, self)
        
