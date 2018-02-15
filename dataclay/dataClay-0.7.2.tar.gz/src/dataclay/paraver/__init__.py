"""Paraver related trace generation.

All the Paraver-files (.prv) generation is done through decorators and
mechanisms defined in this module. There are also capabilities for merge and
checks on the generated prv files.

Additionally, this module defines an application capable of performing several
Paraver-related routines, like "merge".
"""
import atexit
import types
from Queue import Queue, Full
from functools import wraps
import logging
import thread
from threading import Lock
import time

from . import prv_traces


__author__ = 'Alex Barcelo <alex.barcelo@bsc.es>'
__copyright__ = '2015 Barcelona Supercomputing Center (BSC-CNS)'

logger = logging.getLogger(__name__)

pyextrae_event = None

QUEUE_MAXSIZE = 1000

# Used by pyextrae (COMPSs integration)
TASK_EVENTS = 8000010
PROCESS_CREATION = 100

# Explicit and manually crafted list (there may be functions which are not here)
FUNCS_WITH_PARAVER_DECORATORS = [
    # managers.management
    "prepare_stubs",
    "load_babel_data",
    "deploy_stubs",
    "track_local_available_classes",

    # api init & finish
    "init",
    "finish",

    # Storage API calls
    "getByID",
    "initWorker",
    "finishWorker",

    # LogicModuleGrpcClient "LMClient":
    'LMClient.new_enrichment',
    'LMClient.import_contract',
    'LMClient.get_namespace_id',
    'LMClient.get_storage_location_id',
    'LMClient.make_persistent',
    'LMClient.register_listener_persisted_object_with_class_name',
    'LMClient.get_contractids_of_applicant_with_provider',
    'LMClient.get_object_dataset_id',
    'LMClient.move_objects',
    'LMClient.register_to_public_contract',
    'LMClient.new_class_id',
    'LMClient.new_class',
    'LMClient.remove_dataset',
    'LMClient.new_interface',
    'LMClient.delete_alias',
    'LMClient.register_objects_from_ds_garbage_collector',
    'LMClient.new_dataset',
    'LMClient.get_contract_id_of_dataclay_provider',
    'LMClient.get_class_name_for_ds',
    'LMClient.get_executionenvironmentid_for_ds',
    'LMClient.get_info_of_classes_in_namespace',
    'LMClient.set_dataset_id',
    'LMClient.set_dataset_id_from_garbage_collector',
    'LMClient.close_manager_db',
    'LMClient.get_datacontractids_of_provider',
    'LMClient.new_version',
    'LMClient.get_operation_id',
    'LMClient.get_storage_locationid_for_ds',
    'LMClient.get_executionenvironment_for_ds',
    'LMClient.update_refs',
    'LMClient.remove_interface',
    'LMClient.get_interface_info',
    'LMClient.lm_autoregister_ds',
    'LMClient.set_object_read_only',
    'LMClient.execute_method_on_target',
    'LMClient.new_data_contract',
    'LMClient.execute_implementation',
    'LMClient.get_execution_environments_per_locations_for_ds',
    'LMClient.get_property_id',
    'LMClient.register_listener_deleted_object_with_class_name',
    'LMClient.get_contractids_of_applicant',
    'LMClient.get_imported_classes_info_in_namespace',
    'LMClient.remove_implementation',
    'LMClient.get_datacontract_info_of_applicant_with_provider',
    'LMClient.get_stubs',
    'LMClient.get_execution_environments_info',
    'LMClient.get_object_from_alias',
    'LMClient.get_execution_environment_id',
    'LMClient.set_object_read_write',
    'LMClient.get_contractids_of_provider',
    'LMClient.get_datacontractids_of_applicant',
    'LMClient.get_storage_locations_info',
    'LMClient.get_execution_environments_per_locations',
    'LMClient.import_interface',
    'LMClient.activate_tracing',
    'LMClient.get_execution_environment_info',
    'LMClient.new_contract',
    'LMClient.clean_metadata_caches',
    'LMClient.new_namespace',
    'LMClient.close',
    'LMClient.get_object_info',
    'LMClient.get_storage_location_for_ds',
    'LMClient.register_listener_deleted_object_with_object_id',
    'LMClient.get_class_id',
    'LMClient.get_babel_stubs',
    'LMClient.deactivate_tracing',
    'LMClient.get_storage_location_info',
    'LMClient.remove_class',
    'LMClient.get_account_list',
    'LMClient.get_info_of_session_for_ds',
    'LMClient.get_implementationids_that_meet_req',
    'LMClient.get_metadata_by_oid',
    'LMClient.new_session',
    'LMClient.get_class_name_and_namespace_for_ds',
    'LMClient.create_paraver_traces',
    'LMClient.perform_set_of_operations',
    'LMClient.remove_namespace',
    'LMClient.get_dataset_id',
    'LMClient.new_account',
    'LMClient.close_session',
    'LMClient.perform_set_of_new_accounts',
    'LMClient.register_event_listener_implementation',
    'LMClient.close_db',
    'LMClient.consolidate_version',
    'LMClient.delete_persistent',
    'LMClient.get_class_info',
    'LMClient.get_classid_from_import',
    'LMClient.wait_and_process_async_req',
    'LMClient.register_objects',
    'LMClient.get_account_id',
    'LMClient.register_to_public_datacontract',
    'LMClient.remove_operation',
    'LMClient.get_classname_and_namespace_for_ds',
    'LMClient.advise_event',
    'LMClient.register_listener_persisted_object_with_object_id',
    'LMClient.new_replica',
    'LMClient.get_storage_locations_per_execution_environments',
    'LMClient.get_objects_metadata_info_of_class_for_nm',

    # ExecutionEnvGrpcClient "EEClient":
    'EEClient.ds_execute_implementation',
    'EEClient.ds_new_version',
    'EEClient.ds_consolidate_version',
    'EEClient.ds_new_metadata',
    'EEClient.close',
    'EEClient.ds_deploy_metaclasses',
    'EEClient.ds_get_objects',
    'EEClient.ds_store_objects',
    'EEClient.ds_migrate_objects_to_backends',
    'EEClient.ds_upsert_objects',
    'EEClient.ds_remove_objects',
    'EEClient.ds_new_replica',
    'EEClient.ds_new_persistent_instance',
    'EEClient.ds_move_objects',
]

