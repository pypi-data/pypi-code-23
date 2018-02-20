#from basictracer import BasicTracer
from opentracing import Span, Tracer
from opentracing.ext.threadlocalspansource import ThreadLocalActiveSpanSource

class MyTracer(ThreadLocalActiveSpanSource, Tracer):
    def __init__(self):
        super(MyTracer, self).__init__()

    # backwards compatible, i.e. no active, but what about the active span as parent?
    def start_active_span(self, *args, **kwargs):
        ignore_active_value = kwargs.pop('ignore_active', False)
        span = MySpan(self, None)
        span = self.make_active(span)

        return span

    def start_span(self, *args, **kwargs):
        make_active = kwargs.pop('make_active', True)
        ignore_active_value = kwargs.pop('ignore_active', False)
        span = MySpan(self, None)

        return span

class MySpan(Span):
    def __init__(self, tracer, context):
        super(MySpan, self).__init__(tracer, context)
        self._is_finished = False

    def finish(self):
        self._is_finished = True

# NOTE: So remember, just like the default tests do:
# only write tests for the actual code WE have, not
# for the invariants at that step. Then, of course, tests
# for the impl, but that's different.
# TODO - when almost ready, start putting together the
# scenarios we want to test, i.e.
# 1. No active span and ignore active
# 2. Set as active, but ignore activ
# 3. Set active AND implicitly take the one there
# 4. Set active BUT provide a custom span through child_of
# 5. Further calls to threadlocalactivespan.finish() shouldn't be causing the span to have finish called more than once.

tracer = MyTracer()
active_span = tracer.start_active_span(operation_name='Hola')
span = active_span.wrapped

print 'Active tracer: ', tracer.active_span
assert tracer.active_span is active_span

with active_span: # this is gonna get discarded, of course
    pass

assert tracer.active_span is None
assert span._is_finished is True

print 'Default passed!'

# remember: make_active() should be an implicit call most of the time...
#tracer.start_span(operation_name='Hi', active=False, child_of=None) # Option one
#tracer.start_span_active(operation_name='Hi') # Option two
#tracer.start_span(operation_name='Hi').set_active() # Option three # in this case, the default would need to be 'False'...

# So, the best one for me would be to have the three versions, as done with
# the Java impl - but that would mean keeping track of two versions of the method...
# however, the return value would be better...

# TODO - what to do if make_active() is called on the same value?
# 'reentrant'?
active_span = tracer.start_active_span(operation_name='Fuck')
span = active_span.wrapped
assert tracer.active_span == active_span

cont = tracer.active_span.capture()
assert tracer.active_span is active_span # still the same

active_span.deactivate()
assert tracer.active_span is None # no more, but the wrapped span is still around
assert span._is_finished is False

# I'm wondering if we could get a threadlocalactivespan brought around...
# i.e. kept around, called again... :/
active_span = cont.activate()
assert active_span == tracer.active_span # reactivated (active_span again, simply)
assert span._is_finished is False

active_span.deactivate() # refcount == 0, fuck that, deactivate/finish
assert tracer.active_span is None
assert span._is_finished is True

print 'Captured/deactivated passed!'

active_span = tracer.start_span('hola')
assert tracer.active_span is None
active_span.finish()

print 'No make active passed!'

# some invariants, like having make_active() called or
# active, can't be tested - at least in the API side,
# and only in the actual implementations.
