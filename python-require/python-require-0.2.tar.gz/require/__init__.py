import importlib.util, os, inspect, re, sys
import require.empty as empty

class require:

  def __init__(self):
    self.importing = {}
    self.require_debug = (os.getenv('REQUIRE_DEBUG', '') != '')

  def _debug(self, msg):
    if self.require_debug:
      sys.stderr.write(msg + '\n')

  def _path_to_name(self, path):
    return re.sub('/+', '.', re.sub('^/|_py$', '', re.sub('[^a-zA-Z0-9_/]', '_', str(path))))

  def _do_import(self, module_path):
    module_name = self._path_to_name(module_path)

    if os.path.isdir(module_path):
      module_path = os.path.join(module_path, '__init__.py')

    for name, mod in sys.modules.items():
      try:
        mod_path = os.path.realpath(os.path.abspath(inspect.getfile(mod)))
      except TypeError:
        continue
      if mod_path == module_path:
        self._debug(f'Aliasing already-instantiated module {name} to {module_name}')
        sys.modules[module_name] = mod
        return mod

    self._debug(f'Instantiating module {module_name} from path {module_path}')

    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None:
      raise ImportError(f'Could not find {module_path!r}')
  
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
  
    sys.modules[module_name] = module

    return module
  

  def __call__(self, module_path):
    if not os.path.isabs(module_path):
      caller_path = os.path.dirname(os.path.abspath(inspect.stack()[1][1]))
      module_path = os.path.join(caller_path, module_path)
    module_path = os.path.realpath(os.path.abspath(module_path))
    module_name = self._path_to_name(module_path)
    try:
      return sys.modules[module_name]
    except KeyError:
      pass

    containing_mods = []
    module_dir = os.path.dirname(module_path)
    while os.path.isfile(os.path.join(module_dir, '__init__.py')):
      containing_mods.append(module_dir)
      if os.path.ismount(module_dir):
        break
      module_dir = os.path.abspath(os.path.join(module_dir, '..'))

    containing_mods.reverse()

    stub_prefix = self._path_to_name(module_dir).split('.')
    for i in range(1, len(stub_prefix)+1):
      stub_module = '.'.join(stub_prefix[:i])
      if stub_module in sys.modules:
        continue
      self._debug(f'Installing stub module {stub_module}')
      sys.modules[stub_module] = empty

    for module_dir in containing_mods:
      if self.importing.get(module_dir, False):
        continue
      self.importing[module_dir] = True
      self._do_import(module_dir)
    
    return self._do_import(module_path)

sys.modules[__name__] = require()
