from sys import platform


def curr_platform():
  if platform in ('linux', 'linux2'):
    return 'linux'

  if platform == 'darwin':
    return 'osx'

  if platform in ('win32', 'cygwin'):
    return 'windows'

  return None