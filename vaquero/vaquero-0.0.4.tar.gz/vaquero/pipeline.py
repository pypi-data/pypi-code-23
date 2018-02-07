import ast
import imp
import inspect
import types
from .invocation_tools import _name_of


class PipelineCommand:
    def __init__(self, name):
        self._name = name


class SkipTo(PipelineCommand):
    # TODO: Singleton?
    def __init__(self, resuming_function_name):
        self.function_name = _name_of(resuming_function_name)

Done = PipelineCommand('DONE')


def collect_func_ordering(file_path_or_module):
    """
    Collect all top-level functions in a file or module, in order.

    :param file_path_or_module: the path to the python file, or a module.
    :return: the ordered top-level function names.
    """
    if isinstance(file_path_or_module, types.ModuleType):
        file_path = inspect.getsourcefile(file_path_or_module)
    else:
        file_path = file_path_or_module

    with open(file_path, 'r') as fp:
        root = ast.parse(fp.read())

    names = []
    for node in ast.iter_child_nodes(root):
        if isinstance(node, ast.FunctionDef):
            names.append(node.name)
    return names


def collect_pipeline(module, skip_private=True, reloading=True):
    """
    Load the functions in a module in their definition order.

    :param module: a python module
    :param skip_private: ignore functions starting with '_'
    :param reloading: reload the module prior to collection
    :return: the functions in their definition order
    """
    if reloading:
        module = imp.reload(module)

    pipeline = []
    env = vars(module)
    for name in collect_func_ordering(module):
        if skip_private and name.startswith('_'):
            continue
        pipeline.append(env[name])
    return pipeline


class Pipeline(object):
    """
    A sequence of functions for data processing.
    """

    def __init__(self):
        self._pipeline = []
        self._captures = []

    def __iter__(self):
        return iter(self._captures)

    def __call__(self, *args, **kwargs):
        await_f = None
        for f in self._pipeline:
            if await_f is not None:
                if _name_of(f) != await_f:
                    continue
                else:
                    await_f = None

            cmd = f(*args, **kwargs)

            if isinstance(cmd, PipelineCommand):
                if cmd is Done:
                    break
                elif isinstance(cmd, SkipTo):
                    await_f = cmd.function_name

        if await_f is not None:
            raise NameError("Function {} never visited".format(await_f))


class ModulePipeline(Pipeline):
    """
    Extract a pipeline from a Python module.

    This executes each function in the order laid out by the file.
    """
    def __init__(self, module, skip_private_applications=True,
                 include_private_captures=True, reloading=True):
        """

        :param module: the python module to load
        :param skip_private_applications: if True, then functions prefixed with
            '_' are not included in the transformation pipeline
        :param include_private_captures: if True, then functions prefixed with
            '_' ARE captured for error analysis.
        :param reloading: if True, reloads the module when calling `reload()`
        """
        self._module = module
        self._skip_private_applications = skip_private_applications
        self._include_private_captures = include_private_captures
        self._reloading = reloading

        super(ModulePipeline, self).__init__()

        self.reload(force=True)

    def reload(self, force=False):
        """
        Reload the underlying module.

        :param force: if True, reloads the module, even if reloading is false.
        """
        # Note: reloading the module on the initial load actually makes sense
        # given how it's used. In a notebook, you import the module, then
        # pass it to the constructor. It's easy to step over that
        # constructor again, passing the old module reference.
        if force or self._reloading:
            self._pipeline = []
            self._captures = []
            for f in collect_pipeline(self._module, skip_private=False):
                is_private = f.__name__.startswith('_')

                if not self._skip_private_applications or not is_private:
                    self._pipeline.append(f)

                if self._include_private_captures or not is_private:
                    self._captures.append(f)
