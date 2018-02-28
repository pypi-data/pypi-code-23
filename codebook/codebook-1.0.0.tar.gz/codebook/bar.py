import os

def catch(exctype, value, tb):
    while True:
        if not tb.tb_next:
            break
        tb = tb.tb_next
    import traceback
    frame_summary, = traceback.extract_tb(tb)
    from epc.client import EPCClient
    epc_client = EPCClient(('localhost', 9999), log_traceback=True)
    script, extension = os.path.splitext(sys.argv[0])
    epc_client.call('python-exception', args=[f'{script}.{frame_summary.name}'])
    epc_client.close()
    import IPython
    IPython.start_kernel(user_ns={'__locals__': tb.tb_frame.f_locals})

# import sys
# sys.excepthook = catch

aaa = 42
bbb = 442
ccc = 422

def foo(a=1, b=2):
    """A function"""
    bar(88, 99)

def bar(c=3, d=4):
    """A function"""
    x = 5
    return x

def biz(e=5, f=6):
    """A function

    >>> e = 77
    >>> f = 88

    """
    g = e + f
    return g

def baz(h, i=7):
    """A function

    >>> h = 8

    """
    j = h + i
    return j


if __name__ == '__main__':
    foo()
