import os
import webbrowser
from os_helper import curr_platform
from tensorci import log


def open_url(url):
  open_cmd = {
    'osx': 'open',
    'windows': 'explorer',
    'linux': 'xdg-open'
  }.get(curr_platform())

  if not open_cmd:
    webbrowser.open_new_tab(url)
    return

  os.system('{} {}'.format(open_cmd, url))