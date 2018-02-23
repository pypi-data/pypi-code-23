from abc import ABCMeta, abstractmethod
from .observer import Observer
from hdv_logging import simple
from hdv_dummy import Dummy
from setuptools.dist import sequence
from hdv_handyman import utils

MODULE_TYPE_MODULE = 'modules'
MODULE_TYPE_FILTER = 'filters'
MODULE_TYPE_VALIDATOR = 'validators'
MODULE_TYPE_HANDLER = 'handlers'
MODULE_TYPE_HOOK= 'hooks'
MODEUL_TYPE_MANAGER_HOOK = 'managerhook'
MODEUL_TYPE_MODULE_HOOK = 'modulehook'

HOOK_RUN_BEFORE = 'before'
HOOK_RUN_AFTER = 'after'

HOOK_MANAGER_METHOD = 'manager'
HOOK_MODULE_METHOD = 'module'

TIMELOG_NAME_FOR_MANGER = 'manager'
TIMELOG_NAME_FOR_MODULE = 'module'


# HOOK_RUN_WITH_MANAGER = 'startmanager'
# HOOK_RUN_END_MANAGER = 'aftermanager'
# 
# HOOK_RUN_BEFORE_LOOP = 'beforeloop'
# HOOK_RUN_AFTER_LOOP = 'afterloop'


WAIT = 'wait'
EXIT = 'exit'
SKIP = 'skip' 

class ManagerException(Exception):
    pass

class Run():
    
    def __init__(self, main_module):
        
        self.main_module = main_module
        self.run()
        
    def run(self):
        
        print(self.main_module)
        
    

class ModuleBase(metaclass=ABCMeta):
    
    __modulename__ = None
    __moduletype__ = MODULE_TYPE_MODULE
    __master__ = False
    
    @abstractmethod
    def get(self, *args, **kargs):
        pass
    
    @abstractmethod
    def put(self, *args, **kargs):
        pass
    
    @abstractmethod
    def post(self, *args, **kargs):
        pass
    
    @abstractmethod
    def delete(self, *args, **kargs):
        pass
    
    def catchall(self, *args, **kargs):
        
        return None
    
    def setModuleManger(self, manager):
        
        self.manager = manager
        #to save return result
        self._result = None
        return self
    
class SimpleModuleBase(ModuleBase):
    
    def get(self, *args, **kargs):
        pass
    
    def put(self, *args, **kargs):
        pass
    
    def post(self, *args, **kargs):
        pass
    
    def delete(self, *args, **kargs):
        pass
    
class CatchAllModuleBase(SimpleModuleBase):
    
    @abstractmethod
    def catchall(self, *args, **kargs):
        pass
    
class HookBase(metaclass=ABCMeta):
    
    def __init__(self, method=None, module=None, modules=[], methods=[], when=[]):
        
        self.modules = modules if module is None else [module]
        self.methods = methods if methods is None else [method]
        self.when = when if type(when) is type([]) else [when]
        
    @abstractmethod
    def run(self, module, method, when, obj, result):
        pass
    
class ManagerHookBase(HookBase):
    
    def __init__(self, when=[]):
        
        super().__init__(module=MODEUL_TYPE_MANAGER_HOOK, method=HOOK_MANAGER_METHOD , when=when)
        
    
class ModuleHookBase(HookBase):
    
    def __init__(self, when=[]):
        
        super().__init__(module=MODEUL_TYPE_MODULE_HOOK, method=HOOK_MODULE_METHOD, when=when)
    
class SingleIOBase(ModuleBase):

    def insert(self, *args, **kargs):
        pass
    
    def update(self, *args, **kargs):
        pass
    
    def delete(self, *args, **kargs):
        pass
    
    def setInput(self, input):
        self.input = input
    
class FilterBase(SingleIOBase):
    
    __moduletype__ = MODULE_TYPE_FILTER
    pass

class ValidatorBase(SingleIOBase):
    
    __moduletype__ = MODULE_TYPE_VALIDATOR
    pass

class HandlerBase(SingleIOBase):
    
    __moduletype__ = MODULE_TYPE_HANDLER
    pass

class ModuleManagerException(Exception):
    pass

class ContainerBase(Observer):
    pass

#class ModuleStorage(Observer):
class ModuleStorage():
    
    def __init__(self, manager):
        
        self.manager = manager
        
