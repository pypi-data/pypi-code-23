import sys
import os.path
import os
import time
import uuid
import requests
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
site = os.environ.get("STATLY") or "https://learning-rates.com" 
parent_conn, child_conn = mp.Pipe()
session_file = os.path.expanduser('~/.lr')

if not os.path.exists(session_file):
  with open(session_file, "w") as sfile:
    sfile.write(uuid.uuid4().hex)


with open(session_file, "r") as sfile:
  machine=sfile.read()


def sending_process(conn):
  s = requests.Session()
  s.headers.update({
    'machine': machine, 
    'Content-Type': 'application/octet-stream'
    })
  cur_chunk = {}
  finish = False

  try:
    while not finish:
      while conn.poll():
        arg_dict = {}
        args, now = conn.recv()
        if args is None:
          finish = True
          break
        if len(args) == 2:
          arg_dict[args[0]] = args[1]
        elif isinstance(args[0], dict): 
          arg_dict = args[0]
        else:
          raise Exception("wrong arguments")
        
        for name in arg_dict:
          if not (name in cur_chunk):
            cur_chunk[name] = [(arg_dict[name], now)]
          else: 
            cur_chunk[name].append((arg_dict[name], now))

      if len(cur_chunk) > 0:
        try:
          r = s.post("{0}/data/{1}".format(site, session), data=json.dumps(cur_chunk))
          cur_chunk={}
        except Exception as e:
          print("learning rate: error sending data", e)

      if not finish:
        time.sleep(1)
  except Exception as e :
    print("learing-rate: ", e) 
    pass;

def send(*args):
  if not _enabled:
    return
  global once
  global proc
  if once:
    #print("started statly session: {0}/s/{1}".format(site, session))
    proc = mp.Process(target=sending_process, args=(child_conn,))
    proc.start()
    once = False

  if proc.is_alive():
    parent_conn.send((args, time.time()))


def on_exit():
  parent_conn.send((None,None))
  #print("on_exit",  proc)
  if proc:
    proc.join()

def enabled(value):
  global _enabled
  _enabled = value

def get_url(): 
  return "{0}/m/{1}".format(site, machine[:6])

def main():
  print("Open {} to view expriments that run from this box".format(get_url())) 

atexit.register(on_exit)
__all__ = ['send', 'enabled', 'get_url']
