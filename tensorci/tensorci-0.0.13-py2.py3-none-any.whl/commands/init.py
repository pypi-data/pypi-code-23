import os
import click
from tensorci import log
from tensorci.helpers.auth_helper import auth_required
from tensorci.utils import gitconfig
from tensorci.utils.api import api, ApiException
from tensorci.proj_config.config_file import ConfigFile


@click.command()
def init():
  """
  Create a new TensorCI project.

  This command will fail if the current working directory is not the base
  of a git repository.

  Upon success, a new config file named .tensorci.yml will be created in
  the current working directory.

  Ex: tensorci init
  """
  # Require authed user.
  auth_required()

  # Create a ConfigFile class instance to represent our config file
  config = ConfigFile()

  # If the current directory already has a config file, tell the user and exit.
  if os.path.exists(config.path):
    log('TensorCI project already exists.')
    return

  # Find this git project's remote url from inside .git/config
  git_repo, err = gitconfig.get_remote_url()

  # Error out if the remote git url couldn't be found.
  if err:
    log(err)
    return

  try:
    # Register the git repo as a TensorCI repo (upsert)
    api.post('/repo/register', payload={'git_url': git_repo})
  except KeyboardInterrupt:
    return
  except ApiException as e:
    log(e.message)
    return

  # Add placeholders for the config file values
  config.set_value('model', 'path/to/model/file')
  config.set_value('prepro_data', 'module1.module2:function')
  config.set_value('train', 'module1.module2:function')
  config.set_value('test', 'module1.module2:function')
  config.set_value('predict', 'module1.module2:function')
  config.set_value('reload_model', 'module1.module2:function')

  # Write the config file to the user's project.
  config.save()

  log('Initialized new TensorCI project.\nGenerated new config file at {}'.format(config.FILE_NAME))