class ModuleContainer(ContainerBase):
    
    def __getattribute__(self, name):
    
        try:
            if name == super(ModuleContainer, self).__getattribute__('mastername'):
                self.manager.logger.debug('Returning attribute "{}" from master'.format(name))
                return super(ModuleContainer, self).__getattribute__('master')
        except AttributeError:
            pass
        
        try:
            module = super(ModuleContainer, self).__getattribute__('container')[name]
            self.manager.logger.debug('Returning attribute "{}" from container'.format(name))
            return module
        except KeyError:
            pass
        except AttributeError:
            pass
        
        return super(ContainerBase, self).__getattribute__(name)  
    
    def __init__(self, manager):
        
        self.manager = manager
        self.container = {}
        self.master = None
        self.mastername = None

class HookContainer(Observer):
    
    def __init__(self, manager):
        
        self.manager = manager
        self.container = {}
        
class CurrentInfo():
    
    def __init__(self, manager):
        
        self.manager = manager
        self.current_method = None
        self.module_sequence = []
        self.current_index = 0
        self.run_args = {}
        
    def __createSequence(self):
        
        if self.module_sequence:
            return
                
        if self.manager.modules.master and not self.run_args['bypass_master']:
            self.module_sequence.append(self.manager.modules.mastername)
            
        if self.run_args['sequence']:
            self.module_sequence += list(self.run_args['sequence'])
            return
        
        for n in self.manager.modules.container.keys():
            
            if self.run_args['only']:
                if n in self.run_args['only']:
                    self.module_sequence.append(n)
                    
            elif self.run_args['exclude']:
                if n not in self.run_args['exclude']:
                    self.module_sequence.append(n)
                
            else:
                self.module_sequence.append(n)
            
        return
        
    def next(self):
        
        self.__createSequence()
        
        index =  self.current_index + 1
        if index < len(self.module_sequence):
            self.current_index = index
        
    def getNext(self):
        
        self.__createSequence()
        
        index = self.current_index + 1
        
        if len(self.module_sequence) <= index:
            return None
        
        return self.module_sequence[index]
    
    def getPrevious(self):
        
        self.__createSequence()
        
        if self.current_index == 0:
            return None
        
        return self.module_sequence[self.current_index - 1]
        
    
    def getCurrent(self):
        
        self.__createSequence()

        return self.module_sequence[self.current_index]
    
    def getMethod(self):
        
        return self.current_method
    
class TimeLogException(Exception):
    pass

class TimeLog():
    
    def __init__(self, start=None, end=None):
        
        self.start = start
        self.end = end
        if start is None:
            self.start = utils.microtime(True)
        
    def finish(self, end=None):
        
        self.end = end
        if end is None:
            self.end = utils.microtime(True)
    
    def getTime(self):
        
        if not all((self.start, self.end)):
            raise TimeLogException('start and end cannot be empty')
        
        return self.end - self.start
    
class Action():
    
    def __init__(self, method, sequence=(), exclude=(), only=(), bypass_master=False, get_return_values_from=(), output=None, is_for_waitting=False, **kargs):  
        
        self.method = method
        self.sequence = sequence
        self.exclude = exclude
        self.only = only
        self.bypass_master = bypass_master
        self.get_return_values_from = get_return_values_from
        self.output = output
        self.is_for_waitting = is_for_waitting
        self.kargs = kargs

class ModuleManager():
    
    def __init__(self, storage=ModuleStorage, module_container=ModuleContainer, hook_container=HookContainer, logger_kargs={}, echo=False):
        
        self.modules = module_container(self)
        self.hooks = hook_container(self)
        self.storage = storage(self)
        self.storage._timelog = {}
        self.workplace = None
        self.logger = self.__setupLogger(echo, **logger_kargs)
        self.current = CurrentInfo(self)
        #self.manager_hook_done = [0,0]
        self.manager_ended = False
        self.end_has_called = False
        self.actions = []
        self.waittings = []
        
    def __setupLogger(self, echo, **kargs):
        
        if echo is False:
            return Dummy()
        
        return simple(**kargs)
        
    def setWorkplace(self, workplace):
        
        self.workplace = workplace
        
    def end(self):
        
        self.manager_ended = True
        self.__runHooks(MODEUL_TYPE_MANAGER_HOOK, HOOK_MANAGER_METHOD, HOOK_RUN_AFTER, self, None)
        self.manager_hook_done[1] = 1
        self.end_has_called = True
        
    
    def addModule(self, module):
        
        if not isinstance(module, ModuleBase):
            raise ModuleManagerException('module must be a instance of ModuleBase')
        
        if module.__modulename__ is None:
            raise ModuleManagerException('modulename cannot be empty')
        
        module_instance = module.setModuleManger(self)
        
        if module.__master__ is True:
            self.logger.debug('Adding module "{}" as master'.format(module.__modulename__))
            if self.modules.master is not None:
                raise ModuleManagerException('Master module already assinged')
            
            self.modules.master = module_instance
            self.modules.mastername = module.__modulename__
            return True
        
        try:
            self.modules.container[module.__modulename__]
            if module.__modulename__ in self.modules.container:
                self.logger.debug('Module "{}" is already exist'.format(module.__modulename__))
        except KeyError:
            self.logger.debug('Adding module "{}"'.format(module.__modulename__))
            self.modules.container[module.__modulename__] = module_instance
            
        return True
    
    def __runModule(self, method, module, **kargs):
        
        self.__runHooks(module.__modulename__, method, HOOK_RUN_BEFORE, module, None)
        
        if  hasattr(module, method) and callable(getattr(module, method)):
            module_instance = getattr(module, method)
            result = module_instance(**kargs)
        else:
            self.logger.debug('Method "{}" not found from module "{}"'.format(method, module.__modulename__))
            module_instance = getattr(module, 'catchall')
            result = module_instance(**kargs)
    
