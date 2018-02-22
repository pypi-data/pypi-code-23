"""
Utility file exposing a consolidated 'deploy' method used by the following commands:

  $ tensorci train
  $ tensorci serve
  $ tensorci push

"""
from tensorci.proj_config.config_file import ConfigFile
from tensorci.utils import gitconfig
from tensorci.utils.api import api
from tensorci.utils.auth import auth_required


def deploy(action=None):
  """
  Perform a training deploy, API deploy, or both.

  :param str action:
    Deploy action to take.
    Supported values:
      - 'train'
      - 'serve'
      - 'push'
  """
  # Must already be logged in to perform this command.
  auth_required()

  # Load config file from disk into our ConfigFile model.
  config = ConfigFile().load()

  # Return if config file not valid.
  if not config.is_valid():
    exit(1)

  # Find this git project's remote url from inside .git/config
  git_repo = gitconfig.get_remote_url()

  # Create deploy payload.
  payload = {'git_url': git_repo}

  # Perform the deployment with a streaming response.
  resp = api.post('/deployment/{}'.format(action), payload=payload, stream=True)

  # Stream the response logs.
  resp.log_stream()