import time, logging, sys, os
from unittest import TestCase
from nose_parameterized import parameterized

import parproc as pp



class ProtoTest(TestCase):

    def setUp(self):
        logging.basicConfig(level = logging.DEBUG)
        pp.ProcManager.getInst().setOptions(dynamic=False)

    #Proto creation from base
    def test_protoFromBase(self):

        pp.waitClear()

        @pp.Proto(name='test')
        def proto(context, p0):
            return p0 + 'ba'

        #Create proc and run by handle
        pp.create('test', 'test:1', p0='ha')
        pp.create('test', 'test:2', p0='la')
        pp.start('test:1', 'test:2')

        pp.wait('test:1', 'test:2')
        self.assertEqual(pp.results(), {'test:1': 'haba', 'test:2': 'laba'})
        

    #Creation of proto from inside a proc
    def test_protoFromProc(self):

        pp.waitClear()

        @pp.Proto(name='proto')
        def proc1(context, x, y):
            logging.info('PROTO FUNC: {}, {}'.format(x, y))
            return x + context.args['y']

        @pp.Proto(name='base')
        def proc0(context, a, b):
            #Create multiple procs from within proc
            context.create('proto', 'proto:1', x=1, y=a)
            context.create('proto', 'proto:2', x=2, y=b)

            context.start('proto:1', 'proto:2')
            context.wait('proto:1', 'proto:2') #Automatically feeds results into context.results

            return context.results['proto:1'] + context.results['proto:2']

        pp.create('base', 'base', a=1, b=2)
        pp.start('base')
        pp.wait('base')

        self.assertEqual(pp.results(), {'base': 6, 'proto:1': 2, 'proto:2': 4})

    #Tests shorthands for proto creation, starting, stopping, etc
    def test_shorthands(self):

        pp.waitClear()

        #Proto short-hand
        pp.Proto('f0', lambda c, x, y: x*y, now=True)

        #Proc short-hand
        pp.Proc('f1', lambda c: 10, now=True)

        pp.waitForAll()

        #f1 should have run, but not f0, as it has not yet been instantiated
        self.assertEqual(pp.results(), {'f1': 10})

        #Kick off a couple f0s. Starts immediately on creation due to 'now' setting
        pp.wait(*[pp.create('f0', x=1, y=2),
                  pp.create('f0', x=3, y=4)])

        self.assertEqual(pp.results(), {'f1': 10, 'f0:0': 2, 'f0:1': 12})

        #Test kickoff from inside proc
        @pp.Proc(now=True)
        def f2(context):
            context.wait(*[context.create('f0', x=10, y=20),
                           context.create('f0', x=30, y=40)])
            return context.results['f0:2'] + context.results['f0:3']

        pp.wait('f2')

        self.assertEqual(pp.results(), {'f1': 10, 'f0:0': 2, 'f0:1': 12, 'f2': 1400, 'f0:2': 200, 'f0:3': 1200})
            
    #Check timeouts within procs and within procs within procs
    def test_timeouts(self):

        pp.Proto('sleepy', lambda c: time.sleep(10), timeout=1, now=True)

        with self.assertRaises(pp.FailureException):
            pp.wait(pp.create('sleepy'))

        #Test timeout within proc
        @pp.Proc(now=True)
        def gotException(context):
            try:
                context.wait(context.create('sleepy'))
            except pp.FailureException:
                return True #Expect the exception to happen
            else:
                return False

        pp.wait('gotException')
        
        self.assertEqual(pp.results()['gotException'], True)

        
    #Test wait on locks

    #Implement and test timeouts for both wait functions. Verify that TIMEOUT error is set on failure
