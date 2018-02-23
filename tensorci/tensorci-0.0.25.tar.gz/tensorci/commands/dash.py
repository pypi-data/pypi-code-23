import click
import os
import re
from tensorci import log
from tensorci.config import config
from tensorci.helpers import url_helper
from tensorci.proj_config.config_file import ConfigFile
from tensorci.utils import gitconfig
from urlparse import urlparse


@click.command()
def dash():
  """
  Open TensorCI dashboard for this project.

  Ex: tensorci dash
  """
  # Find this git project's remote url from inside .git/config
  git_repo = gitconfig.get_remote_url()

  # Parse out team and repo from remote git_url
  path_match = re.match('/(.*).git', urlparse(git_repo).path)
  team = None
  repo = None

  if path_match:
    path = path_match.groups()[0]
    team, repo = path.split('/')

  if not team or not repo:
    log('Error parsing remote git repo: {}'.format(git_repo))
    return

  # Build dashboard url from TensorCI Dashboard url, the team, and the repo.
  url = '{}/{}/{}'.format(config.DASH_URL, team.lower(), repo.lower())

  try:
    # Open dashboard url in new tab of default browser
    url_helper.open_url(url)
  except BaseException:
    log('Failed to open URL: {}'.format(url))