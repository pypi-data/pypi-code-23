import opentracing
from opentracing.ext.threadlocalspansource import ThreadLocalActiveSpanSource
import gevent
from gevent.monkey import patch_thread

patch_thread()

import threading
print threading.local()

source = ThreadLocalActiveSpanSource()
#print source._tls_snapshot
#source._tls_snapshot = threading.local()
#print source._tls_snapshot

def target1():
    span = opentracing.Span(None, None)
    active_span = source.make_active(span)
    print 'Before - ActiveSpan (t1): %s' % active_span

    gevent.sleep(.5)

    print 'After - ActiveSpan (t1): %s' % active_span
    assert active_span == source.active_span

def target2():
    span = opentracing.Span(None, None)
    active_span = source.make_active(span)
    print 'Before - ActiveSpan (t2): %s' % active_span
    if active_span._to_restore is not None:
        print 'Got damned, got the previous span: %s' % active_span._to_restore

    gevent.sleep(.5)

    print 'After - ActiveSpan (t2): %s' % active_span
    assert active_span == source.active_span

gthreads = [
    gevent.spawn(target1),
    gevent.spawn(target2),
]

gevent.joinall(gthreads)

