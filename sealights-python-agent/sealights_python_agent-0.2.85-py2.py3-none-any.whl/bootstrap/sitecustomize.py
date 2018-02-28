import imp
import os
import sys

from python_agent import admin
from python_agent.common.configuration_manager import ConfigurationManager

boot_directory = os.path.dirname(__file__)
root_directory = os.path.dirname(os.path.dirname(boot_directory))

path = list(sys.path)

if boot_directory in path:
    del path[path.index(boot_directory)]

try:
    (file, pathname, description) = imp.find_module('sitecustomize', path)
except ImportError:
    pass
else:
    imp.load_module('sitecustomize', file, pathname, description)


if root_directory not in sys.path:
    sys.path.insert(0, root_directory)

try:
    configuration_manager = ConfigurationManager()
    configuration_manager.try_load_configuration_from_file()
    run_index = configuration_manager.config_data.args.index("run")
    args = configuration_manager.config_data.args[1: run_index]
    program_exe_path = configuration_manager.config_data.program

    admin.bootstrap(args=args, prog_name=program_exe_path)
except SystemExit as e:
    if getattr(e, "code", 1) != 0:
        sys.exit(4)
except BaseException as e:
    sys.exit(5)

