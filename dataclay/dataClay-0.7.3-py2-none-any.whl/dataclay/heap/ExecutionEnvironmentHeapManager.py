'''
Created on 26 ene. 2018

@author: dgasull
'''
from dataclay.heap.HeapManager import HeapManager
from threading import Timer
from dataclay.heap.MemoryUtils import datasize, memory, resident, peaksize, textsize
import time
from dataclay.serialization.lib.SerializationLibUtils import serialize_for_db_gc
from dataclay.DataClayObjProperties import DCLAY_PROPERTY_PREFIX
import gc
import psutil
import pprint
import sys

""" Percentage to start flushing objects """
GC_MEMORY_PRESSURE_PERCENT = 75.0


class ExecutionEnvironmentHeapManager(HeapManager):

    """
    @summary: This class is intended to manage all dataClay objects in EE runtime's memory.
    """

    """ During a flush of all objects in Heap, if GC is being processed, wait, and check after time specified here in seconds """
    TIME_WAIT_FOR_GC_TO_FINISH = 1
    
    """ Execution Environment being managed """
    exec_env = None 
    
    # Retained objects so they cannot be GC by PythonGC.
    # It is very important to be a sorted list, so first elements to arrive are cleaned before,
    # n any deserialization from DB or parameter, objects deserialized first are referrers to
    # objects deserialized later. Second ones cannot be GC if first ones are not cleaned.
    # During GC,we should know that somehow. It's a hint but improves GC a lot.
    # Also, remember list must be thread-safe:
    # Lists themselves are thread-safe. In CPython the GIL protects against concurrent accesses to them
    retained_objects = list()

    # Store also the ObjectID, because it is the fastest way to check if a certain object
    # is there (we cannot rely on __eq__ operations on user-defined classes.
    retained_objects_id = set()
    
    """ Indicates if HeapManager is flushing all objects in Heap to disk. """
    is_flushing_all = False 
    
    """ Indicates if HeapManager is processing GC"""
    is_processing_gc = False

    def __init__(self, theruntime):
        """
        @postcondition: Constructor of the object 
        @param theruntime: Runtime being managed 
        """ 
        HeapManager.__init__(self, theruntime)  
        self.exec_env = theruntime.get_execution_environment()
        self.logger.debug("EE HEAP MANAGER created for EE %s" % self.exec_env.ee_name)

    def add_to_heap(self, dc_object):
        """
        @postcondition: the object is added to dataClay's heap
        @param dc_object: object to add to the heap 
        """
        HeapManager._add_to_inmemory_map(self, dc_object)
        self.retain_in_heap(dc_object)
        # self.logger.debug("[==GC==] Added to heap object %s with address %s " % (dc_object.get_object_id(), str(id(dc_object))))

    def retain_in_heap(self, dc_object):
        """
        @postcondition: Add a new Hard reference to the object provided. All code in stubs/exec classes using objects in dataClayheap are
        using weak references. In order to avoid objects to be GC without a flush in DB, HeapManager has hard-references to
        them and is the only one able to release them. This function creates the hard-reference.
        @param dc_object: Object to retain. 
        """ 
        if dc_object.get_object_id() not in self.retained_objects_id:
            self.retained_objects_id.add(dc_object.get_object_id())
            self.retained_objects.append(dc_object)

    def release_from_heap(self, dc_obj):
        """ 
        @postcondition: Release hard reference to object provided. Without hard reference, the object can be Garbage collected
        @param dc_obj: object to release
        """
        self.logger.debug("[==GC==] Releasing object with id %s from retained map. " % (dc_obj.get_object_id()))
        try:
            self.retained_objects_id.remove(dc_obj.get_object_id())
            self.retained_objects.remove(dc_obj)        
        except Exception as e:
            self.logger.debug("[==GC==] ERROR Releasing object with id %s " % (dc_obj.get_object_id()))
    
    def __check_memory_pressure(self):
        """
        @postcondition: Check if memory is under pressure 
        @return TRUE if memory is under pressure. FALSE otherwise. 
        """
        """ 
        Memory management in Python involves a private heap containing all Python objects and data structures. 
        The management of this private heap is ensured internally by the Python memory manager. 
        The Python memory manager has different components which deal with various dynamic storage management aspects, 
        like sharing, segmentation, preallocation or caching.
        """
        virtual_mem = psutil.virtual_memory()
        self.logger.debug("[==GC==] Memory: %s" % str(virtual_mem))
        return float(virtual_mem.percent) > GC_MEMORY_PRESSURE_PERCENT
    
    def __nullify_object(self, dc_object):
        """
        @postcondition: Set all fields to none to allow GC action 
        """ 
        
        metaclass = dc_object.get_class_extradata()
        self.logger.debug("[==GC==] Going to clean object %s" % dc_object.get_object_id())
        for prop_name in metaclass.properties.keys():
            self.logger.debug("[==GC==] Setting %s%s to None for object %s" % (DCLAY_PROPERTY_PREFIX, prop_name, dc_object.__dict__))
            object.__setattr__(dc_object, "%s%s" % (DCLAY_PROPERTY_PREFIX, prop_name), None)

    def __clean_object(self, dc_object):
        """
        @postcondition: Clean object (except if not loaded or being used). Cleaning means set all fields to None to allow
        GC to work.
        @param dc_object: Object to clean.
        """
        
        """
        Lock object (not locking executions!)
        Lock is needed in case object is being nullified and some threads requires to load it from disk.
        """
        object_id = dc_object.get_object_id()
        self.runtime.lock(object_id)
        try:
            
            is_loaded = dc_object.is_loaded()
            if not is_loaded: 
                self.logger.debug("[==GC==] Not collecting since not loaded.")
                return
            
            if dc_object.is_dirty() or dc_object.is_pending_to_register(): 
                # Update it 
                self.logger.debug("[==GC==] Updating object %s " % dc_object.get_object_id())
                self.gc_collect_internal(dc_object)
            
            self.logger.debug("[==GC==] Cleaning object %s" % str(dc_object))
            
            """ Set loaded flag to false, any current execution that wants to get/set a field must try to load
            object from DB, and lock will control that object is not being cleaned """
            dc_object.set_loaded(False) 
            
            self.__nullify_object(dc_object)
            
            """ Object is not dirty anymore """
            dc_object.set_dirty(False)
            
            """
            VERY IMPORTANT (RACE CONDITION)
            If some object was cleaned and removed from GC retained refs, it does NOT mean it was removed
            from Weak references Heap because we will ONLY remove an entry in that Heap if the GC removed it.
            So, if some execution is requested after we remove an entry from retained refs (we cleaned and send
            the object to disk), we check if the
            object is in Heap (see executeImplementation as an example) and therefore, we created a new reference
            making impossible for GC to clean the reference. We will add the object to retained refs
            again once it is deserialized from DB. See DeserializationLib. It's the best solution without Lockers 
            in get and remove in Heap.

            Remove it from Retained refs to allow GC action.
            """
            self.release_from_heap(dc_object)

        finally:
            self.runtime.unlock(object_id)

    def gc_collect_internal(self, object_to_update):
        """
        @postcondition: Update object in db or store it if volatile (and register in LM)
        @param object_to_update: object to update
        """
        if object_to_update.is_loaded() and object_to_update.is_persistent():
                self.logger.debug("[==GCUpdate==] Updating object %s" % object_to_update.get_object_id())
                """ Call EE update """ 
                obj_bytes = serialize_for_db_gc(object_to_update, False, None)
                if object_to_update.is_pending_to_register():
                    self.logger.debug("[==GCUpdate==] Pending to register in LM ")
                    self.exec_env.register_and_store_pending(object_to_update, obj_bytes, True)
                elif object_to_update.is_dirty():
                    self.logger.debug("[==GCUpdate==] Updated object %s " % object_to_update.get_object_id())
                    self.runtime.ready_clients["@STORAGE"].update_to_db(object_to_update.get_object_id(), obj_bytes)
                    
                    """ TODO: set datasetid for GC if set by user """

    def run_task(self): 
        """
        @postcondition: Check Python VM's memory pressure and clean if necessary. Cleaning means flushing objects, setting 
        all fields to none (to allow GC to work better) and remove from retained references. If volatile or pending to register,
        we remove it once registered.
        """
        if self.is_flushing_all or self.is_processing_gc:
            self.logger.debug("[==GC==] Not running since is being processed or flush all is being done")
            return 
        # No race condition possible here since there is a time interval for run_gc that MUST be > than time spend to check 
        # flag and set to True. Should we do it atomically? 
        self.is_processing_gc = True
        self.logger.debug("[==GC==] Running GC")

        self.exec_env.prepareThread()
        is_pressure = self.__check_memory_pressure()
        if is_pressure:
                
            """
            cur_frame = sys._getframe(0)
            self.logger.debug("[==GC==] Is enabled? %s" % str(gc.isenabled()))
            self.logger.debug("[==GC==] Is retained objects tracked? %s" % str(gc.is_tracked(self.retained_objects)))
            self.logger.debug("[==GC==] Inmemory map %s" % str(id(HeapManager.get_heap(self))))
            self.logger.debug("[==GC==] Retained map %s" % str(id(self.retained_objects)))
            self.logger.debug("[==GC==] Threshold: %s" % str(gc.get_threshold()))
            self.logger.debug("[==GC==] Count: %s" % str(gc.get_count()))
            self.logger.debug("[==GC==] Current frame ID: %s" % str(id(cur_frame)))
            """
            
            """ Use a while in order to be able to modify list while iterating and allow GC action """
            index = 0
            while index < len(self.retained_objects):      
                           
                dc_obj = self.retained_objects[index]     
                
                """ 
                self.logger.debug("[==GC==] Object address in memory: %s" % str(id(dc_obj)))
                self.logger.debug("[==GC==] Is tracked? %s" % str(gc.is_tracked(dc_obj)))
                for r in gc.get_referents(dc_obj):
                    if r == self.retained_objects:
                        self.logger.debug("[==GC==] REFERENT BEFORE CLEAN FOR %s is retained map. " % (dc_obj.get_object_id()))
                    elif r == HeapManager.get_heap(self):
                        self.logger.debug("[==GC==] REFERENT BEFORE CLEAN FOR %s is inmemory map. " % (dc_obj.get_object_id())) 
                    else:
                        self.logger.debug("[==GC==] REFERENT BEFORE CLEAN FOR %s is: %s " % (dc_obj.get_object_id(), str(id(r))))
                        # self.logger.debug("[==GC==] REFERENT BEFORE CLEAN FOR %s is: %s " % (dc_obj.get_object_id(), pprint.pformat(r)))
                for r in gc.get_referrers(dc_obj):
                    if r == self.retained_objects:
                        self.logger.debug("[==GC==] REFERRER BEFORE CLEAN FOR %s is retained map. " % (dc_obj.get_object_id()))
                    elif r == HeapManager.get_heap(self):
                        self.logger.debug("[==GC==] REFERRER BEFORE CLEAN FOR %s is inmemory map. " % (dc_obj.get_object_id()))
                    else:
                        self.logger.debug("[==GC==] REFERRER BEFORE CLEAN FOR %s is: %s " % (dc_obj.get_object_id(), str(id(r))))
                        # self.logger.debug("[==GC==] REFERRER BEFORE CLEAN FOR %s is: %s " % (dc_obj.get_object_id(), pprint.pformat(r)))
                """
                self.__clean_object(dc_obj)
                """
                for r in gc.get_referents(dc_obj):
                    if r == self.retained_objects:
                        self.logger.debug("[==GC==] REFERENT FOR %s is retained map. " % (dc_obj.get_object_id()))
                    elif r == HeapManager.get_heap(self):
                        self.logger.debug("[==GC==] REFERENT FOR %s is inmemory map. " % (dc_obj.get_object_id()))
                    else:
                        self.logger.debug("[==GC==] REFERENT FOR %s is: %s " % (dc_obj.get_object_id(), str(id(r))))
                        # self.logger.debug("[==GC==] REFERENTS FOR %s is: %s " % (dc_obj.get_object_id(), pprint.pformat(r)))
                """
                """
                for r in gc.get_referrers(dc_obj):
                    if r == self.retained_objects:
                        self.logger.debug("[==GC==] REFERRER FOR %s is retained map. " % (dc_obj.get_object_id()))
                    elif r == HeapManager.get_heap(self):
                        self.logger.debug("[==GC==] REFERRER FOR %s is inmemory map. " % (dc_obj.get_object_id()))
                    else:
                        self.logger.debug("[==GC==] ID REFERRER FOR %s is: %s " % (dc_obj.get_object_id(), str(id(r))))
                        self.logger.debug("[==GC==] REFERRER FOR %s are: %s " % (dc_obj.get_object_id(), pprint.pformat(r)))
                """
                dc_obj = None  # Remove reference from Frame
                
                """
                Big heaps 
                """
                n = gc.collect()
                self.logger.debug("[==GC==] Collected %s" % str(n))
                self.logger.debug("[==GC==] Uncollectable: %s" % str(gc.garbage))
            
                # Check memory 
                is_pressure = self.__check_memory_pressure()
                if not is_pressure:
                    self.logger.debug("[==GC==] Not collecting since no pressure in memory")
                    break
                if self.is_flushing_all:
                    self.logger.debug("[==GC==] Interrupted due to flush all.")
                    break
                        # Force garbage-collection
                
                index = index + 1
        
        """
        For cyclic references 
        """
        n = gc.collect()
        self.logger.debug("[==GC==] Finally Collected %s" % str(n))
        self.logger.debug("[==GC==] Uncollectable: %s" % str(gc.garbage))
                       
        self.cleanReferencesAndLockers()
        self.is_processing_gc = False
        return
        
    def flush_all(self): 
        
        """
        @postcondition: Stores all objects in memory into disk. This function is usually called at shutdown of the 
        execution environment. 
        """
        # If there is another flush, return
        if self.is_flushing_all: 
            return 
        
        self.is_flushing_all = True
        
        """ If there is GC being processed, wait """ 
        while self.is_processing_gc: 
            time.sleep(self.TIME_WAIT_FOR_GC_TO_FINISH)
            
        self.logger.debug("[==FlushAll==] Number of objects in Heap: %s" % self.heap_size())
        for object_to_update in self.retained_objects:
            self.gc_collect_internal(object_to_update)
                
        return
