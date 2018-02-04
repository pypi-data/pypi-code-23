import logging, time, queue, tempfile, sys, os, datetime, traceback
import multiprocessing as mp
from collections import OrderedDict

class FailureException(Exception):
    pass

logger = logging.getLogger('par')

class ProcManager:

    inst = None #Singleton instance
    
    def __init__(self):
        from parproc.term import Term
        self.clear()
        self.term = Term()

    def clear(self):
        logger.debug('----------------CLEAR----------------------')
        self.parallel = 100
        self.procs = OrderedDict() #For consistent execution order
        self.protos = {}
        self.locks = {}
        self.context = {
            'logdir': tempfile.mkdtemp(prefix='parproc_{}_'.format(datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S-%f'))),
            'results': {}, #Context passed to processes
            'params': {}
        } 
        self.missingDeps = {}
        

    #Parallel: Number of parallel running processes
    def setOptions(self, parallel=None, dynamic=None):
        if parallel is not None:
            self.parallel = parallel
        if dynamic is not None:
            self.term.dynamic = dynamic

    def setParams(self, **params):
        for k,v in params.items():
            self.context['params'][k] = v
        
    @classmethod
    def getInst(cls):
        #Only make inst available in parent process
        if mp.current_process().name.startswith('parproc-child'):
            raise Exception('Use context when calling parproc from sub-process')
        
        if cls.inst is None:
            cls.inst = ProcManager()
            
        return cls.inst

    def addProc(self, p):
        logger.debug('ADD: "{}"'.format(p.name))
        if p.name in self.procs:
            raise Exception('Proc "{}" already created'.format(p.name))

        self.procs[p.name] = p

        if p.now or p.name in self.missingDeps:
            #Requested to run by script or dependent
            self.startProc(p.name)

    def addProto(self, p):
        logger.debug('ADD PROTO: "{}"'.format(p.name))
        if p.name in self.protos:
            raise Exception('Proto "{}" already created'.format(p.name))

        self.protos[p.name] = p

    def startProcs(self, names):
        for n in names:
            self.startProc(n)

    #Schedules a proc for execution
    def startProc(self, name):
        p = self.procs[name]

        if p.state == Proc.STATE_IDLE:
            logger.debug('SCHED: "{}"'.format(p.name))
            p.state = Proc.STATE_WANTED

            #Set dependencies as wanted or missing
            if not self.schedDeps(p): #If no unresolved or unfinished dependencies
                self.tryExecuteOne(p) #See if proc can be executed now

    #Create a proc from a proto
    def createProc(self, protoName, procName=None, args=None):
        proto = self.protos.get(protoName, None)
        if proto is None:
            raise Exception('Proto "{}" is undefined')

        if procName is not None and procName in self.procs:
            raise Exception('Proc name "{}" already in use')

        if procName is None:
            #Very simple way to find new procName.. Could be slow though
            i = 0
            while True:
                procName = protoName + ':' + str(i)
                if procName not in self.procs:
                    break
                i += 1

        #Proto args are defaults, but can be overridden by specified args
        procArgs = {}
        if proto.args:
            procArgs.update(proto.args)
        if args:
            procArgs.update(args)

        #Create proc based on prototype
        proc = Proc(name=procName, deps=proto.deps, locks=proto.locks, now=proto.now,
                    args=procArgs, proto=proto, timeout=proto.timeout)

        #Add new proc, by calling procs __call__ function
        proc(proto.func)

        #Return proc name as reference
        return procName

    #Schedule proc dependencies. Returns True if no new deps are found idle
    def schedDeps(self, proc):
        newDeps = False
        for d in proc.deps:
            if d in self.procs:
                if self.procs[d].state == Proc.STATE_IDLE:
                    self.procs[d].state = Proc.STATE_WANTED
                    newDeps = True

                    #Schedule dependencies of this proc
                    if not self.schedDeps(self.procs[d]):
                        #Try to kick off dependency
                        self.tryExecuteOne(self.procs[d], False)
                    
            else:
                #Dependency not yet known
                self.missingDeps[d] = True
                

    #Tries to execute any proc
    def tryExecuteAny(self):
        for name,p in self.procs.items():
            if p.state == Proc.STATE_WANTED:
                self.tryExecuteOne(p, False) #Do not go deeper while iterating


    #Executes proc now if possible. Returns false if not possible
    def tryExecuteOne(self, proc, collect=True):
        
        #If all dependencies are met, and none of the locks are taken, execute proc
        for l in proc.locks:
            if l in self.locks:
                logger.debug('Proc "{}" not started due to lock "{}"'.format(proc.name, l))
                return False

        for d in proc.deps:
            if d not in self.procs:
                logger.debug('Proc "{}" not started due to unknown dependency "{}"'.format(proc.name, d))
                return False
            elif self.procs[d].isFailed():
                logger.debug('Proc "{}" canceled due to failed dependency "{}"'.format(proc.name, d))
                proc.state = Proc.STATE_FAILED
                proc.error = Proc.ERROR_DEP_FAILED
                proc.moreInfo = 'canceled due to failure of "{}"'.format(self.procs[d].name)
                self.term.completedProc(proc)
                
            elif not self.procs[d].isComplete():
                logger.debug('Proc "{}" not started due to unfinished dependency "{}"'.format(proc.name, d))
                return False
        
        #If number of parallel processes limit has not been reached
        if sum(1 for name, p in self.procs.items() if p.isRunning()) >= self.parallel:
            logger.debug('Proc "{}" not started due to parallel process limit of {}'.format(proc.name, self.parallel))
            return        

        #All good. Execute process TODO: In a separate thread
        if proc.state == Proc.STATE_WANTED:
            self.execute(proc)
        else:
            logger.debug('Proc "{}" not started due to wrong state "{}"'.format(proc.name, proc.state))

        #Try execute other procs
        if collect:
            self.collect()


    def execute(self, proc):
        #Add context for specific process
        context = {'args': proc.args, **self.context}
        logger.info('Exec "{}" with context {}'.format(proc.name, context))

        #Queues for bidirectional communication
        proc.queueToProc = mp.Queue()
        proc.queueToMaster = mp.Queue()
        proc.state = Proc.STATE_RUNNING
        proc.startTime = time.time()

        #Set locks
        for l in proc.locks:
            self.locks[l] = proc
        
        #Kick off process
        self.term.startProc(proc)
        proc.process = mp.Process(target = proc.func, name='parproc-child-{}'.format(proc.name),
                                  args=(proc.queueToProc, proc.queueToMaster, context, proc.name))
        proc.process.start()


    #Finds any procs that have completed their execution, and moves them on. Tries to execute other
    #procs if any procs were collected
    def collect(self):
        foundAny = False
        for name in list(self.procs): 
            p = self.procs[name] #Might mutate procs list, so iterate pregenerated list
            if p.isRunning():
                #Try to get output
                try:
                    #logger.debug('collect: looking')
                    msg = p.queueToMaster.get_nowait()
                except queue.Empty: #Not done yet
                    #logger.debug('collect: empty')
                    pass
                else:
                    logger.debug('got msg from proc "{}": {}'.format(name, msg))
                    #Process sent us data
                    if msg['req'] == 'proc-complete':
                        #Process is done
                        #logger.debug('collect: done')
                        p.process = None
                        p.output = msg['value']
                        p.error = msg['error']
                        p.state = Proc.STATE_SUCCEEDED if p.error == Proc.ERROR_NONE else Proc.STATE_FAILED
                        
                        foundAny = True
                        p.logFilename = os.path.join(self.context['logdir'], name + '.log')

                        logger.info('proc "{}" collected: ret = {}'.format(p.name, p.output))

                        self.context['results'][p.name] = p.output
                        
                        logger.info('new context: {}'.format(self.context))
                    
                        #Release locks
                        for l in p.locks:
                            del self.locks[l]

                        self.term.endProc(p)

                    elif msg['req'] == 'get-input':
                        #Proc is requesting input. Provide it
                        input = self.term.getInput(message=msg['message'], password=msg['password'])
                        
                        msg.update({'resp': input})
                        p.queueToProc.put(msg)

                    elif msg['req'] == 'create-proc':
                        procName = self.createProc(msg['protoName'], msg['procName'], msg['args'])
                        msg.update({'procName': procName}) #In case we created new name
                        p.queueToProc.put(msg) #Respond with same msg. No new data

                    elif msg['req'] == 'start-procs':
                        self.startProcs(msg['names'])
                        p.queueToProc.put(msg) #Respond with same msg. No new data                    

                    elif msg['req'] == 'check-complete':
                        msg.update({'complete': self.checkComplete(msg['names']),
                                    'failure': self.checkFailure(msg['names'])})
                        p.queueToProc.put(msg)

                    elif msg['req'] == 'get-results':
                        msg.update({'results': self.context['results']})
                        p.queueToProc.put(msg)

                    else:
                        raise Exception('unknown call: {}'.format(msg['req']))

            #If still running after processing messages, check for timeout
            if p.isRunning() and p.timeout is not None and\
               (time.time() - p.startTime) > p.timeout:

                p.process.terminate()
                p.process = None
                p.output = None
                p.error = Proc.ERROR_TIMEOUT
                p.state = Proc.STATE_FAILED
                p.logFilename = os.path.join(self.context['logdir'], name + '.log')

                logger.info('proc "{}" timed out'.format(p.name))

                self.context['results'][p.name] = None
                        
                logger.info('new context: {}'.format(self.context))
                    
                #Release locks
                for l in p.locks:
                    del self.locks[l]

                self.term.endProc(p)


        if foundAny:
            self.tryExecuteAny()

    #Wait for all procs and locks
    def waitForAll(self, exceptionOnFailure=True):
        logger.debug('WAIT FOR COMPLETION')
        while any(p.state != Proc.STATE_IDLE and not p.isComplete() for name, p in self.procs.items()) or self.locks:
            self._step()

        #Do final update. Force update
        self.term.update(force=True)

        #Raise on issue
        if exceptionOnFailure and self.checkFailure(list(self.procs)):
            raise FailureException()

    #Wait for procs or locks
    def wait(self, names):
        logger.debug('WAIT FOR {}'.format(names))
        while not self.checkComplete(names):            
            self._step()
            
        #Do final update. Force update
        self.term.update(force=True)

        #Raise on issue
        if self.checkFailure(names):
            raise FailureException()

        

    def checkComplete(self, names):
        #If proc does not exist, waits for proc to be created
        return all(self.procs[name].isComplete() if name in self.procs else False for name in names)\
            and not any(name in self.locks for name in names)

    def checkFailure(self, names):
        return any(self.procs[name].state == Proc.STATE_FAILED for name in names if name in self.procs)
            
               
               

    #Move things forward
    def _step(self):
        #Move things forward
        self.collect()
        #Wait for a bit
        time.sleep(0.01)
        #Update terminal
        self.term.update()
            
            
    #def getData(self):
    #    return {p.name: p.output for key, p in self.procs.items()}

    def waitClear(self, exceptionOnFailure=False):
        self.waitForAll(exceptionOnFailure=exceptionOnFailure)
        self.clear()


#Objects of this class only live inside the individual proc threads
class ProcContext:

    def __init__(self, procName, context, queueToProc, queueToMaster):
        self.procName = procName
        self.results = context['results']
        self.params = context['params']
        self.args = context['args']
        self.queueToProc = queueToProc
        self.queueToMaster = queueToMaster

    def _cmd(self, **kwargs):
        #Pass request to master
        self.queueToMaster.put(kwargs)
        #Get and return response
        logger.debug('ProcContext request to master: {}'.format(kwargs))
        resp = self.queueToProc.get()
        logger.debug('ProcContext response from master: {}'.format(resp))
        return resp

    def getInput(self, message='', password=False):
        return self._cmd(req='get-input', message=message, password=password)['resp']

    def create(self, protoName, procName=None, **args):
        return self._cmd(req='create-proc', protoName=protoName, procName=procName, args=args)['procName']
        
    def start(self, *names):
        self._cmd(req='start-procs', names=names)

    def wait(self, *names):
        #Periodically poll for completion
        logger.info('waiting to wait')
        while True:
            res = self._cmd(req='check-complete', names=names)
            if res['failure']:
                raise FailureException()
            elif res['complete']:
                break
            logger.info('waiting for sub-proc')
            time.sleep(0.01)

        #At this point, everything is complete
        logger.info('wait done. results pre: {}'.format(self.results))
        self.results.update(self._cmd(req='get-results', names=names)['results'])    
        logger.info('wait done. results post: {}'.format(self.results))


#Decorator for process prototypes. These can be parameterized and instantiated again and again
class Proto:
    def __init__(self, name=None, f=None, deps=[], locks=[], now=False, args=None, timeout=None):
        #Input properties
        self.name = name
        self.deps = deps
        self.locks = locks
        self.now   = now #Whether proc will start once created
        self.args  = args if args is not None else {}
        self.timeout = timeout

        if f is not None:
            #Created using short-hand
            self.__call__(f)

    #Called immediately after initialization
    def __call__(self, f):
    
        if self.name is None:
            self.name = f.__name__

        self.func = f
        ProcManager.getInst().addProto(self)
        
        return None #Not meant to be called in the traditional way


#Decorator for processes
# name   - identified name of process
# deps   - process dependencies. will not be run until these have run
# locks  - list of locks. only one process can own a lock at any given time
class Proc:

    STATE_IDLE        = 0 #Defined, but will not run until it is the dependency of another proc
    STATE_WANTED      = 1 #Dependency of another proc, or specified to run immediately
    STATE_RUNNING     = 2
    STATE_SUCCEEDED   = 3
    STATE_FAILED      = 4

    ERROR_NONE        = 0
    ERROR_EXCEPTION   = 1
    ERROR_DEP_FAILED  = 2
    ERROR_TIMEOUT     = 3
    
    
    #Called on intitialization
    def __init__(self, name=None, f=None, *, deps=[], locks=[], now=False, args=None, proto=None, timeout=None):
        #Input properties
        self.name = name
        self.deps = deps
        self.locks = locks
        self.now = now
        self.args = args if args is not None else {}
        self.proto = None
        self.timeout = timeout

        #Utils
        self.logFilename = ''

        #Main function
        self.func = None

        #State
        self.startTime = None
        self.endTime = None
        self.process = None
        self.queueToProc = None
        self.queueToMaster = None
        self.state = Proc.STATE_IDLE
        self.error = Proc.ERROR_NONE
        self.moreInfo = ''
        self.output = None

        if f is not None:
            #Created using short-hand
            self.__call__(f)

    def isRunning(self):
        return self.state == Proc.STATE_RUNNING
    
    def isComplete(self):
        return self.state == Proc.STATE_SUCCEEDED or self.state == Proc.STATE_FAILED

    def isFailed(self):
        return self.state == Proc.STATE_FAILED


    #Called immediately after initialization
    def __call__(self, f):
        #Queue is bi-directional queue to provide return value on exit (and maybe other things in the future
        def func(queueToProc, queueToMaster, context, name):
            #TODO: Wrap function and replace sys.stdout and sys.stderr to capture output
            #https://stackoverflow.com/questions/30793624/grabbing-stdout-of-a-function-with-multiprocessing
            logger.info('proc "{}" started'.format(name))

            pc = ProcContext(name, context, queueToProc, queueToMaster)
            error = Proc.ERROR_NONE
            ret = None

            stdout = sys.stdout
            stderr = sys.stderr

            #Redirect output to file, one for each process, to keep the output in sequence
            logFilename = os.path.join(context['logdir'], name + '.log')
            with open(logFilename, 'w') as logFile:
                sys.stdout = logFile #Redirect stdout
                sys.stderr = logFile

                try:
                    ret = f(pc, **pc.args)    #Execute process
                except Exception as e:
                    ex_type, ex, tb = sys.exc_info()
                    info = str(e) + '\n' + ''.join(traceback.format_tb(tb))

                    logFile.write(info)
                    error = Proc.ERROR_EXCEPTION


            sys.stdout = stdout
            sys.stderr = stderr
                
            msg = {'req': 'proc-complete', 'value': ret, 'logFilename': logFilename, 'error': error}

            logger.info('proc "{}" ended: ret = {}'.format(name, ret))
            
            queueToMaster.put(msg) #Provide return value from function

        if self.name is None:
            self.name = f.__name__

        self.func = func
        ProcManager.getInst().addProc(self)
        
        return None #Not meant to be called in the traditional way







def waitForAll(exceptionOnFailure=True):
    return ProcManager.getInst().waitForAll(exceptionOnFailure=exceptionOnFailure)
    

def results():
    return ProcManager.getInst().context['results']

def setParams(**params):
    ProcManager.getInst().setParams(**params)
    

#Waits for any previous job to complete, then clears state
def waitClear(exceptionOnFailure=False):
    return ProcManager.getInst().waitClear(exceptionOnFailure=exceptionOnFailure)

def start(*names):
    return ProcManager.getInst().startProcs(names)

def create(protoName, procName=None, **args):
    return ProcManager.getInst().createProc(protoName, procName, args)

#Wait for given proc or lock names
def wait(*names):
    return ProcManager.getInst().wait(names)
