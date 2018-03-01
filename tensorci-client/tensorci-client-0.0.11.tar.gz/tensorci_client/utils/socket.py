from tensorci_client.definitions import default_socket_port
from tensorci_client.utils.envs import envs
from websocket import WebSocket


def new_socket(domain=None, port=default_socket_port, **kwargs):
  if envs.TENSORCI_SOCKET_URL:
    url = envs.TENSORCI_SOCKET_URL
  else:
    use_secure_sockets = kwargs.get('SECURE_SOCKETS') is True or domain != 'localhost'

    if use_secure_sockets:
      protocol = 'wss://'
    else:
      protocol = 'ws://'

    url = protocol + domain + ':' + port

  ws = WebSocket(**kwargs)
  ws.connect(url)

  return ws