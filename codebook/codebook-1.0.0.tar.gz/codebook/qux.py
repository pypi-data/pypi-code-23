EMBEDDED = True

def foo(a=1, b=2):
    import IPython
    IPython.start_kernel(user_ns={**locals(), **globals(), **vars()})

def bar():
    print(__name__)

if __name__ == '__main__':
    foo()
