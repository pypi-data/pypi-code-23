from __future__ import absolute_import

from bluelens_spawning_pool import spawning_pool

class Service(object):
  def __init__(self,
               redis_server,
               redis_password,
               redis=None,
               log=None):
    print('init')
    self._redis = redis
    self._redis_server = redis_server
    self._redis_password = redis_password
    self._log = log

  def do(self, host_code, host_group, version_id):
    print('Service')

  def spawn_crawler(self,
                    container_name,
                    container_image,
                    id,
                    server_url,
                    server_password,
                    metadata_namespace,
                    envs):

    pool = spawning_pool.SpawningPool()

    project_name = container_name + '-' + id
    self._log.debug('spawn_crawler: ' + project_name)

    pool.setServerUrl(server_url)
    pool.setServerPassword(server_password)
    pool.setApiVersion('v1')
    pool.setKind('Pod')
    pool.setMetadataName(project_name)
    pool.setMetadataNamespace(metadata_namespace)

    pool.addMetadataLabel('name', project_name)
    pool.addMetadataLabel('group', container_name)
    pool.addMetadataLabel('SPAWN_ID', id)

    container = pool.createContainer()
    pool.setContainerName(container, project_name)

    for key, value in envs.items():
      pool.addContainerEnv(container, key, value)

    pool.setContainerImage(container, container_image)
    pool.setContainerImagePullPolicy(container, 'Always')
    pool.addContainer(container)
    pool.setRestartPolicy('Never')
    pool.spawn()