PARAVER_FUNC_MAP = {name: i for i, name in enumerate(FUNCS_WITH_PARAVER_DECORATORS, 500)}

UNKNOWN_METHODS = list()


class PrvManager(object):
    """A Paraver Manager is associated to a single output .prv file.

    A single PrvManager should be instantiated for each process. Keep that in
    mind when using multiprocessing features.

    When the instance has already been instantiated, the classmethod get_manager
    returns the instance.
    """
    prv_instance = None

    def __new__(cls, *args):
        """Initialize the static value of prv_instance with the new instance.

        Caution! This constructor will statically overwrite a prior instance of
        PrvManager. It is ok for subprocesses to instantiate their own manager,
        but only with different PID (see also __init__).
        """
        ret = super(PrvManager, cls).__new__(cls, *args)
        cls.prv_instance = ret

        # This is something very slow which should be done during initialization
        # and not during tracing.
        try:
            from pyextrae.common import extrae
            logger.info("Using pyextrae.common for tracing information")
            global pyextrae_event
            pyextrae_event = extrae.event

            # Override the dummy method with one that actually traces something
            cls._add_extrae_trace = cls._add_extrae_trace_activated
        except ImportError:
            logger.info("Not using pyextrae (ImportError, ignoring)")

        return ret

    def __init__(self, output_name):
        """Initialize the internal Queue and Mutex, and output the synchronization line.

        :param output_base_name: The file path base for the trace output. The
        initialization will add -<pid>.prv to it.

        Caution! Never instantiate a PrvManager more than once in the same
        subprocess --it will silently overwrite the output file.
        """
        self.dump_mutex = Lock()
        self.tracing_queue = Queue(QUEUE_MAXSIZE)
        self.output_name = output_name
        with open(self.output_name, 'w') as f:
            f.write("5:{:d}:{:d}\n".format(int(time.time() * 1000),
                                           int(time.clock() * 1000000)))

        atexit.register(self._dump, force=True)

    @classmethod
    def get_manager(cls):
        """Get the interpreter-wide manager.
        :rtype : PrvManager
        :return: The PrvManager instance to be used.
        """
        return cls.prv_instance

    def close(self):
        """Flush the tracing queue and close everything."""
        logger.debug("Closing PrvManager with output_name: %s", self.output_name)
        self._dump(force=True)

    def _dump(self, force=False):
        flag = self.dump_mutex.acquire(force)

        if flag:
            with open(self.output_name, 'a') as f:
                f.write(self.format_line(
                    (0, thread.get_ident(), int(time.clock() * 1000000),
                     "1:py.PrvManager.DUMP")
                ))

                while not self.tracing_queue.empty():
                    f.write(self.format_line(self.tracing_queue.get_nowait()))

                f.write(self.format_line(
                    (0, thread.get_ident(), int(time.clock() * 1000000),
                     "0:py.PrvManager.DUMP")
                ))
        else:
            # Wait for the ongoing dump, but the job here is done, no retry
            self.dump_mutex.acquire()

        self.dump_mutex.release()

    def _add_trace(self, prv_id, time_ns, extra):
        """Add an entry to the internal trace Queue, and dump if needed.

        See documentation of Paraver files for more information.
        """
        success = False

        while not success:
            try:
                self.tracing_queue.put((prv_id, thread.get_ident(), time_ns, extra), block=False)
            except Full:
                logger.debug("Queue full, dumping to %s", self.output_name)
                self._dump()
            else:
                success = True

    def add_function_trace(self, enter, full_name, prv_value):
        """Trace entry: Function (enter or exit).

        :param enter: Boolean to signal whether it is entering or exiting the method.
        :param full_name: Hierarchical name of the function.
        :param prv_value: Numerical identifier for PyCOMPSs-compliant Paraver tracing.
        """
        self._add_extrae_trace(enter, prv_value)
        self._add_trace(prv_traces.TraceType.METHOD.value, int(time.clock() * 1000000),
                        "{:d}:{}".format(1 if enter else 0, full_name))

    def _add_extrae_trace(self, enter, prv_value):
        """Dummy do-nothing method, which is used when lack of pyextrae."""
        pass

    def _add_extrae_trace_activated(self, enter, prv_value):
        """The real implementation of _add_extrae_trace (which uses pyextrae)"""
        assert pyextrae_event is not None, \
            "Check the initialization logic, because pyextrae_event " \
            "cannot be `None` while extrae tracing is activated"
        if enter:
            pyextrae_event(TASK_EVENTS, 0)
            pyextrae_event(TASK_EVENTS, prv_value)
        else:
            pyextrae_event(TASK_EVENTS, 0)

    def add_network_send(self, network_type, send_port, request_id, dest_host_ip, message_size, method_id):
        """Trace a certain network send (can be a SEND_REQUEST or a SEND_RESPONSE)."""
        if not _is_network_tracing_enabled():
            return
        self._add_trace(network_type.value, int(time.clock() * 1000000),
                        "{:d}:{:d}:{}:{:d}:{:d}".format(
                            send_port, request_id, dest_host_ip, message_size, method_id))

    def add_network_receive(self, origin_host_ip, origin_host_port, request_id, method_id):
        """Trace a certain network receive (a RESPONSE)."""
        if not _is_network_tracing_enabled():
            return
        self._add_trace(prv_traces.TraceType.RECEIVE.value, int(time.clock() * 1000000),
                        "{}:{:d}:{:d}:{:d}".format(
                            origin_host_ip, origin_host_port, request_id, method_id))

    @classmethod
    def format_line(cls, tuple_info):
        """Return the formatted string from a certain tracing information.

        :param tuple_info: A tuple containing required values for paraver tracing entry
        (three numbers and a string)
        :return: The formatted string
        """
        return "{:d}:{:d}:{:d}:{}\n".format(*tuple_info)


