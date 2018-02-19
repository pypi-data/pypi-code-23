"""Deserialization code related to DataClay objects

The code implemented in this module is (at "this moment") identical to the ones
implemented in the Java package client.CommonLib. Specifically, the deserialize*
functions are more or less adapted here.
"""

from io import BytesIO
import logging

from dataclay.exceptions.exceptions import InvalidPythonSignature
from dataclay.serialization.python.lang.VLQIntegerWrapper import VLQIntegerWrapper
from dataclay.serialization.python.util.PyTypeWildcardWrapper import PyTypeWildcardWrapper
import dataclay.communication.grpc.messages.common.common_messages_pb2 as common_messages
from dataclay.communication.grpc.Utils import get_metadata

__author__ = 'Alex Barcelo <alex.barcelo@bsc.es>'
__copyright__ = '2015 Barcelona Supercomputing Center (BSC-CNS)'

logger = logging.getLogger(__name__)


def deserialize_params(serialized_params_or_return, iface_bitmaps,
        param_specs, params_order, runtime):
    return deserialize_params_or_return(serialized_params_or_return,
                        iface_bitmaps,
                        param_specs,
                        params_order, runtime)


def _create_buffer_and_deserialize(obj_bytes, instance, ifacebitmaps, metadata, cur_deser_python_objs):
    """
    @postcondition: Create buffer and deserialize
    @param obj_bytes: bytes to deserialize 
    @param instance: Instance to deserialize
    @param ifacebitmaps: Map of bitmaps representing the interfaces to use
    @param metadata: object metadata
    @param cur_deser_python_objs: Currently deserialized Java objects
    """
    
    # TODO: bytes is an io_file, use a buffer instead
    instance.deserialize(obj_bytes, ifacebitmaps, metadata, cur_deser_python_objs)

    
def deserialize_grpc_message_from_db(obj_bytes):
    """
    @postcondition: Deserialize grpc message from DB 
    @param obj_bytes: object bytes
    @return grpc msg stored in db
    """
    msg = common_messages.PersistentObjectInDB()
    msg.ParseFromString(obj_bytes)
    return msg


def deserialize_object_from_db(object_to_fill, object_bytes, runtime):
    """
    @postcondition: Deserialize object from bytes
    @param object_to_fill: object to fill
    @param object_bytes: Object bytes
    @param runtime: runtime 
    """

    msg = deserialize_grpc_message_from_db(object_bytes)
    metadata = get_metadata(msg.metadata)
    deserialize_object_from_db_bytes_aux(object_to_fill, metadata, msg.data, runtime)

    
def deserialize_object_from_db_bytes_aux(object_to_fill, metadata, data, runtime):
    """
    @postcondition: Deserialize object from bytes into instance provided
    @param metadata: object metadata
    @param data: Object data
    @param runtime: runtime 
    """
    
    cur_deser_python_objs = dict() 
    obj_bytes = BytesIO(data)
    _create_buffer_and_deserialize(obj_bytes, object_to_fill, None, metadata, cur_deser_python_objs)
    object_to_fill.set_loaded(True)
    object_to_fill.set_persistent(True)
    
    """
    GARBAGE COLLECTOR RACE CONDITION
    ================================
    If some object was cleaned and removed from GC retained refs, it does NOT mean it was removed
    from Weak references map (Heap) because we will ONLY remove an entry in Heap if it is
    pointing to NULL, i.e. the Java GC removed it.
    So, if some execution is requested after we remove an entry from retained refs (we cleaned and send
    the object to disk), we check if the
    object is in Heap (see executeImplementation in DS) and therefore, we created a new reference
    making impossible for Java GC to clean the reference. We will add the object to retained references
    again once it is deserialized from DB.
    """
    runtime.retain_in_heap(object_to_fill)
    
    
def deserialize_objbytes_from_db_into_obj_data(object_id, obj_bytes_from_db, runtime):
    """
    @postcondition: Deserialize object from bytes into ObjectData and return it. 
    @param object_id: ID of object
    @param obj_bytes_from_db: Object bytes
    @param runtime: Runtime to use
    @return object data (to send) of this object
    """
    logger.debug("OBJECT_ID %s, OBJ_BYTES %s", object_id, obj_bytes_from_db)
    
    msg = deserialize_grpc_message_from_db(obj_bytes_from_db)
    metadata = get_metadata(msg.metadata)
    obj_bytes = BytesIO(msg.data)

    logger.debug("METADATA %s and METADATA CLASS_ID %s", metadata, metadata[1][0])

    return object_id, metadata[1][0], metadata, obj_bytes


