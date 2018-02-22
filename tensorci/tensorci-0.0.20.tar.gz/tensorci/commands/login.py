import click
from tensorci import log
from tensorci.definitions import auth_header_name
from tensorci.utils import auth
from tensorci.utils.api import api


@click.command()
@click.option('--username', '-u')
@click.option('--password', '-p')
def login(username, password):
  """
  Login as a TensorCI user.

  If --username (-u) and --password (-p) are not provided as options, the user
  will be prompted for these values.

  Ex: tensorci login
  """
  log('Enter your TensorCI credentials:')

  # Prompt user for username unless already provided
  username = (username or click.prompt('GitHub Username')).strip()

  # Can't proceed without username :/
  if not username:
    log('GitHub username is required.')
    return

  # Prompt user for password unless already provided
  pw = (password or click.prompt('CLI Password', hide_input=True)).strip()

  # Can't proceed without pw :/
  if not pw:
    log('CLI password is required.')
    return

  # Construct API payload
  payload = {
    'username': username,
    'password': pw,
    'provider': 'github'  # hard-coding for now since only supporting GH
  }

  try:
    resp = api.post('/provider_user/login', payload=payload, log_on_error=False, exit_on_error=False)
  except KeyboardInterrupt:
    return

  # Log the error if the login failed.
  if not resp.ok:
    log('Authentication failed.')
    return

  # Get the user_token provided in the response headers
  user_token = resp.headers.get(auth_header_name)

  # Create a new authed session in netrc with the user_token as the password
  auth.create(password=user_token)

  log('Logged in as {}.'.format(username))