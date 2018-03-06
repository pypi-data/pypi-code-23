try:
  import cPickle as pickle
except ImportError:
  import pickle

import logging

__author__ = "Casper da Costa-Luis <casper.dcl@physics.org>"
__version__ = "0.2.0"


def memoise(ignore_kwargs=None, ignore_args=None):
  if ignore_kwargs is None:
    ignore_kwargs = []
  if ignore_args is None:
    ignore_args = []

  def inner(fn):
    m = {}

    def memoisedFn(*a, **k):
      vs = tuple(v for v in a if v not in ignore_args)
      ks = tuple((k, v) for (k, v) in k.items() if k not in ignore_kwargs)
      res = m.get((vs, ks), None)
      if res is None:
        return m.setdefault((vs, ks), fn(*a, **k))
      return res
    return memoisedFn

  return inner


def load_db(shmDB):
  from io import open
  fname = "/dev/shm/" + shmDB
  db = {}
  try:
    db = pickle.load(open(fname, "rb"))
  except IOError as e:
    if "no such file" not in str(e).lower():
      log = logging.getLogger(__name__)
      log.warn("Could not load db. Possibly first time?")
      log.warn(str(e))
  return db


def save_db(shmDB, db):
  from io import open
  fname = "/dev/shm/" + shmDB
  pickle.dump(db, open(fname, "wb"), -1)


def hashForce(i):
  """returns hash(str(i)) if hash(i) fails"""
  try:
    return hash(i)
  except TypeError:
    return hash(str(i))


def memo_db(shmDB):
  """memoise to /dev/shm/"""
  db = load_db(shmDB)

  def wrapper(fn):
    def inner(*a, **k):
      key = (a, tuple(map(hashForce, k.items())))
      res = db.get(key, None)
      if res is None:
        db[key] = res = fn(*a, **k)
        save_db(shmDB, db)
      return res
    return inner
  return wrapper
