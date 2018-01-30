# -*- coding: utf-8 -*-
from cStringIO import StringIO
import sys
import thread
import time
import traceback


def threads(connection):
    """Dump current threads execution stack."""
    frames = sys._current_frames()
    this_thread_id = thread.get_ident()
    now = time.strftime('%Y-%m-%d %H:%M:%S')
    res = ['Threads traceback dump at {0}\n'.format(now)]
    for thread_id, frame in frames.iteritems():
        if thread_id == this_thread_id:
            continue
        # Find request in frame
        reqinfo = ''
        f = frame
        while f is not None:
            request = f.f_locals.get('request')
            if request is not None:
                reqmeth = request.get('REQUEST_METHOD', '')
                pathinfo = request.get('PATH_INFO', '')
                reqinfo = (reqmeth + ' ' + pathinfo)
                qs = request.get('QUERY_STRING')
                if qs:
                    reqinfo += '?' + qs
                break
            f = f.f_back
        if reqinfo:
            reqinfo = ' ({0})'.format(reqinfo)
        output = StringIO()
        traceback.print_stack(frame, file=output)
        res.append('Thread {0}{1}:\n{2}'.format(
            thread_id,
            str(reqinfo),
            output.getvalue())
        )
    frames = None
    res.append('End of dump')
    print >> connection, '\n'.join(res)

