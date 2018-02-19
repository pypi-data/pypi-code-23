import argparse

_tasks = {}

class HakeException(Exception):
  pass

def def_task(name, func):
  _tasks[name] = func

def def_default_task(func):
  _tasks['default'] = func

def run_tasks(*tasks):
  for task in tasks:
    _tasks[task]()

class task():
  def __init__(self, name):
    self.name = name

  def __call__(self, f):
    _tasks[self.name] = f
    return f

class default_task():
  def __init__(self, f):
    self.f = f
    _tasks['default'] = f

  def __call__(self, *args):
    self.f()

def _start_default_task():
  func = None
  if 'default' in _tasks:
    func = _tasks['default']
  else:
    keys = list(_tasks.keys())
    if len(keys) == 0:
      raise HakeException('No tasks specified!')
    else:
      func = _tasks[keys[0]]
  func()

def _start_first_task(*tasks):
  if len(tasks) > 0:
    run_tasks(*tasks)
  else:
    _start_default_task()

def start(desc = 'A Hake script'):
  parser = argparse.ArgumentParser(description = desc)
  parser.add_argument(
    'tasks',
    metavar = 'TASK',
    type = str,
    nargs = argparse.REMAINDER,
    default = [],
    help = 'Tasks to run'
  )
  args = parser.parse_args()
  _start_first_task(*args.tasks)