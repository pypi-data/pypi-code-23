import os
from importlib import util as importlib_util


def module_exists(module_name: str):
    """
    Check if a module exists.
    """
    try:
        __import__(module_name)
    except ImportError:
        return False
    else:
        return True


def load_module_from_file(module_path: str):
    """"""
    module_name: str = os.path.basename(module_path.replace('.py', ''))
    spec = importlib_util.spec_from_file_location(module_name, module_path)
    module = importlib_util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module
