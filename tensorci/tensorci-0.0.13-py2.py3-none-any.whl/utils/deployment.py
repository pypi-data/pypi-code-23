from tensorci.helpers.auth_helper import auth_required
from tensorci.utils.api import api
from tensorci.helpers.dynamic_response_helper import handle_dynamic_log_response
from tensorci.proj_config.config_file import ConfigFile
from tensorci.utils import gitconfig


def deploy(action=None):
  # Require authed user
  auth_required()

  # Load config file from disk into our ConfigFile model.
  config = ConfigFile().load()

  # Return if config file not valid.
  if not config.validate():
    exit(1)

  # Find this git project's remote url from inside .git/config
  git_repo, err = gitconfig.get_remote_url()

  # Error out if the remote git url couldn't be found.
  if err:
    log(err)
    return

  # Create deploy payload
  payload = {'git_url': git_repo}

  # Perform the deploy with a streaming response
  resp = api.post('/deployment/{}'.format(action), payload=payload, stream=True)

  # Handle response
  handle_dynamic_log_response(resp)