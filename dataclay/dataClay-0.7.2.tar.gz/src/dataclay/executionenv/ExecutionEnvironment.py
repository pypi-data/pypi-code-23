from io import BytesIO
import logging
import lru
import uuid
import traceback
from dataclay.commonruntime.Runtime import getRuntime, setRuntime
from dataclay.commonruntime.Runtime import threadLocal
from dataclay.commonruntime.Settings import settings
from dataclay.communication.grpc.clients.ExecutionEnvGrpcClient import EEClient
from dataclay.communication.grpc.messages.common.common_messages_pb2 import LANG_PYTHON
from dataclay.paraver import trace_function
from dataclay.DataClayObjProperties import DCLAY_GETTER_PREFIX
from dataclay.DataClayObjProperties import DCLAY_PROPERTY_PREFIX
from dataclay.DataClayObjProperties import DCLAY_SETTER_PREFIX
from dataclay.serialization.lib.DeserializationLibUtils import deserialize_params
from dataclay.serialization.lib.DeserializationLibUtils import deserialize_object_with_data
from dataclay.serialization.lib.SerializationLibUtils import serialize_params_or_return, serialize_dcobj_with_data, \
    serialize_for_db
from dataclay.util.FileUtils import deploy_class
from dataclay.util.classloaders import ClassLoader
from dataclay.util.YamlParser import dataclay_yaml_load
from dataclay.commonruntime.ExecutionEnvironmentRuntime import ExecutionEnvironmentRuntime

__author__ = 'Alex Barcelo <alex.barcelo@bsc.es>'
__copyright__ = '2015 Barcelona Supercomputing Center (BSC-CNS)'

logger = logging.getLogger(__name__)


