import click
from tensorci import log
from tensorci.utils import auth


@click.command()
def logout():
  """
  Logout of TensorCI.

  Ex: tensorci logout
  """
  # Remove authed session from netrc
  auth.delete()
  log('Successfully logged out.')