"""Management of Python Classes.

This module is responsible of management of the Class Objects. A central Python
Metaclass is responsible of Class (not object) instantiation.

Note that this managers also includes most serialization/deserialization code
related to classes and function call parameters.
"""
from decorator import getfullargspec
import inspect
from logging import getLogger
import re
import uuid

from dataclay.DataClayObjectExtraData import DataClayInstanceExtraData, DataClayClassExtraData
from dataclay.commonruntime.Runtime import getRuntime
from dataclay.commonruntime.RuntimeType import RuntimeType
from dataclay.exceptions.exceptions import ImproperlyConfigured
from dataclay.util.management.classmgr.MetaClass import MetaClass
from dataclay.util.management.classmgr.Operation import Operation
from dataclay.util.management.classmgr.Property import Property
from dataclay.util.management.classmgr.Type import Type
from dataclay.util.management.classmgr.Utils import STATIC_ATTRIBUTE_FOR_EXTERNAL_INIT
from dataclay.util.management.classmgr.python.PythonClassInfo import PythonClassInfo
from dataclay.util.management.classmgr.python.PythonImplementation import PythonImplementation
from dataclay.DataClayObjProperties import DynamicProperty, ReplicatedDynamicProperty, PreprocessedProperty
from dataclay.util.StubUtils import load_babel_data
from dataclay.util.classloaders.ClassLoader import load_metaclass
from dataclay.exceptions.exceptions import DataclayException

# Publicly show the dataClay method decorators
__author__ = 'Alex Barcelo <alex.barcelo@bsc.es>'
__copyright__ = '2016 Barcelona Supercomputing Center (BSC-CNS)'

logger = getLogger(__name__)

# For efficiency purposes compile the folowing regular expressions:
# (they return a tuple of two elements)
re_property = re.compile(r"(?:^\s*@dclayReplication\s*\(\s*(before|after)Update\s*=\s*'([^']+)'(?:,\s(before|after)Update='([^']+)')?(?:,\sinMaster='(True|False)')?\s*\)\n)?^\s*@ClassField\s+([\w.]+)[ \t]+([\w.\[\]<> ,]+)", re.MULTILINE)
re_import = re.compile(r"^\s*@dclayImport(?P<from_mode>From)?\s+(?P<import>.+)$", re.MULTILINE)

# Populated by ExecutionGateway, can be freely accessed and cleared (see MetaClassFactory)
loaded_classes = set()

# Class extradata caches
class_extradata_cache_exec_env = dict()
class_extradata_cache_client = dict()


