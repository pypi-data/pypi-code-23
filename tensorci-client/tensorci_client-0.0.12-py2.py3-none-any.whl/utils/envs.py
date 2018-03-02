import os


class Envs(object):
  vars = (
    'TENSORCI_CLIENT_ID',
    'TENSORCI_CLIENT_SECRET',
    'TENSORCI_TEAM',
    'TENSORCI_PROJECT',
    'TENSORCI_HOST_DOMAIN',
    'TENSORCI_SOCKET_URL',
    'TENSORCI_SOCKET_PORT'
  )

  def __init__(self):
    for var in self.vars:
      setattr(self, var, os.environ.get(var))


envs = Envs()