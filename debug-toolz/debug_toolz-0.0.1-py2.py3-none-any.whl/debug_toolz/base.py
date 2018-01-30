from functools import wraps
from inspect import getcallargs


def show_args(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        params = getcallargs(fn, *args, **kwargs)
        print "The function {name} was called ".format(name=fn.__name__)
        print "with the following arguments: "
        for k, v in params.iteritems():
            print "{k}: {v}".format(k=k, v=v)
        return fn(*args, **kwargs)
    return wrapper


@show_args
def f(a, b, c=1):
    return (a, b, c)


if __name__ == "__main__":
    f(1, 2)
