import json
from tensorci_client.exps import *
from tensorci_client.utils.envs import envs
from tensorci_client.utils.slug import to_slug
from tensorci_client.utils.socket import new_socket
from tensorci_client import definitions


class TensorCI(object):
  """
  TensorCI Websocket API Client.

  Basic Usage:

    Using kwargs for configuration:

      from tensorci_client.tensorci import TensorCI

      tensorci_client = TensorCI(client_id=<PROJECT_CLIENT_ID>,
                                 client_secret=<PROJECT_CLIENT_SECRET>,
                                 team=<TEAM_NAME>,
                                 project=<PROJECT_NAME>)

    Using environment variables for configuration:

      export TENSORCI_CLIENT_ID="<PROJECT_CLIENT_ID>"
      export TENSORCI_CLIENT_SECRET="<PROJECT_CLIENT_SECRET>"
      export TENSORCI_TEAM="<TEAM_NAME>"
      export TENSORCI_PROJECT="<PROJECT_NAME>"

      from tensorci_client.tensorci import TensorCI

      tensorci_client = TensorCI()
  """

  def __init__(self, client_id=None, client_secret=None, team=None, project=None):
    """
    :param str client_id:
      TensorCI project client ID
      :default: TENSORCI_CLIENT_ID env var
    :param str client_secret:
      TensorCI project client secret
      :default: TENSORCI_CLIENT_SECRET env var
    :param str team:
      TensorCI team name (will be slugified)
      :default: TENSORCI_TEAM env var
    :param str project:
      TensorCI project name (will be slugified)
      :default: TENSORCI_PROJECT env var
    """
    # Configuration attrs
    self.client_id = client_id or envs.TENSORCI_CLIENT_ID
    self.client_secret = client_secret or envs.TENSORCI_CLIENT_SECRET
    self.team = team or envs.TENSORCI_TEAM
    self.project = project or envs.TENSORCI_PROJECT

    # Validate configuration attrs above
    self.validate_config()

    domain = self.construct_domain()
    port = envs.TENSORCI_SOCKET_PORT or definitions.default_socket_port
    self.socket = new_socket(domain=domain, port=port)

  def validate_config(self):
    configs = (
      ('client_id', 'TENSORCI_CLIENT_ID'),
      ('client_secret', 'TENSORCI_CLIENT_SECRET'),
      ('team', 'TENSORCI_TEAM'),
      ('project', 'TENSORCI_PROJECT')
    )

    # Which instance vars are false-y?
    missing_creds = [c for c in configs if not getattr(self, c[0])]

    # Raise an error if any configs are missing
    if missing_creds:
      raise MissingCredentialsException(missing_creds)

  def construct_domain(self):
    # Slugify team & project name
    team_slug = to_slug(self.team or '')
    project_slug = to_slug(self.project or '')

    # Full domain has structure: <TEAM_SLUG>-<PROJECT_SLUG>.tensorci.com
    subdomain = '-'.join((team_slug, project_slug))
    host_domain = envs.TENSORCI_HOST_DOMAIN or definitions.host_domain

    return '.'.join((subdomain, host_domain))

  def request(self, handler, **kwargs):
    data = {
      'handler': handler,
      'data': kwargs.get('data')
    }

    try:
      # Send request data through the socket and wait for immediate response.
      self.socket.send(json.dumps(data))
      resp = self.socket.recv()
    except BaseException as e:
      raise SocketRequestException(e.message or e)

    try:
      # Response must be JSON parse-able
      resp = json.loads(resp)
    except:
      raise ResponseParseException(resp=resp)

    return resp

  def predict(self, **kwargs):
    return self.request('predict', **kwargs)