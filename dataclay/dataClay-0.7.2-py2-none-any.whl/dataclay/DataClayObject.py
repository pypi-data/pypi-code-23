"""Management of Python Classes.

This module is responsible of management of the Class Objects. A central Python
Metaclass is responsible of Class (not object) instantiation.

Note that this managers also includes most serialization/deserialization code
related to classes and function call parameters.
"""
from logging import getLogger
from operator import attrgetter
from uuid import UUID
from cPickle import Pickler, Unpickler
import uuid
from dataclay.DataClayObjMethods import dclayMethod
from dataclay.DataClayObjProperties import DCLAY_PROPERTY_PREFIX
from dataclay.DataClayObjectExtraData import DataClayInstanceExtraData
from dataclay.commonruntime.ExecutionGateway import ExecutionGateway
from dataclay.commonruntime.Runtime import getRuntime
from dataclay.serialization.lib.DeserializationLibUtils import deserialize_association, PersistentLoadPicklerHelper
from dataclay.serialization.lib.SerializationLibUtils import serialize_association, PersistentIdPicklerHelper
from dataclay.serialization.python.lang.BooleanWrapper import BooleanWrapper
from dataclay.serialization.python.lang.StringWrapper import StringWrapper
from dataclay.serialization.python.util.PyTypeWildcardWrapper import PyTypeWildcardWrapper
from dataclay.util.management.classmgr.UserType import UserType

# Publicly show the dataClay method decorators
__author__ = 'Alex Barcelo <alex.barcelo@bsc.es>'
__copyright__ = '2016 Barcelona Supercomputing Center (BSC-CNS)'

logger = getLogger(__name__)


def _get_object_by_id_helper(object_id):
    """Helper method which can be pickled and used by DataClayObject.__reduce__"""
    return getRuntime().get_object_by_id(object_id)


