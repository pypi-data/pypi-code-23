from tensorci_client.definitions import default_socket_port
from tensorci_client.utils.envs import envs
from websocket import WebSocket


def new_socket(domain=None, port=default_socket_port, headers={}, **kwargs):
  if envs.TENSORCI_SOCKET_URL:
    url = envs.TENSORCI_SOCKET_URL
  else:
    use_secure_sockets = kwargs.get('secure_sockets') is True or domain != 'localhost'

    if use_secure_sockets:
      protocol = 'wss://'
      port = 443
    else:
      protocol = 'ws://'

    url = '{}{}:{}'.format(protocol, domain, port)

  formatted_headers = ['{}: {}'.format(k, v) for k, v in headers.items()]
  connect_kwargs = {}

  if formatted_headers:
    connect_kwargs['header'] = formatted_headers

  ws = WebSocket(**kwargs)
  ws.connect(url, **connect_kwargs)

  return ws