#         print('called {}'.format(module.__modulename__))
#         print(self.current.__dict__)
        module._result = result
        self.current.next()
        self.logger.debug('Current module "{}" has been executed. Previous module was "{}" and next moulde will be "{}"'.format(self.current.getCurrent(), self.current.getPrevious(), self.current.getNext()))
        
        if result in (WAIT, SKIP, EXIT):
            return result
        
        return result
    
    def run(self):
        
        self.storage._timelog[TIMELOG_NAME_FOR_MANGER] = TimeLog()
        self.__runHooks(MODEUL_TYPE_MANAGER_HOOK, HOOK_MANAGER_METHOD, HOOK_RUN_BEFORE, self, None)
        
        for a in self.actions:
            
            self.storage._timelog[MODEUL_TYPE_MODULE_HOOK] = {}
            self.storage._timelog[MODEUL_TYPE_MODULE_HOOK][a.method] = TimeLog()
            self.__runHooks(MODEUL_TYPE_MODULE_HOOK, HOOK_MODULE_METHOD, HOOK_RUN_BEFORE, self, None, current_running_method=a.method)
            
            self._run(
                method=a.method,
                sequence=a.sequence,
                exclude=a.exclude,
                only=a.only,
                bypass_master=a.bypass_master,
                get_return_values_from=a.get_return_values_from,
                output=a.output,
                is_for_waitting=a.is_for_waitting,
                **a.kargs
                )
            
            self.storage._timelog[MODEUL_TYPE_MODULE_HOOK][a.method].finish()
            self.__runHooks(MODEUL_TYPE_MODULE_HOOK, HOOK_MODULE_METHOD, HOOK_RUN_AFTER, self, None, current_running_method=a.method)
            
        #reset actions
        self.actions = []    
        
        self.storage._timelog[TIMELOG_NAME_FOR_MANGER].finish()
        self.__runHooks(MODEUL_TYPE_MANAGER_HOOK, HOOK_MANAGER_METHOD, HOOK_RUN_AFTER, self, None)
        
        return self
            
    def _run(self, method, sequence=(), exclude=(), only=(), bypass_master=False, get_return_values_from=(), output=None, is_for_waitting=False, **kargs):
        
        #have to reset module_sequence if new moude has added.
        self.current.module_sequence = []
        self.current.run_args = locals()
        self.current.current_method = method
        self.current.current_index = 0
        
        output = output if output else {}
        has_waitting = False
        
        #clean up waitting list
        if not is_for_waitting:
            self.waittings = []
        
        #master first
        if any([is_for_waitting, bypass_master]) is False and self.modules.master is not None:
            self.logger.debug('Running master module')
            result = self.__runModule(method, self.modules.master, **kargs)
            
            if result is WAIT:
                raise ModuleManagerException('Master module cannot reutrns wait')
            
            output[self.modules.mastername] = result;
#             result = getattr(self.modules.master, method)(**kargs)
#             
#             if result is WAIT:
#                 raise ModuleManagerException('Master module cannot reutrns wait')
#             
#             output[self.modules.mastername] = self.__runHooks(self.modules.mastername, method, HOOK_RUN_AFTER, self.modules.master, result)
        
        if sequence:
            moduels = {}
            for s in sequence:
                moduels[s] = self.modules.container[s]
            moduels = moduels.items()
        else:
            moduels = self.modules.container.items()
        
        for name, obj in moduels:
            if name in exclude:
                continue
            
            if only and name not in only:
                self.logger.debug('{} is not in only list... skip to next module'.format(name))
                continue
            