def _is_tracing_enabled(module_name):
    """Check if a certain submodule is to-be-traced.

    :param module_name: The name of the module in which the function/method is.
    :return: True if it should be traced, false otherwise.
    """
    # TODO check something (properties, file, etc.) and return a valid boolean
    # Dummy implementation, always trace
    return True


def _is_network_tracing_enabled():
    """Check if network calls tracing is enabled (globally for all calls).

    :return: True if it should be traced, false otherwise.
    """
    # TODO check something (properties, file, etc.) and return a valid boolean
    # Dummy implementation, always trace
    return True


def trace_method(func):
    """Decorator for class methods that may be traced."""
    if not _is_tracing_enabled(func.__module__):
        return func

    try:
        prv_value = PARAVER_FUNC_MAP[func.func_name]
    except KeyError:
        logger.warning("Method `%s` (in module %s, unknown class) "
                       "is not correctly registered for Paraver",
                       func.func_name, func.__module__)
        prv_value = 999

    @wraps(func)
    def func_wrapper(self, *args, **kwargs):
        full_name = "py.{}.{}".format(self.__class__.__name__,
                                      func.func_name)

        prv = PrvManager.get_manager()
        prv.add_function_trace(True, full_name, prv_value)
        # Proceed to the method call
        try:
            ret = func(self, *args, **kwargs)
        finally:
            prv.add_function_trace(False, full_name, prv_value)
        return ret

    return func_wrapper


