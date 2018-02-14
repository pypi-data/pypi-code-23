import sys
import os.path
import os
import time
import uuid
import json
import multiprocessing as mp
import atexit

session = uuid.uuid4().hex
machine = None
cur_chunk = {}
last_sent = time.time()
once = True
_enabled = True
proc = None
site = os.environ.get("LRS") or "https://learning-rates.com" 
chunk_list = mp.Manager().list()
session_file = os.path.expanduser('~/.lr')

if not os.path.exists(session_file):
  with open(session_file, "w") as sfile:
    sfile.write(uuid.uuid4().hex)


with open(session_file, "r") as sfile:
  machine=sfile.read()

def sending_process(chunk_list):
  import requests
  PY3 = sys.version_info[0] == 3
  string_type = str if PY3 else basestring

  s = requests.Session()
  s.headers.update({
    'machine': machine, 
    'Content-Type': 'application/octet-stream'
    })
  cur_chunk = {}
  finish = False
  cons_fails = 0

  try:
    while not finish:
      while len(chunk_list) > 0:
        arg_dict = {}
        args, now = chunk_list.pop(0) 
        if args is None:
          finish = True
          break
        if len(args) == 2:
          arg_dict[args[0]] = args[1]
        elif isinstance(args[0], dict): 
          arg_dict = args[0]
        else:
          raise Exception("wrong arguments")
        
        arg_dict_filter = {}
        for name in arg_dict:
          #str_type = str(type(arg_dict[name]))
          if isinstance(arg_dict[name], bool) or isinstance(arg_dict[name], int) or isinstance(arg_dict[name], float) or isinstance(arg_dict[name], string_type):
            arg_dict_filter[name] = arg_dict[name]
          #TODO: numpy
          #elif str_type == "<type 'numpy.float16'>" 

            
        arg_dict = arg_dict_filter

        for name in arg_dict:
          if not (name in cur_chunk):
            cur_chunk[name] = [(arg_dict[name], now)]
          else: 
            cur_chunk[name].append((arg_dict[name], now))

      if len(cur_chunk) > 0:
        try:
          r = s.post("{0}/data/{1}".format(site, session), data=json.dumps(cur_chunk), timeout=5.0)
          cur_chunk={}
          cons_fails = 0
        except Exception as e:
          cons_fails += 1
          print("learning-rates.com: error sending data", e)
          if cons_fails >= 6:
            print("learning-rates.com: Too many connection problems, stop sending.")
            finished = True

      if not finish:
        time.sleep(1)
  except Exception as e :
    print("learing-rates.com: ", e) 

hyper = {}
def hyperparams(d):
  to_send = {}
  for name in d:
    if not (name in hyper):
      hyper[name] = d[name]
      to_send[name] = d[name]

  send(to_send)

def send(*args):
  if not _enabled:
    return
  global once
  global proc
  if once:
    proc = mp.Process(target=sending_process, args=(chunk_list,))
    proc.start()
    once = False

  if proc.is_alive():
    chunk_list.append((args, time.time()))


exit_code = None
exit_exc = None
original_exit = sys.exit
original_exc = sys.excepthook

def exc_handler(exc_type, exc, *args):
  global exit_exc
  exit_exc = exc_type
  if original_exc is not None:
    original_exc(exc_type, exc, *args)

def my_exit(code=0):
    global exit_code
    exit_code = code
    original_exit(code)

sys.exit = my_exit
sys.excepthook = exc_handler

def on_exit():
  if proc is None:
    return

  if exit_exc is None and exit_code == 0:
    proc.join()
  else:
    proc.terminate()

def enabled(value):
  global _enabled
  _enabled = value

def get_url(): 
  return "{0}/m/{1}".format(site, machine[:6])

def main():
  print("Open {} to view expriments that run from this box".format(get_url())) 

atexit.register(on_exit)
__all__ = ['send', 'enabled', 'get_url']
