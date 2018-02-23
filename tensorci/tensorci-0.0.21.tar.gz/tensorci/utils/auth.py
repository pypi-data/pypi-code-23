"""
User-auth utilities file, exposing functions to get/create/delete a user's session.
Uses native netrc file for storing a user's session token.
"""
from tensorci import log
from tensorci.config import config
from tinynetrc import Netrc


def create(password=None):
  """
  Creates a new user session.

  Upserts a section to the netrc file, with the following specs:
    domain --> config.DOMAIN
      password --> 'password' param

  :param str password: Session token
  """
  # Get the native netrc file.
  netrc = Netrc()

  # Upsert domain/password group
  netrc[config.DOMAIN]['password'] = password

  # Save dat bish.
  netrc.save()


def delete():
  """
  Delete a user session.
  Removes the domain (config.DOMAIN) section from the native netrc file.
  """
  # Get the native netrc file.
  netrc = Netrc()

  # If our domain exists in the netrc file, remove it and save.
  if config.DOMAIN in netrc.keys():
    del netrc[config.DOMAIN]
    netrc.save()


def authed():
  """
  Check whether a user is logged in.

  :return: The user's auth status
  :rtype: bool
  """
  creds = get_creds()
  return bool(creds.get('password'))


def get_password():
  """
  Get password for the user's current session.

  :return: The netrc password associated with this domain
  :rtype: str
  """
  return get_creds().get('password')


def get_creds():
  """
  Get user credentials from the native netrc file.

  :return: Dict representation of netrc domain info
  :rtype: dict
  """
  return Netrc().get(config.DOMAIN, {})


def auth_required():
  """Check if user is authed and exit if not"""
  if not authed():
    log('You must be logged in to perfom that action.\n'
        'Use \'tensorci login\' if you already have an account, or visit '
        'https://tensorci.com to create a new account.')
    exit(1)