class DataClayObject(object):
    """Main class for Persistent Objects.

    Objects that has to be made persistent should derive this class (either
    directly, through the StorageObject alias, or through a derived class).
    """

    __metaclass__ = ExecutionGateway

    # Extradata of the object. Private field.
    __dclay_instance_extradata = None
    
    def initialize_object(self, new_object_id=None):
        """ 
        @postcondition: Initialize the object 
        @param new_object_id: Object Id of the object
        """        
        if new_object_id is not None:  # TODO: remove this if once ExecutionGateway is not initializing object id twice
            self.set_object_id(new_object_id)
        getRuntime().add_to_heap(self)
        
        # TODO: improve this using an specialization (dgasull) 
        if getRuntime().is_exec_env(): 
            self.set_persistent(True)  # All objects are persistent
            self.set_hint(getRuntime().get_hint())
            self.set_owner_session_id(getRuntime().get_session_id())
            self.initialize_object_as_volatile()
    
    def initialize_object_as_persistent(self):
        """
        @postcondition: object is initialized as a persistent object.
        Flags for "persistent" state might be different in EE and client.
        """
        # TODO: improve this using an specialization (dgasull) 
        if getRuntime().is_exec_env(): 
            # *** Execution Environment flags
            self.set_persistent(True)

            # by default, loaded = true for volatiles created inside executions
            # this function (initialize as persistent) is used for objects being
            # deserialized and therefore they might be unloaded
            # same happens for pending to register flag.
            self.set_loaded(False)
            self.set_pending_to_register(False)
            
        else: 
            # *** Client flags
            self.set_persistent(True)

    def initialize_object_as_volatile(self):
        """
        @postcondition: Initialize object with state 'volatile' with proper flags. Usually, volatile state is created by a stub, app, exec
        class,.. See same function in DataClayExecutionObject for a different initialization. This design is intended to be
        clear with object state.
        """
        # TODO: improve this using an specialization (dgasull) 
        if getRuntime().is_exec_env(): 
            # *** Execution Environment flags
            self.set_loaded(True)
            self.set_pending_to_register(True)
    
    def get_location(self):
        """Return a single (random) location of this object."""
        return getRuntime().get_execution_environment_by_oid(self.__dclay_instance_extradata.object_id)

    def get_master_location(self):
        """Return the uuid relative to the master location of this object."""
        return self.__dclay_instance_extradata.master_location

    def set_master_location(self, eeid):
        """Set the master location of this object."""
        if not isinstance(eeid, UUID):
            raise AttributeError('The master location should be the ExecutionEnvironment\'s id')
        self.__dclay_instance_extradata.master_location = eeid

    def get_all_locations(self):
        """Return all the locations of this object."""
        return getRuntime().get_all_execution_environments_by_oid(self.__dclay_instance_extradata.object_id)
    
    def new_replica(self, backend_id, recursive=True):
        getRuntime().new_replica(self.get_object_id(), backend_id, recursive)

    def new_version(self, backend_id):
        return getRuntime().new_version(self.get_object_id(), backend_id)

    def consolidate_version(self, version_info):
        getRuntime().consolidate_version(version_info)

    def make_persistent(self, alias=None, backend_id=None, recursive=True):
        getRuntime().make_persistent(self, alias=alias, backend_id=backend_id, recursive=recursive)

    def get_execution_environments_info(self):
        return getRuntime().get_execution_environments_info()

    def get_object_id(self):
        """
        @postcondition: Return object id of the object
        @return Object id
        """
        return self.__dclay_instance_extradata.object_id
    
    def set_object_id(self, new_object_id):
        """
        @postcondition: Set object id of the object
        @param new_object_id: object id
        """
        self.__dclay_instance_extradata.object_id = new_object_id

    def get_dataset_id(self):
        """
        @postcondition: Return dataset id of the object 
        @return Data set id
        """
        return self.__dclay_instance_extradata.dataset_id
    
    def set_dataset_id(self, new_dataset_id):
        """
        @postcondition: Set dataset id of the object
        @param new_dataset_id: dataset id
        """
        self.__dclay_instance_extradata.dataset_id = new_dataset_id

    def getID(self):
        """Return the string representation of the persistent object.

        dataClay specific implementation: The objects are internally represented
        through ObjectID, which are UUID. This method returns the UUID as a
        string.
        """
        return str(self.__dclay_instance_extradata.object_id)

    @classmethod
    def get_object_by_id(cls, object_id):
        return getRuntime().get_object_by_id(object_id)

    @classmethod
    def get_by_alias(cls, alias):
        return getRuntime().get_by_alias(cls, alias)

    @classmethod
    def delete_alias(cls, alias):
        return getRuntime().delete_alias(cls, alias)

    def set_persistent(self, ispersistent):
        """
        @postcondition: Set value of persistent flag in the object
        @param ispersistent: value to set
        """
        self.__dclay_instance_extradata.persistent_flag = ispersistent

    def set_loaded(self, isloaded):
        """
        @postcondition: Set value of loaded flag in the object
        @param isloaded: value to set
        """
        logger.verbose("Setting loaded to `%s` for object %r" % (isloaded, self))
        self.__dclay_instance_extradata.loaded_flag = isloaded

    def is_persistent(self):
        """
        @postcondition: Return TRUE if object is persistent. FALSE otherwise. 
        @return is persistent flag
        """
        return self.__dclay_instance_extradata.persistent_flag

    def is_loaded(self):
        """
        @postcondition: Return TRUE if object is loaded. FALSE otherwise. 
        @return is loaded flag
        """
        return self.__dclay_instance_extradata.loaded_flag
    
    def get_owner_session_id(self):
        """
        @postcondition: Get owner session id
        @return Owner session id
        """
        return self.__dclay_instance_extradata.owner_session_id
    
    def set_owner_session_id(self, the_owner_session_id):
        """
        @postcondition: Set ID of session of the owner of the object. 
        @param the_owner_session_id: owner session id 
        """ 
        self.__dclay_instance_extradata.owner_session_id = the_owner_session_id
    
    def is_pending_to_register(self):
        """
        @postcondition: Return TRUE if object is pending to register. FALSE otherwise. 
        @return is pending to register flag
        """
        return self.__dclay_instance_extradata.pending_to_register_flag
    
    def set_pending_to_register(self, pending_to_register):
        """
        @postcondition: Set pending to register flag. 
        @param pending_to_register: The flag to set
        """
        self.__dclay_instance_extradata.pending_to_register_flag = pending_to_register
    
    def is_dirty(self):
        """
        @postcondition: Return TRUE if object is dirty (it was modified). FALSE otherwise. 
        @return dirty flag
        """
        return self.__dclay_instance_extradata.dirty_flag
    
    def set_dirty(self, dirty_value):
        """
        @postcondition: Set dirty flag. 
        @param dirty_value: The flag to set
        """
        self.__dclay_instance_extradata.dirty_flag = dirty_value
    
    def get_hint(self):
        """
        @postcondition: Get hint
        @return Hint
        """
        return self.__dclay_instance_extradata.execenv_id
    
    def set_hint(self, new_hint):
        """
        @postcondition: Set hint
        @param new_hint: value to set
        """
        self.__dclay_instance_extradata.execenv_id = new_hint
            
    @classmethod
    def get_class_extradata(cls):
        return ExecutionGateway.get_class_extradata(cls)

    def run_remote(self, backend_id, operation_name, value):
        return getRuntime().run_remote(self.get_object_id(), backend_id, operation_name, value)

    def serialize(self, io_file, ignore_user_types, iface_bitmaps,
                  cur_serialized_objs, pending_objs):

        # Put slow debugging info inside here:
        """
        NOTE: new implementation of ExecutionGateway assert is not needed and wrong
        if logger.isEnabledFor(DEBUG):
        #    klass = self.__class__
        #    logger.debug("Serializing instance %r from class %s",
        #                 self, klass.__name__)
        #    logger.debug("The previous class is from module %s, in file %s",
        #                 klass.__module__, inspect.getfile(klass))
            # logger.debug("The class extradata is:\n%s", klass._dclay_class_extradata)
        #    assert klass._dclay_class_extradata == self._dclay_class_extradata
        """
        if hasattr(self, "__dclay_serialize__"):
            # The object has a user-defined serialization method.
            dco_extradata = self.__dclay_instance_extradata
            last_flag = dco_extradata.loaded_flag
            dco_extradata.loaded_flag = True

            # Use pickle to the result of the serialization
            import cPickle as pickle
            state = pickle.dumps(self.__dclay_serialize__())

            # Leave the previous value, probably False
            dco_extradata.loaded_flag = last_flag

            StringWrapper(mode="binary").write(io_file, state)

        else:
            # Regular dataClay provided serialization
            # Get the list of properties, making sure it is sorted
            properties = sorted(
                self.get_class_extradata().properties.values(),
                key=attrgetter('position'))

            logger.verbose("Serializing list of properties: %s", properties)

            for p in properties:

                try:
                    value = object.__getattribute__(self, "%s%s" % (DCLAY_PROPERTY_PREFIX, p.name))
                except AttributeError:
                    value = None
                
                logger.verbose("Serializing property %s with value %s " % (p.name, value))

                if value is None:
                    BooleanWrapper().write(io_file, False)
                else:
                    BooleanWrapper().write(io_file, True)
                    if isinstance(p.type, UserType) and not ignore_user_types:
                        serialize_association(io_file, value, cur_serialized_objs, pending_objs)
                    else:
                        pck = Pickler(io_file)
                        pck.persistent_id = PersistentIdPicklerHelper(cur_serialized_objs, pending_objs)
                        pck.dump(value)

    def deserialize(self, io_file, iface_bitmaps,
                    metadata,
                    cur_deserialized_python_objs):
        """Reciprocal to serialize."""

        # Put slow debugging info inside here:
        #
        # NOTE: new implementation of ExecutionGateway assert is not needed and wrong
        # if logger.isEnabledFor(DEBUG):
        #     klass = self.__class__
        #     logger.debug("Deserializing instance %r from class %s",
        #                  self, klass.__name__)
        #     logger.debug("The previous class is from module %s, in file %s",
        #                  klass.__module__, inspect.getfile(klass))
        #     logger.debug("The class extradata is:\n%s", klass._dclay_class_extradata)
        #     assert klass._dclay_class_extradata == self._dclay_class_extradata
        #
        # LOADED FLAG = TRUE only once deserialization is finished to avoid concurrent problems!
        # # This may be due to race conditions. It may need to do some extra locking
        # if self.__dclay_instance_extradata.loaded_flag:
        #     logger.debug("Loaded Flag is True")
        # else:
        #     self.__dclay_instance_extradata.loaded_flag = True

        if hasattr(self, "__dclay_deserialize__"):
            # The object has a user-defined deserialization method.

            # Use pickle, and use that method instead
            import cPickle as pickle
            state = pickle.loads(StringWrapper(mode="binary").read(io_file))
            self.__dclay_deserialize__(state)

        else:
            # Regular dataClay provided deserialization

            # Start by getting the properties
            properties = sorted(
                self.get_class_extradata().properties.values(),
                key=attrgetter('position'))
            
            logger.trace("Tell io_file before loop: %s", io_file.tell())
            logger.verbose("Deserializing list of properties: %s", properties)

            for p in properties:
                
                logger.trace("Tell io_file in loop: %s", io_file.tell())
                not_null = BooleanWrapper().read(io_file)
                value = None
                if not_null:
                    logger.debug("Not null property %s", p.name)
                    if isinstance(p.type, UserType):
                        try:
                            logger.debug("Property %s is an association", p.name)
                            value = deserialize_association(io_file, iface_bitmaps, metadata, cur_deserialized_python_objs, getRuntime())
                        except KeyError as e:
                            logger.error('Failed to deserialize association', exc_info=True)
                    else:
                        upck = Unpickler(io_file)
                        upck.persistent_load = PersistentLoadPicklerHelper(
                            metadata, cur_deserialized_python_objs, getRuntime())
                        value = upck.load()

                logger.debug("Setting value %s for property %s", value, p.name)

                object.__setattr__(self, "%s%s" % (DCLAY_PROPERTY_PREFIX, p.name), value)

    def __reduce__(self):
        """Support for pickle protocol.

        Take into account that internal Pickle usage should be used with help
        of PersistentIdPicklerHelper and PersistentLoadPicklerHelper --for
        further information on the inner working look at the modules
        [Des|S]erializationLibUtils and both the serialize and deserialize
        methods of this class.

        This method is left here as a courtesy to end users that may need or
        want to Pickle DataClayObjects manually or through other extensions.
        """
        logger.info("Proceeding to `__reduce__` (Pickle-related) on a DataClayObject")
        dco_extradata = self.__dclay_instance_extradata

        if not dco_extradata.persistent_flag:
            # FIXME: Support for volatile means that this is not acceptable.
            # FIXME: But right now, this is a sensible default (specially for Tiramisu)
            logger.warning("Trying to pickle a non-persistent object. Unsupported. Making it persistent")
            self.make_persistent()

        return _get_object_by_id_helper, (self.get_object_id(),)  # this last argument must be a tuple

    def __repr__(self):
        dco_extradata = self.__dclay_instance_extradata
        dcc_extradata = self.get_class_extradata()

        if dco_extradata.persistent_flag:
            return "<%s (ClassID=%s) instance with ObjectID=%s>" % \
                   (dcc_extradata.classname, dcc_extradata.class_id, dco_extradata.object_id)
        else:
            return "<%s (ClassID=%s) volatile instance with ObjectID=%s>" % \
                   (dcc_extradata.classname, dcc_extradata.class_id, dco_extradata.object_id)

    def __eq__(self, other):
        if not isinstance(other, DataClayObject):
            return False

        self_extradata = self.__dclay_instance_extradata
        other_extradata = other.__dclay_instance_extradata

        if not self_extradata.persistent_flag or not other_extradata.persistent_flag:
            return False

        return self_extradata.object_id and other_extradata.object_id \
            and self_extradata.object_id == other_extradata.object_id

    @dclayMethod(obj='anything', property_name='str', value='anything', beforeUpdate='str', afterUpdate='str')
    def __setUpdate__(self, obj, property_name, value, beforeUpdate, afterUpdate):
        if beforeUpdate is not None:
            getattr(self, beforeUpdate)(property_name, value)
        object.__setattr__(obj, "%s%s" % ("_dataclay_property_", property_name), value)
        if afterUpdate is not None:
            getattr(self, afterUpdate)(property_name, value)
