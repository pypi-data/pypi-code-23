from __future__ import absolute_import

from bluelens_spawning_pool import spawning_pool

class Pod(object):
  def __init__(self, redis_server, redis_password, redis=None, log=None):
    self._redis = redis
    self._redis_server = redis_server
    self._redis_password = redis_password
    self._log = log

  def log(self, msg):
    if self._log != None:
      self._log.debug(msg)

  def delete_pod(self, spawn_id, release_mode):
    self.log('delete_pod: ' + spawn_id)
    data = {}
    data['namespace'] = release_mode
    data['key'] = 'SPAWN_ID'
    data['value'] = spawn_id
    spawn = spawning_pool.SpawningPool()
    spawn.setServerUrl(self._redis_server)
    spawn.setServerPassword(self._redis_password)
    spawn.delete(data)

