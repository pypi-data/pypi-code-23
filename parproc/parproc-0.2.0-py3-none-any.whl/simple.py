import time, logging, sys, os
from unittest import TestCase
from nose_parameterized import parameterized

import parproc as pp



class SimpleTest(TestCase):

    #Delays for 'seconds' seconds, and returns a tuple containing start-time and end-time
    def markedDelay(self, seconds):
        start = time.time()
        time.sleep(0.1)
        return (start, time.time())

    #Checks that the processes are in the given order based on (start, end) tuples
    def assertProcStartOrder(self, procNames):
        logging.debug('Checking start order: {}'.format(', '.join(['{}: {}'.format(name, pp.results()[name][0]) for name in procNames])))
        start = 0
        for pName in procNames:
            tt = pp.results()[pName]
            self.assertGreater(tt[0], start)
            start = tt[0]

    #Checks that the processes are not overlapping, based on their (start, end) tuples
    def assertProcNonOverlapping(self, procNames):
        end = 0
        for pName in procNames:
            tt = pp.results()[pName]
            self.assertGreater(tt[0], end)
            end = tt[1]

    def setUp(self):
        logging.basicConfig(level = logging.DEBUG)
        pp.ProcManager.getInst().setOptions(dynamic=False)

        

    @parameterized.expand([
        (1, ),
        (10, ),
    ])
    def test_simple(self, parallel=None):
        if parallel is None:
            return

        pp.waitClear()
        pp.ProcManager.getInst().setOptions(parallel=parallel)

        @pp.Proc(name='t1', deps=['t2'], now=True)
        def t1(context):
            print(context)
            return 'You' + context.results['t2']

        @pp.Proc(name='t2', now=True)
        def t2(context):
            return 'Me'

        pp.waitForAll()

        self.assertEqual(pp.results()['t2'], 'Me')
        self.assertEqual(pp.results()['t1'], 'YouMe')
        
        
    @parameterized.expand([
        (1, ),
        (10, ),
    ])
    def test_locks(self, parallel=None):
        if parallel is None:
            return
        
        pp.waitClear()
        pp.ProcManager.getInst().setOptions(parallel=parallel)

        @pp.Proc(name='t1', locks=['lock1'], now=True)
        def t1(context):
            return self.markedDelay(0.1)

        @pp.Proc(name='t2', locks=['lock1'], now=True) #Same lock as t1. Will wait for t1
        def t2(context):
            return self.markedDelay(0.1)
        
        @pp.Proc(name='t3', now=True)
        def t3(context):
            return self.markedDelay(0.1)

        pp.waitForAll()

        if parallel > 1:
            self.assertProcStartOrder(['t1', 't2']) #t1 or t3 could start first, but both before t2
            self.assertProcStartOrder(['t3', 't2'])
        else:
            self.assertProcStartOrder(['t1', 't2', 't3']) #In non-parallel mode, these go in sequence
            
        self.assertProcNonOverlapping(['t1', 't2']) #Share lock, so should not overlap


    #Verifies that if a proc has not been set to run immediately, it is not run until needed by another process, or until
    #a command has been sent to run it
    def test_wanted(self):

        pp.waitClear()
        
        @pp.Proc(name='x1')
        def x1(context):
            return True

        @pp.Proc(name='x2', deps=['x1'])
        def x2(context):
            return True
        
        
        @pp.Proc(name='x3')
        def x3(context):
            return True

        @pp.Proc(name='x4', deps=['x3'], now=True)
        def x4(context):
            return True

        pp.waitForAll() #Should only execute x3 and x4

        self.assertEqual(pp.results(), {'x3': True, 'x4': True})

        pp.start('x2') #Should kick off 'x1', then 'x2

        pp.waitForAll()

        self.assertEqual(pp.results(), {'x1': True, 'x2': True, 'x3': True, 'x4': True})


    def test_input(self):

        #Mock stdin
        readline = sys.stdin.readline
        sys.stdin.readline = lambda: 'the input'

        pp.waitClear()

        @pp.Proc(name='input0', now=True)
        def input0(context):
            return context.getInput()


        pp.waitForAll()

        self.assertEqual(pp.results(), {'input0': 'the input'})

        #Restore stdin
        sys.stdin.readline = readline


    def test_log(self):

        pp.waitClear()


        @pp.Proc(name='logger', now=True)
        def input0(context):
            print('this is the log output') #print to stdout
            print('this is an error', file=sys.stderr) #print to stderr

        pp.waitForAll()

        logFile = os.path.join(pp.ProcManager.getInst().context['logdir'], 'logger.log')
        with open(logFile, 'r') as f:
            self.assertEqual(f.read(), 'this is the log output\nthis is an error\n')


    #Verifies that dependant procs fail if a dependency fails
    def test_dependencyFailure(self):

        pp.waitClear()

        @pp.Proc(now=True)
        def p0(context):
            sleep(0.1)
            raise Exception('error')

        @pp.Proc(now=True, deps=['p0'])
        def p1(context):
            return True
        
        @pp.Proc(now=True, deps=['p1'])
        def p2(context):
            return True

        
        with self.assertRaises(pp.FailureException):
            pp.waitForAll()

        #Only one proc (the first) should run
        self.assertEqual(pp.results(), {'p0': None})

        
    
#Create test that sets up 4 procs that are not supposed to run, but with some deps. trigger one of them, and verify that only the ones with deps are executed        
#Only execute procs that either have 'now=True' or have another task with a dependency to them!
#Add state to proc (idle, ready, complete, failed)
#Add timeout option to each proc
