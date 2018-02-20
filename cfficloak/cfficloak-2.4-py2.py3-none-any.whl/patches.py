import wrapt


@wrapt.patch_function_wrapper('distutils.ccompiler', 'CCompiler.spawn')
def _subprocess_spawn(wrapped, instance, args, kwargs):
    """
    Building C extension on Windows, it fails when debugging with pycharm due to the
    command line being split on spaces in any of the args. This doesn't happen during
    normal run mode however, so it's probably an issue with the debug injection tools
    in pycharm. It's easy to fix in code however by ensuring any paths with spaces in
    them are quoted.
    :param wrapped:
    :param instance:
    :param args:
    :param kwargs:
    :return:
    """
    from subprocess import call
    ret = call(args[0])
    return ret
