"""
Utility for interacting with the git repo of the current working directory
"""
import git
import os


def get_remote_url(remote='origin', required=True):
  """
  Read the git url for the given remote from the .git/config
  file of the current working directory.

  :param str remote: Git remote to look for
  :param bool required: Should the program exit if the url for this remote isn't found?
  :return: The git url for the given remote
  :rtype: str
  """
  # Handle case where git remote url isn't found. What to do depends
  # on whether this url is required to exist or not...
  def handle_not_found(err):
    if not required:
      return None
    log(err)
    exit(1)

  git_path = '{}/.git'.format(os.getcwd())

  # Whether the cwd is a git repository or not
  is_git_repo = os.path.exists(git_path) and os.path.isdir(git_path)

  # Cwd needs to be a git repo...
  if not is_git_repo:
    return handle_not_found('Current project is not a git repository.')

  config_path = '{}/config'.format(git_path)  # where the remote url should be found

  # Config file needs to exist...
  if not os.path.exists(config_path):
    return handle_not_found('.git/config file missing.')

  try:
    # Parse the git config file
    config = git.GitConfigParser([config_path], read_only=True)
  except KeyboardInterrupt:
    exit(0)
  except BaseException:
    return handle_not_found('Error parsing .git/config file.')

  try:
    # Get the url for the given remote
    url = config.get_value('remote "{}"'.format(remote), 'url')
  except KeyboardInterrupt:
    exit(0)
  except BaseException:
    return handle_not_found('Error determining remote origin url...make sure you have a git remote origin set up.')

  if not url.endswith('.git'):
    url += '.git'

  return str(url)