def deserialize_metadata_from_db(obj_bytes_from_db):
    """
    @postcondition: deserialize metadata from db (just metadata)
    @param obj_bytes_from_db: object bytes from db
    @return metadata of the object
    """
    msg = common_messages.PersistentObjectInDB()
    msg.ParseFromString(obj_bytes_from_db)
    metadata = get_metadata(msg.metadata)
    return metadata


def deserialize_object_with_data(param_or_ret, instance, ifacebitmpas, runtime, owner_session_id, force_deserialization):
    """ 
    @postcondition: Deserialize object into a memory instance. ALSO called from executeImplementation in case of 'executions during
    deserialization'. THIS FUNCTION SHOULD NEVER BE CALLED FROM CLIENT SIDE.
    @param param_or_ret: Param/return bytes and metadata
    @param instance: Object in which to deserialize data
    @param ifacebitmaps: Interface bitmaps
    @param runtime: the runtime 
    @param owner_session_id: Can be None. ID of owner session of the object. Used for volatiles pending to register. 
    @param force_deserialization: Check if the object is loaded or not. If FALSE and loaded, then no deserialization is happening. If TRUE, then
    deserialization is forced.
    """
    
    """
    FORCE DESERIALIZATION NOTE.
    Volatiles in server can be created in two ways: received from client or in some execution.
    If created during execution, flag loaded = true, but if received, flag loaded should be false until
    the object is properly loaded. In order to control the first case, constructor of the object is
    setting loaded to true and here we set it to false. Therefore we need to "force" deserialization sometimes.
    Also happening in update of objects and cleaning in GC.
    """     
    """ Lock object until deserialization is finished in case another instance is waiting to do the same so much """ 
    runtime.lock(instance.get_object_id())
    try:
        if force_deserialization or not instance.is_loaded():
            """ TODO: improve GRPC messages """
            metadata = param_or_ret[2]
            obj_bytes = BytesIO(param_or_ret[3])
            cur_deser_python_objs = dict()
            _create_buffer_and_deserialize(obj_bytes, instance, None, metadata, cur_deser_python_objs)
            instance.set_loaded(True)
            instance.set_persistent(True)
            if owner_session_id is not None:
                instance.set_owner_session_id(owner_session_id)
    
    finally:
        runtime.unlock(instance.get_object_id())

    
def deserialize_return(serialized_params_or_return, iface_bitmaps, return_type, runtime):
    
    if serialized_params_or_return[0] == 0:
        return None 
    return deserialize_params_or_return(serialized_params_or_return,
                        iface_bitmaps,
                        {"0": return_type},
                        ["0"], runtime)[0]


def deserialize_params_or_return(serialized_params_or_return,
        iface_bitmaps, param_specs, params_order, runtime):
    """ 
    @postcondition: deserialize parameters or return of an execution 
    @param serialized_params_or_return: serialized parameters or return 
    @param iface_bitmaps: interface bitmaps 
    @param param_specs: specifications of parameters 
    @param params_order: order of parameters
    @param runtime: runtime being used
    """
    num_params = serialized_params_or_return[0]
    params = [None] * num_params

    """ VOLATILES """
    first_volatile = True 
    for i, serialized_param in serialized_params_or_return[3].iteritems():
        """ TODO: move this into a private function, only used in EE """ 
        """ CLIENT CANNOT DESERIALIZE VOLATILES """ 
        object_id = serialized_param[0]
        class_id = serialized_param[1]
        
        if first_volatile: 
            runtime.add_volatiles_under_deserialization(serialized_params_or_return[3])
            first_volatile = False
        
        deserialized_param = runtime.get_or_new_volatile_instance_and_load(object_id, class_id, runtime.get_hint(),
                                                                           serialized_param, iface_bitmaps)
        
        if i < num_params:
            params[i] = deserialized_param
    
    """ LANGUAGE """ 
    for i, serialized_param in serialized_params_or_return[2].iteritems():

        obj_bytes = BytesIO(serialized_param[1])
        params[i] = deserialize_language(obj_bytes, param_specs[params_order[i]])
    
    """ IMMUTABLES """
    for i, serialized_param in serialized_params_or_return[1].iteritems():

        obj_bytes = BytesIO(serialized_param)
        params[i] = deserialize_immutable(obj_bytes, param_specs[params_order[i]])
    
    """ PERSISTENT """ 
    for i, serialized_param in serialized_params_or_return[4].iteritems():

        object_id = serialized_param[0]
        hint = serialized_param[1]
        class_id = serialized_param[2]
        deserialized_param = runtime.get_or_new_persistent_instance(object_id, class_id, hint)
        deserialized_param.set_persistent(True)
        if i < num_params:
            params[i] = deserialized_param
            # Set hint in metadata (ToDo: create general getOrNewInstance)       

    if not first_volatile:
        runtime.remove_volatiles_under_deserialization()
    
    return params