def _trace_method_in_class(klass, func):
    """Decorator for methods in a class, when class is known."""
    try:
        prv_value = PARAVER_FUNC_MAP["%s.%s" % (klass.__name__, func.__name__)]
    except KeyError:
        logger.warning("Method `%s` (class %s, module %s) "
                       "is not correctly registered for Paraver",
                       func.__name__, klass.__name__, func.__module__)
        prv_value = 999

    @wraps(func)
    def func_wrapper(self, *args, **kwargs):
        full_name = "py.{}.{}".format(klass.__name__,
                                      func.__name__)

        prv = PrvManager.get_manager()
        prv.add_function_trace(True, full_name, prv_value)
        # Proceed to the method call
        try:
            ret = func(self, *args, **kwargs)
        finally:
            prv.add_function_trace(False, full_name, prv_value)
        return ret

    return func_wrapper


def trace_function(func):
    """Decorator for functions (not methods) that may be traced."""
    if not _is_tracing_enabled(func.__module__):
        return func

    try:
        prv_value = PARAVER_FUNC_MAP[func.func_name]
    except KeyError:
        logger.warning("Function `%s` (in module %s) is not correctly registered for Paraver",
                       func.func_name, func.__module__)
        prv_value = 999

    @wraps(func)
    def func_wrapper(*args, **kwargs):
        full_name = "py.{}.{}".format(func.__module__, func.func_name)

        prv = PrvManager.get_manager()
        prv.add_function_trace(True, full_name, prv_value)
        # Proceed to the function call
        try:
            ret = func(*args, **kwargs)
        finally:
            prv.add_function_trace(False, full_name, prv_value)
        return ret

    return func_wrapper


def trace_all_public_methods(klass):
    """Decorator for a class, trace all its public methods.

    Given a certain class (decorated through usual approach) "instrumentate"
    all its public methods to yield paraver information.

    Note that all non-underscore-starting methods are considered public. Take
    that in mind while programming your class. You can also explicitly avoid
    tracing a certain method by doing the following:

        def public_method_not_traced(self, ...):
            ...
        public_method_not_traced.do_not_trace = True

    :param klass: The class that will be "instrumented".
    :return: The same class, but with its methods instrumented.
    """

    if not _is_tracing_enabled(klass.__module__):
        return klass

    for name, obj in klass.__dict__.items():
        if name.startswith("_"):
            continue

        if isinstance(obj, types.FunctionType):  # @abarcelo doesn't understand why UnboundMethodType wasn't working
            if getattr(obj, "do_not_trace", False):
                # The user explicitly defined "do_not_trace" flag here
                continue

            setattr(klass, name, _trace_method_in_class(klass, obj))

    return klass


def pcf_dataclay_addendum():
    logger.info("EVENT_TYPE")
    logger.info("0    %d    dataClay events", TASK_EVENTS)
    logger.info("VALUES")
    logger.info("0      End") 
    for name, value in PARAVER_FUNC_MAP.items():
        logger.info("%d %s", value, name) 


def compss_dataclay_addendum():
    return ((value, name) for name, value in PARAVER_FUNC_MAP.items())
