__all__ = ["cprof", "lprof"]
__author__ = "Casper da Costa-Luis <casper.dcl@physics.org>"
__version__ = "0.0.1"


def cprof(f):
    from cProfile import Profile

    def inner(*args, **kwargs):
        profile = Profile()
        try:
            profile.enable()
            result = f(*args, **kwargs)
            profile.disable()
            return result
        finally:
            profile.print_stats(sort=1)
    return inner


def lprof(follow=None):
    from line_profiler import LineProfiler

    if follow is None:
        follow = []

    def inner(func):
        def profiled_func(*args, **kwargs):
            profiler = LineProfiler()
            try:
                profiler.add_function(func)
                for f in follow:
                    profiler.add_function(f)
                profiler.enable_by_count()
                return func(*args, **kwargs)
            finally:
                profiler.print_stats()
        return profiled_func
    return inner
