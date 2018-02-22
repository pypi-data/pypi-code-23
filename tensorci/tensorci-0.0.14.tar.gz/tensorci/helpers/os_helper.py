"""
Helper methods related to the current operating system
"""
from sys import platform

LINUX = 'linux'
OSX = 'osx'
WINDOWS = 'windows'


def curr_platform():
  """
  Get a string identifying the current operating system in use.

  Current supported return values:
    - 'linux'
    - 'osx'
    - 'windows'

  :return: The operating system in use
  :rtype: str
  """

  return {
    # Linux
    'linux': LINUX,
    'linux2': LINUX,

    # Mac
    'darwin': OSX,

    # Windows
    'win32': WINDOWS,
    'cygwin': WINDOWS
  }.get(platform)