class ExecutionEnvironment(object):
    
    # FIXME de-hardcode this value
    cached_metadatainfo = lru.LRU(50)
    cached_sessioninfo = lru.LRU(50)
    logger = logging.getLogger(__name__)
    ee_name = None
    
    # This variable will store the following:
    #   - iface_bm (Interface BitMap): used across calls
    #   - session_id (SessionID): is maintained during a deep call
    #   - dataset_id (DataSetID): set on executeImplementation and newPersistentInstance,
    #                             and used for makePersistent of instances.
    thread_local_info = threadLocal
    
    """ Runtime of this execution environment """
    runtime = None

    def __init__(self, theee_name):
        self.runtime = ExecutionEnvironmentRuntime(self)
        self.ee_name = theee_name
        """ Initialize runtime """
        self.runtime.initialize_runtime()
        
    def get_runtime(self):
        """
        @return: Runtime of this Execution Environment 
        """ 
        return self.runtime
    
    def prepareThread(self):
        """ 
        Prepare thread local information. Threads contain information about session, dataset,... and it is also used 
        to obtain proper Runtimes. This function was designed for a multithreading design. 
        IMPORTANT: This function should be called at the beginning of all "public" functions in this module.
        """ 
        setRuntime(self.runtime)
    
    @trace_function
    def ds_deploy_metaclasses(self, namespace, classes_map_yamls):
        """Deploy MetaClass containers to the Python Execution Environment.
    
        This function stores in a file all the MetaClass, in addition to (optionally)
        putting them into the cache, according to the ConfigOptions.
    
        :param namespace: The namespace 
        :param classes_map: classes map
        :return: The response (empty string)
        """
        
        self.prepareThread()
        for class_name, clazz_yaml in classes_map_yamls.iteritems():
            metaclass = dataclay_yaml_load(clazz_yaml)
            ClassLoader.deploy_metaclass_grpc(
                namespace, class_name, clazz_yaml, metaclass)
    
            if metaclass.name == "UserType" or metaclass.name == "HashType":
                # logger.warning("Ignoring %s dataClay MetaClass" % metaclass.name)
                # logger.debug(metaclass)
                continue
    
            if metaclass.name == "DataClayPersistentObject" \
                    or metaclass.name == "DataClayObject"\
                    or metaclass.name == "StorageObject":
                continue
    
            # logger.info("Deploying class %s to deployment source path %s",
            #             metaclass.name, settings.deploy_path_source)
    
            try:
                # ToDo: check whether `lang_codes.LANG_PYTHON` or `'LANG_PYTHON'` is the correct key here
                import_lines = metaclass.languageDepInfos[LANG_PYTHON].imports
                imports = "\n".join(import_lines)
            except KeyError:
                # What is most likely is languageDepInfos not having the Python
                imports = ""
    
            deploy_class(metaclass.namespace, metaclass.name,
                         metaclass.juxtapose_code(True),
                         imports,
                         settings.deploy_path_source,
                         ds_deploy=True)
            # logger.debug("Deployment of class %s successful", metaclass.name)
    
        return str()
    
    def get_object_metadatainfo(self, object_id):
        """Get the MetaDataInfo for a certain object.
        :param object_id: The ID of the persistent object
        :return: The MetaDataInfo for the given object.
    
        If we have it available in the cache, return it. Otherwise, call the
        LogicModule for it.
        """
        
        self.prepareThread()
        logger.info("Getting MetaData for object {%s}", object_id)
    
        try:
            md_info = self.cached_metadatainfo[object_id]
            logger.debug("Hit on self.cached_metadatainfo")
        except KeyError:
            md_info = getRuntime().ready_clients["@LM"].get_metadata_by_oid(self.thread_local_info.session_id, object_id)
            self.cached_metadatainfo[object_id] = md_info
        return md_info
    
    def get_local_instance(self, session_id, object_id, retry=True):
        self.prepareThread()
        return getRuntime().get_or_new_instance_from_db(object_id, retry)
    
    def get_from_db(self, object_id):
        """Get object directly from StorageLocation (DB).
        
        :param session_id: ID of current session
        :param object_id: ID of object to get
        :return: python object
        """
        self.prepareThread()    
        py_object = getRuntime().get_or_new_instance_from_db(object_id, True)
    
        if py_object is None:
            raise Exception("Object from DB returns None")
    
        return py_object
    
    def internal_exec_impl(self, implementation_name, instance, params):
        """Internal (network-agnostic) execute implementation behaviour.
    
        :param instance: The object in which execution will be performed.
        :param implementation_name: Name of the implementation (may also be some dataClay specific $$get)
        :param params: The parameters (args)
        :return: The return value of the function being executed.
        """
        self.prepareThread()
        
        """
        TODO: use better design for this (dgasull) 
        It is possible that a property is set to None by the GC before we 'execute' it. It should be solve by always 
        checking if loaded before returning value. Check race conditions with GC. 
        """
        if not instance.is_loaded(): 
            getRuntime().load_object_from_db(instance, True)
    
        if implementation_name.startswith(DCLAY_GETTER_PREFIX):
            prop_name = implementation_name[len(DCLAY_GETTER_PREFIX):]
            ret_value = getattr(instance, DCLAY_PROPERTY_PREFIX + prop_name)
            logger.debug("Getter: for property %s returned %r", prop_name, ret_value)
    
        elif implementation_name.startswith(DCLAY_SETTER_PREFIX):
            prop_name = implementation_name[len(DCLAY_SETTER_PREFIX):]
            logger.debug("Setter: for property %s (value: %r)", prop_name, params[0])
            setattr(instance, DCLAY_PROPERTY_PREFIX + prop_name, params[0])
            ret_value = None
            instance.set_dirty(True)
    
        else:
            logger.debug("Call: %s(*args=%s)", implementation_name, params)
            dataclay_decorated_func = getattr(instance, implementation_name)
            ret_value = dataclay_decorated_func._dclay_entrypoint(instance, *params)
    
        return ret_value
    
    def set_local_session_and_dataset(self, session_id):
        """Set the global `self.thread_local_info` with Session and DataSet data.
    
        :param session_id: The UUID for SessionID.
        :return: None
    
        Set both the SessionID (just as provided) and also the DataSetID associated
        to that Session. Note that the cache is used (`cached_sessioninfo`) when
        available. If not in the cache, perform a getInfoOfSessionForDS RPC call.
        """
        self.prepareThread()
        try:
            session_info_entry = self.cached_sessioninfo[session_id]
        except KeyError:
            session_info_entry = getRuntime().ready_clients["@LM"].get_info_of_session_for_ds(session_id)
            self.cached_sessioninfo[session_id] = session_info_entry
    
        self.thread_local_info.session_id = session_id
        self.thread_local_info.dataset_id = session_info_entry[0][0]
    
    def store_objects(self, session_id, objects_data_to_store, moving, ids_with_alias):
        """
        @postcondition: Store objects in DB 
        @param session_id: ID of session storing objects 
        @param objects_data_to_store: Objects Data to store 
        @param moving: Indicates if store is done during a move 
        @param ids_with_alias: IDs with alias 
        """
        self.prepareThread()
    
        for cur_obj_data in objects_data_to_store: 
            object_id = cur_obj_data[0]
            metadata = cur_obj_data[2]
            obj_bytes = cur_obj_data[3]
            bytes_for_db = serialize_for_db(object_id, metadata, obj_bytes, True)
            getRuntime().ready_clients["@STORAGE"].store_to_db(object_id, bytes_for_db)    
        
    def register_and_store_pending(self, instance, obj_bytes, sync):
        
        object_id = instance.get_object_id()
        getRuntime().ready_clients["@STORAGE"].store_to_db(object_id, obj_bytes)    
        instance.set_pending_to_register(False)    
        # class_id = instance.get_class_extradata().class_id
        # reg_info = [object_id, class_id, instance.get_owner_session_id(), instance.get_dataset_id()]
        
        # getRuntime().ready_clients["@LM"].register_objects_from_ds_garbage_collector(reg_info, instance.get_hint())
        dataset_id = None
        reg_infos = list()
        dcc_extradata = instance.get_class_extradata()
        infos = [object_id, dcc_extradata.class_id, instance.get_owner_session_id(), dataset_id]
        reg_infos.append(infos)
            
        lm_client = getRuntime().ready_clients["@LM"]
        
        lm_client.register_objects(reg_infos, settings.environment_id, None, None,
                                           LANG_PYTHON)
        """
        // Inform MDS about new object !
            final Map<ObjectID, MetaClassID> storedObjs = new ConcurrentHashMap<>();
            storedObjs.put(instance.getObjectID(), instance.getMetaClassID());
    
            final Map<ObjectID, SessionID> objsSessions = new ConcurrentHashMap<>();
            objsSessions.put(instance.getObjectID(), instance.getOwnerSessionIDforVolatiles());
            final RegistrationInfo regInfo = new RegistrationInfo(instance.getObjectID(),
                    instance.getMetaClassID(), instance.getOwnerSessionIDforVolatiles(),
                    instance.getDataSetID());
    
            if (DEBUG_ENABLED) {
                logger.debug("[==RegisterPending==] Going to register " + regInfo + " for instance " + System.identityHashCode(instance));
            }
    
            if (sync) {
                final List<RegistrationInfo> regInfos = new ArrayList<>();
                regInfos.add(regInfo);
                this.runtime.getLogicModuleAPI().registerObjects(regInfos,
                        executionEnvironmentID, null, null, Langs.LANG_JAVA);
            } else {
                this.runtime.getLogicModuleAPI().registerObjectsFromDSGarbageCollector(regInfo,
                        executionEnvironmentID,
                        this.runtime);
            }
        """
        
    @trace_function
    def ds_exec_impl(self, object_id, implementation_id, serialized_params_grpc_msg, session_id):
        """Perform a Remote Execute Implementation.
    
        See Java Implementation for details on parameters and purpose.
        """
        self.prepareThread()
        self.set_local_session_and_dataset(session_id)
        logger.debug("Starting new execution")
        logger.debug("SessionID of current execution: %s", session_id)
        logger.debug("ObjectID of current execution: %s", object_id)
        logger.debug("ImplementationID in which the method belongs: %s", implementation_id)
    
        instance = self.get_local_instance(session_id, object_id, True)
    
        metaclass_container = instance.get_class_extradata().metaclass_container
        operation = metaclass_container.get_operation(implementation_id)
        logger.debug("DESERIALIZING PARAMETERS")
    
        num_params = serialized_params_grpc_msg[0]
        params = [] 
        if num_params > 0:
            params = deserialize_params(serialized_params_grpc_msg, None,
                                        operation.params,
                                        operation.paramOrder, getRuntime())
        logger.debug("STARTING EXECUTION")
    
        ret_value = self.internal_exec_impl(operation.name,
                                       instance,
                                       params)
        
        logger.debug("SERIALIZING RESULT ")
        if ret_value is None:
            logger.debug(" -> Returning None")
            return None
        
        logger.debug(" -> Serializing %s (type: %s)", ret_value, operation.returnType)
        return serialize_params_or_return({0: ret_value},
                                          None,
                                          {"0": operation.returnType},
                                          ["0"],
                                          None,
                                          getRuntime())  # No volatiles inside EEs
    
    @trace_function
    def new_persistent_instance(self, payload):
        """Create, make persistent and return an instance for a certain class."""
    
        raise NotImplementedError("NewPersistentInstance RPC is not yet ready (@ Python ExecutionEnvironment)")
    
    def new_replica(self, session_id, object_id, recursive):
        """Creates a new replica of the object with ID provided in the backend specified.
    
    	:param session_id: ID of session
    	:param object_id: ID of the object
    	:param recursive: Indicates if all sub-objects must be replicated as well.
    	:return: Set of IDs of replicated objects
    	"""
        logger.debug("[==Replica==] New replica for %s", object_id)
        self.prepareThread()
        
        object_ids = set()
        object_ids.add(object_id)
        serialized_objs = self.get_objects(session_id, object_ids, recursive, False)
    
        # Adds associated oid found in metadata in object_ids
        # ToDo: Check
        for obj_found in serialized_objs:
            for k in obj_found[2][0]:
                oid = obj_found[2][0][k]
                if oid not in object_ids:
                    logger.verbose("[==Replica==] Associated OID %s found in serialized_objects and not in object_ids", oid)
                    object_ids.add(oid)
                if not recursive:
                    break
    
        logger.debug("[==Replica==] Serialized_objs at the end are %s", serialized_objs)
    
        objects_list = self._check_and_prepare(serialized_objs)
    
        logger.debug("[==Replica==] Object list to store is %s", objects_list)
    
        for obj_id in object_ids:
            for obj in objects_list:
                obj_bytes = obj[3]
                if obj[0] == obj_id:                
                    metadata = obj[2]
                    bytes_for_db = serialize_for_db(obj_id, metadata, obj_bytes, False)
                    getRuntime().ready_clients["@STORAGE"].store_to_db(obj_id, bytes_for_db)    
    
        return object_ids
    
    def get_objects(self, session_id, object_ids, recursive, moving):
        """Get the serialized objects with id provided
    
    	:param session_id: ID of session
    	:param object_ids: IDs of the objects to get
    	:param recursive: Indicates if, per each object to get, also obtain its associated objects.
    	:param moving: Indicates we are getting object for a move
    	:return: List of serialized objects with ids provided
        """
        logger.debug("[==Get==] Getting objects %s", object_ids)
        self.prepareThread()
        
        result = list()
        self.thread_local_info.session_id = session_id
        pending_oids = list()
        obtained_objs = dict()
        objects_in_other_backend = list()
        is_pickle = False
    
        for oid in object_ids:
    
            if recursive:
                # Add object to pending
                pending_oids.append(oid)
    
                while pending_oids:
                    current_oid = pending_oids.pop()
    
                    if current_oid in obtained_objs:
                        # Already Read
                        logger.verbose("[==Get==] Object %s already read", current_oid)
                        continue
    
                    else:
                        try:
                            logger.verbose("[==Get==] Trying to get local instance for object %s", current_oid)
                            current_obj = self.get_local_instance(session_id, current_oid, False)
    
                            obj_with_data = self.get_object_internal(current_oid, moving)
                            result.append(obj_with_data)
    
                            # ToDo: Check and correct it
                            # ToDo: Get metadata from obj_with data and get hint
                            md_info = self.get_object_metadatainfo(current_oid)
    
                            # Get hint from metadata_info
                            for k, v in md_info.locations.iteritems():
                                hint = k
                                break
    
                            obtained_objs[current_oid] = hint
    
                            # Get associated objects and add them to pendings
                            for k in obj_with_data[2][0]:
                                oid_found = obj_with_data[2][0][k]
                                if oid_found != current_oid and oid_found not in obtained_objs:
                                    pending_oids.append(oid_found)
    
                        except Exception as e:
                            logger.debug("[==Get==] Object is in other backend")
                            # Get in other backend
                            objects_in_other_backend.append(current_oid)
            else:
                try:
                    result.append(self.get_object_internal(oid, moving))
                except Exception as e:
                    logger.debug("[==Get==] Object is in other backend")
                    # Get in other backend
                    objects_in_other_backend.append(oid)
    
        obj_with_data_in_other_backends = self.get_objects_in_other_backends(session_id, objects_in_other_backend,
                                                                        recursive, moving)
    
        logger.verbose("[==Get==] Object with data return length: %d", len(obj_with_data_in_other_backends))
        logger.trace("[==Get==] Object with data in other backends content: %s", obj_with_data_in_other_backends)
        for obj_in_oth_back in obj_with_data_in_other_backends:
            logger.trace("[==Get==] Append %s to the result", obj_in_oth_back)
            result.append(obj_in_oth_back)
    
        checked_result = self._check_and_prepare(result)
    
        return checked_result
    
    def get_object_internal(self, oid, moving):
        """Get object internal function
    
    	:param oid: ID of the object ot get
    	:param moving: Indicates we are getting object for a move
    	:return: Object with data
        """
        # Serialize the object
        logger.verbose("[==GetInternal==] Trying to get local instance for object %s", oid)
        self.prepareThread()
        
        # ToDo: Manage better this try/catch
    
        current_obj = self.get_local_instance(self.thread_local_info.session_id, oid, False)
    
        if moving:
            # TODO: Remove hint in order to avoid hints to be also moved.
            pass
    
        pending_objs = list()
        md_info = self.get_object_metadatainfo(oid)
        # ToDo: Remove hint for moving
    
        # ToDo: Check and correct it
        # Get hint from metadata_info
        for k, v in md_info.locations.iteritems():
            hint = k
            break
    
        # Add object to result and obtained_objs for return and recursive
        return serialize_dcobj_with_data(current_obj, pending_objs,
                                         False, hint, getRuntime(), False)
    
    def get_objects_in_other_backends(self, session_id, objects_in_other_backend, recursive, moving):
        """Get object in another backend. This function is called from DbHandler in a recursive get.
    
    	:param session_id: ID of session
    	:param objects_in_other_backend: List of metadata of objects to read. It is useful to avoid multiple trips.
    	:param recursive: Indicates is recursive
    	:param moving: Indicates if moving
    	:return: ID of objects and for each object, its bytes.
        """
        self.prepareThread()
        result = list()
    
        # Prepare to unify calls (only one call for DS)
        objects_per_backend = dict()
    
        for curr_oid in objects_in_other_backend:
            logger.debug("[==GetObjectsInOtherBackend==] Looking for metadata of %s", curr_oid)
    
            locations = self.get_object_metadatainfo(curr_oid).locations
            # FIXME Always obtain from the first location ??
            location = locations.popitem()[0]
    
            try:
                objects_in_backend = objects_per_backend[location]
            except KeyError:
                objects_in_backend = set()
                objects_per_backend[location] = objects_in_backend
            objects_in_backend.add(curr_oid)
    
        # Now Call
        for backend_id, objects_to_get in objects_per_backend.iteritems():
    
            logger.debug("[==GetObjectsInOtherBackend==] Get from other location, objects: %s", objects_to_get)
            backend = getRuntime().ready_clients["@LM"].get_executionenvironment_for_ds(backend_id)
    
            try:
                client_backend = getRuntime().ready_clients[backend_id]
            except KeyError:
                logger.verbose("[==GetObjectsInOtherBackend==] Not found Client to ExecutionEnvironment {%s}!"
                               " Starting it at %s:%d", backend_id, backend.hostname, backend.port)
    
                client_backend = EEClient(backend.hostname, backend.port)
                getRuntime().ready_clients[backend_id] = client_backend
    
            cur_result = client_backend.ds_get_objects(session_id, objects_to_get, recursive, moving)
    
            logger.verbose("[==GetObjectsInOtherBackend==] call return length: %d", len(cur_result))
            logger.trace("[==GetObjectsInOtherBackend==] call return content: %s", cur_result)
    
            for res in cur_result:
                result.append(res)
    
        return result
    
    def new_version(self, session_id, object_id, metadata_info):
        """Creates a new version of the object with ID provided in the backend specified.
    
    	:param session_id: ID of session
    	:param object_id: ID of the object
    	:param metadata_info: Metadata of the object, including the backends where the root object to be versioned is located
    	:return: The OID of the version root and the mapping from version OID to original OID for each versioned object
        """
        self.prepareThread()
        logger.debug("[==Version==] New version for %s ", object_id)
    
        # Get the data service of one of the backends that contains the original object.
        object_ids = set()
        object_ids.add(object_id)
    
        serialized_objs = self.get_objects(session_id, object_ids, True, False)
    
        # Prepare OIDs
        logger.debug("[==Version==] Serialized objects obtained to create version for %s are %s", object_id, serialized_objs)
        version_to_original = dict()
        original_to_version = dict()
        versions_hints = dict()
    
        # Store version in this backend (if already stored, just skip it)
        for obj in serialized_objs:
            orig_obj_id = obj[0]
            version_obj_id = uuid.uuid4()
            version_to_original[version_obj_id] = orig_obj_id
            original_to_version[orig_obj_id] = version_obj_id
            # ToDo: Manage hints for versions_hints dict
            # versions_hints[version_obj_id] = hint
    
        # ToDo: Add also versions_hints to modify_metadata_oids
        serialized_objs = [self._modify_metadata_oids(obj, original_to_version) for obj in serialized_objs]
        serialized_objs = [self._modify_oid(obj, original_to_version) for obj in serialized_objs]
    
        logger.debug("[==Version==] Serialized Objects after modification are %s", serialized_objs)
    
        # Store versions
        objs_to_store = self._check_and_prepare(serialized_objs)
    
        for obj in objs_to_store:
            obj_id = obj[0]
            metadata = obj[2]
            obj_bytes = obj[3]
            logger.info("obj_id is %s, obj_data are %s", obj_id, obj_bytes)
            
            bytes_for_db = serialize_for_db(obj_id, metadata, obj_bytes, False)
            
            getRuntime().ready_clients["@STORAGE"].store_to_db(obj_id, bytes_for_db)
            
        # Modify metadata_info
        version_id = original_to_version[object_id]
        environments = dict()
        environments[settings.environment_id] = getRuntime().ready_clients["@LM"].get_executionenvironment_for_ds(settings.environment_id)
    
        logger.debug("[==Version==] Modifying metadataInfo: %s", metadata_info)
        version_md = metadata_info
        version_md.locations = environments
        logger.debug("[==Version==] Added metadata info to MetaData Cache: %s : %s", version_id, version_md)
        self.cached_metadatainfo[version_id] = version_md
        logger.debug("[==Version==] Version finished for object %s , newVersion oid is: %s", object_id, version_id)
    
        return version_id, version_to_original
    
    def consolidate_version(self, session_id, version):
        """Consolidates all the objects in versionInfo, being the current data service the one containing all the versioned
    	   objects. For each versioned object, its OID is set to the original one according to the mapping in versionInfo,
    	   and the consolidated object is stored in the same locations as the original one (before versioning). The versions
    	   are deleted.
    
    	:param session_id:ID of session
    	:param version: Info of the version
        """
        self.prepareThread()
        # Consolidate in this backend - the complete version is here
        version_to_original = version.versionsMapping
    
        original_hints = dict()
        # ToDo: Check it
        for version_oid, original_oid in version_to_original.iteritems():
            original_md = version.originalMD[original_oid]
            # ToDo: Correct this assignment
            for k, v in original_md.locations.iteritems():
                original_hints[original_oid] = k
                break
    
        logger.debug("[==Consolidate==] Consolidating %s", version.versionOID)
    
        version_object_ids = set()
        # Get bytes of all version objects
        for k, v in version_to_original.iteritems():
            version_object_ids.add(k)
    
        dirty_version_bytes = self.get_objects(session_id, version_object_ids, True, False)
        logger.debug("[==Consolidate==] Version objs obtained are %s", dirty_version_bytes)
    
        # Update original objects
        # ToDo: Add also versions_hints to modify_metadata_oids
        version_bytes = list()
    
        for vers_byte in dirty_version_bytes:
            # Change the stream position to 0
            vers_byte[3].seek(0)
            modified_metadata = self._modify_metadata_oids(vers_byte, version_to_original)
            modified_oid = self._modify_oid(modified_metadata, version_to_original)
            version_bytes.append(modified_oid)
    
        logger.trace("[==Consolidate==] Version objs modified are %s", version_bytes)
    
        dest_loc = None
    
        try:
            self.thread_local_info.session_id = session_id
    
            # Update original objects (here and in other DSs - replicas)
            orig_oid = version_to_original[version.versionOID]
            md_info = version.originalMD[orig_oid]
            locs = md_info.locations
            for loc_id in locs:
                dest_loc = locs[loc_id]
                if loc_id == settings.environment_id:
                    logger.verbose("[==Consolidate==] Upsert Objects in this DS")
                    self.upsert_objects(session_id, version_bytes)
                else:
                    try:
                        st_client = getRuntime().ready_clients[loc_id]
                    except KeyError:
                        logger.verbose("[==Consolidate==] Not found Client to ExecutionEnvironment {%s}!"
                                       " Starting it at %s:%d", loc_id, dest_loc.hostname, dest_loc.port)
    
                        st_client = EEClient(dest_loc.hostname, dest_loc.port)
                        getRuntime().ready_clients[loc_id] = st_client
    
                    logger.debug("[==Consolidate==] Going to other DS to upsert %s", version_to_original[version.versionOID])
                    st_client.ds_upsert_objects(session_id, version_bytes)
    
                # Delete versions here
                # FIXME: G.C. should do it
                # commonruntime.ready_clients["@STORAGE"].ds_remove_objects(session_id, version_object_ids, True, False, dest_loc)
    
        except Exception as e:
            traceback.print_exc()
            logger.error("Exception during Consolidate Version")
            raise e
        
        logger.debug("[==Consolidate==] Consolidate ended")
    
    def _check_and_prepare(self, serialized_objs):
        """ Check if serialized_obj are in the right format and prepare the objects_list to send to store_objects """
        objects_list = list()
    
        for obj in serialized_objs:
            logger.trace("[==CheckAndPrepare==] Obj in Serialized objs content: %s", obj)
    
            # ToDo ToDo ToDo
            # Since the ds_store_objects is serializing again we deserialize the data before sending it
            # ToDo: Correct this
            if not isinstance(obj[3], BytesIO):
                logger.verbose("Type for (obj[3]): %s", type(obj))
                logger.trace("Bytes (obj[3]) serialized in wrong way for %s", obj)
                serialized_obj = BytesIO(obj[3])
            else:
                serialized_obj = obj[3]
            dcobj = obj[0], obj[1], obj[2], serialized_obj
            objects_list.append(dcobj)
    
        return objects_list
    
    def _modify_metadata_oids(self, obj, original_to_version):
        """ Modify the version's metadata in serialized_objs with original OID"""
        self.prepareThread()
        logger.debug("[==ModifyMetadataOids==] Modify serialized object %r", obj)

        for tag, oid in obj[2][0].iteritems():
            obj[2][0][tag] = original_to_version[oid]

        logger.debug("[==ModifyMetadataOids==] Object with modified metadata is %r", obj)

        return obj
    
    def _modify_oid(self, obj, original_to_version):
        """ Modify the version's OID in serialized_objs with the original OID"""
        new_obj = original_to_version[obj[0]], obj[1], obj[2], obj[3]
        return new_obj
    
    def upsert_objects(self, session_id, object_ids_and_bytes):
        """Updates objects or insert if they do not exist with the values in objectBytes.
        NOTE: This function is recursive, it is going to other DSs if needed.
        :param session_id: ID of session needed.
    	:param object_ids_and_bytes: Map of objects to update.
    	"""
        self.prepareThread()
        self.thread_local_info.session_id = session_id
    
        try:
            objects_in_other_backends = list()
    
            # To check for replicas
            for cur_entry in object_ids_and_bytes:
                # ToDo: G.C. stuffs
                object_id = cur_entry[0]
                logger.debug("[==Upsert==] Updated or inserted object %s", object_id)
                try:
                    # Update bytes at memory object
                    logger.debug("[==Upsert==] Getting/Creating instance from upsert with id %s", object_id)
                    instance = getRuntime().get_or_new_instance_from_db(object_id, False)
                    # ToDo: Check deserialization
                    deserialize_object_with_data(cur_entry, instance, None, getRuntime(), getRuntime().get_session_id(), True)
                except Exception:
                    # Get in other backend
                    objects_in_other_backends.append(cur_entry)
    
            self.upsert_objects_in_other_backend(session_id, objects_in_other_backends)
    
        except Exception as e:
            traceback.print_exc()
            logger.error("Exception during Upsert Objects")
            raise e
    
    def upsert_objects_in_other_backend(self, session_id, objects_in_other_backends):
        """Update object in another backend.
    
    	:param session_id: ID of session
    	:param objects_in_other_backends: List of metadata of objects to update and its bytes. It is useful to avoid multiple trips.
    	:return: ID of objects and for each object, its bytes.
        """
        self.prepareThread()
        # Prepare to unify calls (only one call for DS)
        objects_per_backend = dict()
        for curr_obj_with_ids in objects_in_other_backends:
            
            curr_oid = curr_obj_with_ids[0]
            # ToDo: Get Metadata for cur_entry and retrieve locations
            locations = self.get_object_metadatainfo(curr_oid).locations
            # FIXME Always obtain from the first location ??
            location = locations.popitem()[0]
            # Update object at first location (NOT UPDATING REPLICAS!!!)
            # ToDo: Correct locations use
            try:
                objects_in_backend = objects_per_backend[location]
            except KeyError:
                objects_in_backend = list()
                objects_per_backend[location] = objects_in_backend
                
            objects_in_backend.append(curr_obj_with_ids)
        # Now Call
        # ToDo: Check this for
        for backend_id, objects_to_update in objects_per_backend.iteritems():
    
            backend = getRuntime().ready_clients["@LM"].get_executionenvironment_for_ds(backend_id)
    
            try:
                client_backend = getRuntime().ready_clients[backend_id]
            except KeyError:
                logger.verbose("[==GetObjectsInOtherBackend==] Not found Client to ExecutionEnvironment {%s}!"
                               " Starting it at %s:%d", backend_id, backend.hostname, backend.port)
    
                client_backend = EEClient(backend.hostname, backend.port)
                getRuntime().ready_clients[backend_id] = client_backend
    
            client_backend.ds_upsert_objects(session_id, objects_to_update)
