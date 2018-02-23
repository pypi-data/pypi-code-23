"""
Utility for determining which dev environment is currently being used
"""
import os

# Recognized environments
TEST = 'test'
DEV = 'dev'
STAGING = 'staging'
PROD = 'prod'

ENV = (os.environ.get('TENSORCI_ENVIRON') or PROD).lower()

# Ensure the environment is a supported value
assert ENV in (TEST, DEV, STAGING, PROD)


def env():
  """
  Get the current environment's string representation

  Potential values:
    - 'test'
    - 'dev'
    - 'staging'
    - 'prod'

  :return: The current environment
  :rtype: str
  """
  return ENV


def is_test():
  """
  Are we testing?

  :returns: Whether this is a test environment
  :rtype: bool
  """
  return ENV == TEST


def is_dev():
  """
  Are we on a dev environment?

  :returns: Whether this is a dev environment
  :rtype: bool
  """
  return ENV == DEV


def is_staging():
  """
  Are we on staging?

  :returns: Whether this is a staging environment
  :rtype: bool
  """
  return ENV == STAGING


def is_prod():
  """
  Are we on prod?

  :returns: Whether this is a prod environment
  :rtype: bool
  """
  return ENV == PROD