def deserialize_association(io_file, iface_bitmaps,
        metadata, cur_deserialized_objs, runtime):
    """
    @postcondition: deserialize association 
    @param io_file: bytes of the object containing the association
    @param iface_bitmaps: interface bitmaps
    @param metadata: metadata of the object 
    @param cur_deserialized_objs: current deserialized objects
    @param runtime: the runtime
    """

    tag = VLQIntegerWrapper().read(io_file)
    logger.info("Deserializing association for tag: %d", tag)
    logger.info("Metadata OIDs: %s", metadata[0])
    object_id = metadata[0][tag]
    logger.info("Metadata ClassIDs: %s", metadata[1])
    metaclass_id = metadata[1][tag]
    # TODO: NumRefs ( metadata[3]) not deserialized?? Ask about
    # metadata[3] is io_file (Check it?)

    hint = None
    try:
        logger.info("Metadata Hints: %s", metadata[2])
        hint = metadata[2][tag]
    except KeyError: 
        pass

    obj = runtime.get_or_new_persistent_instance(object_id, metaclass_id, hint)
    cur_deserialized_objs[tag] = obj
    return obj


def deserialize_immutable(io_file, type_):
    # Well, if it is a primitive type we already have them...
    try:
        ptw = PyTypeWildcardWrapper(type_.signature)
    except InvalidPythonSignature:
        raise NotImplementedError("Only Java primitive types are "
                                      "understood in Python.")
    return ptw.read(io_file)


def deserialize_language(io_file, type_):
    # Well, if it is a primitive type we already have them...
    try:
        ptw = PyTypeWildcardWrapper(type_.signature)
    except InvalidPythonSignature:
        raise NotImplementedError("In fact, InvalidPythonSignature was "
                                      "not even implemented, seems somebody is "
                                      "raising it without implementing logic.")
    return ptw.read(io_file)


class PersistentLoadPicklerHelper(object):
    """Helper to solve deserialization of associations inside Pickled structures.

    See https://docs.python.org/2.7/library/pickle.html#pickling-and-unpickling-external-objects
    for more information of what this is doing.

    The `__call__` method is being called by Pickle for persistent ids, i.e.,
    objects that have been serialized by PersistentIdPicklerHelper and thus
    are associations (DataClayObjects).

    The code is very close to the deserialize association.
    """
    def __init__(self, metadata, cur_deserialized_objs, runtime):
        self._metadata = metadata
        self._runtime = runtime
        self._cur_deserialized_objs = cur_deserialized_objs

    def __call__(self, str_tag):
        tag = int(str_tag)
        logger.verbose("Deserializing association for tag: %d", tag)
        logger.debug("Metadata OIDs: %s", self._metadata[0])
        object_id = self._metadata[0][tag]
        logger.debug("Metadata ClassIDs: %s", self._metadata[1])
        metaclass_id = self._metadata[1][tag]

        # TODO: NumRefs ( metadata[3]) not deserialized?? Ask about
        # metadata[3] is io_file (Check it?)

        hint = None
        try:
            logger.debug("Metadata Hints: %s", self._metadata[2])
            hint = self._metadata[2][tag]
        except KeyError:
            logger.debug("No Metadata Hints")
            pass

        obj = self._runtime.get_or_new_persistent_instance(object_id, metaclass_id, hint)
        self._cur_deserialized_objs[tag] = obj
        return obj
