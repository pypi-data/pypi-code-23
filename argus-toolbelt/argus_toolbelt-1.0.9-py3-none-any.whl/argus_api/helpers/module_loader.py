import sys, importlib, pkgutil

def import_submodules(package_name: str, exclude_name: str = None) -> dict:
    """Import all submodules of a module, recursively. 

    This is used to import all APIs when Argus is loaded,
    so that the commands become registered as plugins,
    but can also be used to recursively import any other 
    package where you want every single file to load.

    TODO: Plugin loader can use this function to recursively
    load argus_plugins package!
    
    :param package_name: Package name, e.g "argus_api.api"
    :param exclude_name: Any module containing this string will not be imported
    """
    package = sys.modules[package_name]
    return {
      name: importlib.import_module(package_name + "." + name)
      for loader, name, is_pkg in pkgutil.walk_packages(package.__path__)
      if not exclude_name or  exclude_name not in name
    }