class ExecutionGateway(type):
    """Python' Metaclass dataClay "magic"

    This type-derived Metaclass is used by DataClayObject to control the class
    instantiation and also object instances.
    """

    def __new__(cls, classname, bases, dct):

        if classname == 'DataClayObject':
            # Trivial implementation, do nothing
            return super(ExecutionGateway, cls).__new__(cls, classname, bases, dct)
        # at this point, a real dataClay class is on-the-go
        klass = super(ExecutionGateway, cls).__new__(cls, classname, bases, dct)
        loaded_classes.add(klass)
        return klass

    def __init__(cls, name, bases, dct):
        logger.verbose("Initialization of class %s in module %s",
                    name, cls.__module__)

        super(ExecutionGateway, cls).__init__(name, bases, dct)

    def __call__(self, *args, **kwargs):
        
        if getattr(self, STATIC_ATTRIBUTE_FOR_EXTERNAL_INIT, False):
            logger.debug("New Persistent Instance (remote init) of class `%s`", self.__name__)
            return getRuntime().new_persistent_instance_aux(self, args, kwargs)
        else:
            ret = object.__new__(self)  # this defers the __call__ method
            logger.debug("New regular dataClay instance of class `%s`", self.__name__)
            self._populate_internal_fields(ret)
            self.__init__(ret, *args, **kwargs)

            # FIXME this should read "make_volatile" because the object is not "persistent"
            """ WARNING: IF YOU UNCOMMENT THIS, TELL DGASULL WHY!! """
            """
            if getRuntime().current_type == RuntimeType.exe_env:
                logger.verbose("Making the recently created object persistent (in fact, it should be volatile for now)")
                getRuntime().make_persistent(ret, None, None, True)
            """
            return ret

    @staticmethod
    def get_class_extradata(klass):
        
        classname = klass.__name__
        module_name = klass.__module__
        full_name = "%s.%s" % (module_name, classname)
        
        """
        Check if class extradata is in cache. 
        """
        dc_ced = None
        if getRuntime().current_type == RuntimeType.client:
            dc_ced = class_extradata_cache_client.get(full_name)
        else:
            dc_ced = class_extradata_cache_exec_env.get(full_name)
        
        if dc_ced is not None:
            return dc_ced
        
        logger.verbose('Proceeding to prepare the class `%s` from the ExecutionGateway',
                       full_name)
        logger.debug("The RuntimeType is: %s",
                     "client" if getRuntime().current_type == RuntimeType.client else "not client")

        dc_ced = DataClayClassExtraData(
            full_name=full_name,
            classname=classname,
            namespace=module_name.split('.', 1)[0],
            properties=dict(),
            imports=list(),
        )

        if getRuntime().current_type == RuntimeType.client:
            class_stubinfo = None

            try:
                all_classes = load_babel_data()

                for c in all_classes:
                    if "%s.%s" % (c.namespace, c.className) == full_name:
                        class_stubinfo = c
                        break
            except ImproperlyConfigured:
                pass

            if class_stubinfo is None:
                # Either ImproperlyConfigured (not initialized) or class not found:
                # assuming non-registered class

                # Prepare properties from the docstring
                doc = klass.__doc__  # If no documentation, consider an empty string
                if doc is None:
                    doc = ""
                property_pos = 0

                for m in re_property.finditer(doc):
                    # declaration in the form [ 'before|after', 'method', 'before|after', 'method', 'name', 'type' ]
                    declaration = m.groups()
                    prop_name = declaration[-2]
                    prop_type = declaration[-1]

                    beforeUpdate = declaration [1] if declaration [0] == 'before' else declaration [3] if declaration [2] == 'before' else None

                    afterUpdate = declaration [1] if declaration [0] == 'after' else declaration [3] if declaration [2] == 'after' else None

                    inMaster = declaration[4] == 'True'

                    current_type = Type.build_from_docstring(prop_type)

                    logger.trace("Property `%s` (with type signature `%s`) ready to go",
                                 prop_name, current_type.signature)

                    dc_ced.properties[prop_name] = PreprocessedProperty(name=prop_name, position=property_pos, type=current_type, beforeUpdate=beforeUpdate, afterUpdate=afterUpdate, inMaster=inMaster)

                    # Keep the position tracking (required for other languages compatibility)
                    property_pos += 1

                    # Prepare the `property` magic --this one without getter and setter ids
                    # dct[prop_name] = DynamicProperty(prop_name)
                    setattr(klass, prop_name, DynamicProperty(prop_name))

                for m in re_import.finditer(doc):
                    gd = m.groupdict()

                    if gd["from_mode"]:
                        import_str = "from %s\n" % gd["import"]
                    else:
                        import_str = "import %s\n" % gd["import"]

                    dc_ced.imports.append(import_str)

            else:
                logger.debug("Loading a class with babel_data information")

                dc_ced.class_id = class_stubinfo.classID
                dc_ced.stub_info = class_stubinfo

                # WIP WORK IN PROGRESS (because all that is for the ancient StubInfo, not the new one)

                # Prepare the `property` magic --in addition to prepare the properties dictionary too
                for i, prop_name in enumerate(dc_ced.stub_info.propertyListWithNulls):

                    if prop_name is None:
                        continue

                    prop_info = class_stubinfo.properties[prop_name]
                    if prop_info.beforeUpdate is not None or prop_info.afterUpdate is not None:
                        setattr(klass, prop_name, ReplicatedDynamicProperty(prop_name, prop_info.beforeUpdate, prop_info.afterUpdate, prop_info.inMaster))

                    else:
                        # dct[prop_name] = DynamicProperty(prop_name)
                        setattr(klass, prop_name, DynamicProperty(prop_name))

                    dc_ced.properties[prop_name] = PreprocessedProperty(name=prop_name, position=i, type=prop_info.propertyType, beforeUpdate=prop_info.beforeUpdate, afterUpdate=prop_info.afterUpdate, inMaster=prop_info.inMaster)

        elif getRuntime().current_type == RuntimeType.exe_env:
            logger.verbose("Seems that we are a DataService, proceeding to load class %s",
                           dc_ced.full_name)
            namespace_in_classname, dclay_classname = dc_ced.full_name.split(".", 1)
            if namespace_in_classname != dc_ced.namespace:
                raise DataclayException("Namespace in ClassName: %s is different from one in ClassExtraData: %s", namespace_in_classname, dc_ced.namespace) 
            mc = load_metaclass(dc_ced.namespace, dclay_classname)
            dc_ced.metaclass_container = mc
            dc_ced.class_id = mc.dataClayID

            # Prepare the `property` magic --in addition to prepare the properties dictionary too
            for p in dc_ced.metaclass_container.properties:
                
                # dct[p.name] = DynamicProperty(p.name)
                setattr(klass, p.name, DynamicProperty(p.name))

                dc_ced.properties[p.name] = PreprocessedProperty(
                    name=p.name, position=p.position, type=p.type, beforeUpdate=p.beforeUpdate, afterUpdate=p.afterUpdate, inMaster=p.inMaster)
        else:
            raise RuntimeError("Could not recognize RuntimeType %s", getRuntime().current_type)

        """
        Update class extradata cache. 
        """
        if getRuntime().current_type == RuntimeType.client:
            class_extradata_cache_client[full_name] = dc_ced
        else:
            class_extradata_cache_exec_env[full_name] = dc_ced

        return dc_ced

    def new_dataclay_instance(self, **kwargs):
        """Return a new instance, without calling to the class methods."""
        logger.debug("New dataClay instance (without __call__) of class `%s`", self.__name__)
        ret = object.__new__(self)  # this defers the __call__ method
        self._populate_internal_fields(ret, **kwargs)
        return ret

    @staticmethod
    def _populate_internal_fields(instance, **kwargs):
        from dataclay.DataClayObject import DataClayObject
        if not isinstance(instance, DataClayObject):
            raise DataclayException("Population of fields is assumed to be done onto a DataClayObject")

        logger.debug("Populating internal fields for the class. Provided kwargs: %s", kwargs)

        # Mix default values with the provided ones through kwargs
        fields = {
            "persistent_flag": False,
            "object_id": uuid.uuid4(),
            "dataset_id": None,
            "loaded_flag": True,
            "pending_to_register_flag": False,
            "dirty_flag": False
        }
        fields.update(kwargs)

        # Store some extradata in the class
        instance_dict = object.__getattribute__(instance, "__dict__")
        instance_dict["_DataClayObject__dclay_instance_extradata"] = DataClayInstanceExtraData(**fields)
        
        """
        TODO: get_class_extradata function is adding DynamicProperties to class (not to instance!) so it is needed 
        to be called. Please, use a better function for that. 
        """
        instance_dict["_dclay_class_extradata"] = ExecutionGateway.get_class_extradata(instance.__class__)
        
        """ object here is volatile. """
        instance.initialize_object()

        return instance

    def _prepare_metaclass(self, namespace, responsible_account):
        """Build a dataClay "MetaClass" for this class.

        :param str namespace: The namespace for this class' MetaClass.
        :param str responsible_account: Responsible account's username.
        :return: A MetaClass Container.
        """
        try:
            class_extradata = ExecutionGateway.get_class_extradata(self)
        except AttributeError:
            raise ValueError("MetaClass can only be prepared for correctly initialized DataClay Classes")

        logger.verbose("Preparing MetaClass container for class %s (%s)",
                    class_extradata.classname, class_extradata.full_name)

        # The thing we are being asked (this method will keep populating it)
        current_python_info = PythonClassInfo(
            imports=list()
        )
        current_class = MetaClass(
            namespace=namespace,
            name=class_extradata.full_name,
            parentType=None,
            operations=list(),
            properties=list(),
            isAbstract=False,
            languageDepInfos={'LANG_PYTHON': current_python_info}
        )

        ####################################################################
        # OPERATIONS
        ####################################################################
        for name, dataclay_func in inspect.getmembers(self, inspect.ismethod):
            # Consider only functions with _dclay_method
            if not getattr(dataclay_func, "_dclay_method", False):
                logger.verbose("Method `%s` doesn't have attribute `_dclay_method`",
                             dataclay_func)
                continue

            original_func = dataclay_func._dclay_entrypoint
            logger.debug("MetaClass container will contain method `%s`, preparing", name)

            # Skeleton for the operation
            current_operation = Operation(
                namespace=namespace,
                className=class_extradata.full_name,
                descriptor=name,  # FIXME this is *not* correct at all!
                signature=name,  # FIXME this is *not* correct at all!
                name=name,
                nameAndDescriptor=name,  # FIXME this is *not* correct at all!
                params=dict(),
                paramOrder=list(),
                returnType=Type.build_from_type(dataclay_func._dclay_ret),
                implementations=list(),
                isAbstract=False,
                isStaticConstructor=False)

            # Start with parameters
            #########################

            # The actual order should be retrieved from the signature
            signature = getfullargspec(original_func)
            if signature.varargs or signature.varkw:
                raise NotImplementedError("No support for varargs or varkw yet")

            current_operation.paramOrder[:] = signature.args[1:]  # hop over 'self'
            current_operation.params.update({k: Type.build_from_type(v)
                                             for k, v in dataclay_func._dclay_args.iteritems()})

            if len(current_operation.paramOrder) != len(current_operation.params):
                raise DataclayException("All the arguments are expected to be annotated, " \
                    "there is some error in %s::%s|%s" \
                    % (namespace, class_extradata.full_name, name)) 

            # Follow by implementation
            ############################

            current_implementation = PythonImplementation(
                responsibleAccountName=responsible_account,
                namespace=namespace,
                className=class_extradata.full_name,
                opNameAndDescriptor=name,  # FIXME
                position=0,
                includes=list(),
                accessedProperties=list(),
                accessedImplementations=list(),
                requiredQuantitativeFeatures=dict(),
                requiredQualitativeFeatures=dict(),
                code=inspect.getsource(dataclay_func._dclay_entrypoint))

            current_operation.implementations.append(current_implementation)

            # Finally, add the built operation container into the class
            #############################################################
            current_class.operations.append(current_operation)

        ####################################################################
        # PROPERTIES
        ####################################################################
        for n, p in class_extradata.properties.iteritems():
            current_property = Property(
                namespace=namespace,
                className=class_extradata.full_name,
                name=n,
                position=p.position,
                type=p.type,
                beforeUpdate=p.beforeUpdate,
                afterUpdate=p.afterUpdate,
                inMaster=p.inMaster)

            current_class.properties.append(current_property)

        ####################################################################
        # IMPORTS
        ####################################################################
        current_python_info.imports.extend(class_extradata.imports)

        return current_class
