import os
import types


def _clean_filename(filename):
    """
    Make a traceback code-frame's file name more human readable.

    :param filename: the file name given in a traceback code frame.
    :return: the human-readable file name
    """
    # The file name for an IPython input cell looks like:
    #    <ipython-input-111-8515003c2eb6>
    # It'd be less noisy to read in input cell format:
    #    In [111]
    if filename.startswith("<ipython-input-"):
        return "In [{}]".format(filename.split("-")[2])
    else:
        return os.path.basename(filename)


def _extract_args(frame):
    """
    Extract the arguments given to the function called in the given frame.

    :param frame: the frame from a traceback object
    :return: None if there were no arguments, otherwise a tuple of the
        function's arguments.
    """
    # Number of arguments given to the function.
    # But, this doesn't include * or ** arguments.
    code = frame.f_code
    n_args = code.co_argcount
    if n_args == 0:
        return None
    else:
        # The `co_varnames` object seems like a stack, listing variables in
        # creation order. The first `n_args` bindings are the function's
        # arguments.
        #
        # Warning: Don't make this a tuple, even though it feels natural.
        # JMESPath doesn't like array-indexing on tuples.
        return [frame.f_locals.get(k) for k in code.co_varnames[:n_args]]


def no_filter(invocation_dict):
    return True


def _extract_invocations(tb, accept_pred=no_filter):
    """
    Extract a list of function invocation information from a traceback.

    :param tb: the traceback object
    :param accept_pred: given the extracted invocation details, this
        predicate returns True to include this in the results list. The
        default predicate does no filtering.
    :return: a list of dictionaries with `name`, `file_name`, `lineno`,
        `call_args` keys associated with the invocation's traceback frame
    """
    invocations = []

    while tb:
        frame = tb.tb_frame
        code = frame.f_code

        invocation = {'name': code.co_name,
                      'filename': _clean_filename(code.co_filename),
                      'lineno': tb.tb_lineno,
                      'call_args': _extract_args(frame)}
        if accept_pred(invocation):
            invocations.append(invocation)
        tb = tb.tb_next

    return invocations


def callables_from(env, include_private=False):
    """
    Collect all the callable objects in the given environment

    :param env: the target environment (i.e. binding -> value dict). Usually,
        this should be `globals()`. If it is an object, it collects all methods
        in that object. If it is a module, it collects all top-level callables.
    :return: a list of the callable objects' names
    """
    if isinstance(env, types.ModuleType):
        env = vars(env)
    elif not isinstance(env, dict):
        # TODO: BUG: Will this break descriptors and property methods?
        env = {k: getattr(env, k) for k in dir(env)}

    if include_private:
        return [name for name, obj in env.items() if hasattr(obj, '__call__')]
    else:
        return [name for name, obj in env.items()
                if hasattr(obj, '__call__') and not name.startswith('_')]




def _name_of(f):
    return f.__name__ if hasattr(f, '__name__') else f