#             try :
#                 candidate = getattr(obj, method)
#             except(AttributeError):
#                 continue
            
            result = None
            #self.__runHooks(name, method, HOOK_RUN_BEFORE, obj, result)
            self.logger.debug('Running module: "{}" method: "{}"'.format(name, method))
            #result = candidate(**kargs)
            result = self.__runModule(method, obj, **kargs)
            
            if result is EXIT:
                self.logger.debug('Exit for module: "{}" method: "{}"'.format(name, method))
                return output
            if result is SKIP:
                self.logger.debug('Skipping for module: "{}" method: "{}"'.format(name, method))
                continue
            
            if result is WAIT:
                has_waitting = True
                
            if result is WAIT and not is_for_waitting:
                self.logger.debug('Adding to waittings "{}"'.format(name))
                self.waittings.append(name)
                has_waitting = True
                
            if is_for_waitting and result is not WAIT:
                self.logger.debug('Waitting list has total {} moduels'.format(len(self.waittings)))
                self.logger.debug('Deleting {} from waittings '.format(name))
                self.waittings.remove(name)
                
            #result = self.__runHooks(name, method, HOOK_RUN_AFTER, obj, result)
            
            if name in get_return_values_from:
                output[name] = result
            if "*" in get_return_values_from:
                output[name] = result
        
        if has_waitting or len(self.waittings) > 0:
            self.runWaitting(method, output)
        else:
            #clean up saved result
            self.__cleanUpSavedResult()
            return output
        
    def performAction(self, method, sequence=(), exclude=(), only=(), bypass_master=False, get_return_values_from=(), output=None, is_for_waitting=False, **kargs):  
        
        self.actions.append(
            Action(
                method=method, 
                sequence=sequence, 
                exclude=exclude, 
                only=only, 
                bypass_master=bypass_master, 
                get_return_values_from=get_return_values_from, 
                output=output, 
                is_for_waitting=is_for_waitting, 
                **kargs)
        )
    
    def __cleanUpSavedResult(self):
        
        self.modules.master._result = None
         
        for n, o in self.modules.container.items():
            o._result = None
        
        
    def runWaitting(self, method, output):
        
        if len(self.waittings) is 0:
            self.logger.debug('No module found on waitting list')
            return False
        
        self.logger.debug('Running runAll(...) from runWaitting')
        self.run(method, only=list(self.waittings), is_for_waitting=True , output=output)
            
    def runOne(self, name, method, **kargs):
        
        result = self.__runModule(method, self.getModule(name), **kargs)
        return result

    def addHook(self, hook):
        
        if not isinstance(hook, HookBase):
            raise ModuleManagerException('hook must be a instance of HookBase')
        
        for module in hook.modules:
            try:
                self.hooks.container[module]
            except KeyError:
                self.hooks.container[module] = {}
                 
            for method in hook.methods:
                try:
                    self.hooks.container[module][method]
                except KeyError:
                    self.hooks.container[module][method] = {}
                 
                for when in hook.when:
                    try:
                        self.hooks.container[module][method][when]
                    except KeyError:
                        self.hooks.container[module][method][when] = []
                     
                    #now add hook
                    self.logger.debug('Hook has been added to module : "{}" method : "{}"  when : "{}"'.format(module, method, when))
                    self.hooks.container[module][method][when].append(hook)
        

    def __runHooks(self, module, method, when, obj, result, current_running_module=None, current_running_method=None):
        
        try:
            self.logger.debug('Looking hooks for moduel : "{}" method : "{}"  when : "{}". Now returning '.format(module, method, when))
            hooks = self.hooks.container[module][method][when]
        except KeyError:
            return result
        
        output = None
        hook_found = False
        for h in hooks:
            hook_found = True
            method = current_running_method if current_running_method is not None else method
            module if current_running_module is not None else module
            output = getattr(h, 'run')(module, method, when, obj, result)
        
        self.logger.debug('Hook is returning to run for moduel : "{}" method : "{}"  when : "{}". Now returning '.format(module, method, when))
        return output if hook_found else result
        
    def getModule(self, name):
        
        return getattr(self.modules, name)
    
    def ___getattribute__(self, name):
        
        try:
            return self.modules[name]
        except KeyError:
            return super(ModuleManager, self).__getattribute__(name)
        
    
    def __del__(self):
        
        try:
            self.hooks.container['managerhook']['manager']['after']
        except KeyError:
            return
        
        if not self.end_has_called:
            #raise ManagerException('Found manager hook but no end method has called')
            pass
            
    