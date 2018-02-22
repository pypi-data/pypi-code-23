"""
Helper methods related to all-things URL
"""
import os
import os_helper
import re
import webbrowser
from tensorci import log


def open_url(url):
  """
  Open a URL in the default browser

  :param str url: URL to navigate to
  """
  # Ensure the url is a valid http/https url
  assert is_valid_url(url)

  # Get the current operating system in use
  current_os = os_helper.curr_platform()

  # Figure out which sys command to use to open the url
  # based on what the current OS is.
  open_cmd = {
    os_helper.OSX: 'open',
    os_helper.WINDOWS: 'explorer',
    os_helper.LINUX: 'xdg-open'
  }.get(current_os)

  # If using an unknown OS, try opening the url with
  # python's built-in 'webbrowser' library.
  if not open_cmd:
    webbrowser.open_new_tab(url)
    return

  # Open the url in the default browser
  os.system('{} {}'.format(open_cmd, url))


def is_valid_url(url):
  """
  Check if given url is a valid http/https url

  :param str url: Url to validate
  :return: Whether the url is valid
  :rtype: bool
  """
  url_regex = re.compile(
    r'^(?:http)s?://'  # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
    r'(?::\d+)?'  # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)

  return re.match(url_regex, url) is not None
