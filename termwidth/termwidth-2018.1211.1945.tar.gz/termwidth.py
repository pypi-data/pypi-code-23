import logging, sys

_log = logging.getLogger(__name__); debug, info, warn, error = _log.debug, _log.info, _log.warn, _log.error


DEFAULT = (80, 25)


def getTermWidth():
  ''' Function that returns the terminal width. '''
  ok, x, y = _tryCurses()
  if ok: return x, y
  if sys.platform == 'win32':
    ok, x, y = _tryWindows()
    if ok: return x, y
    return DEFAULT
  ok, x, y = _tryTput()
  if ok: return x, y
  ok, x, y = _tryPosix()
  return x, y

def _tryCurses():
  ''' Attempts to read curses module. '''
  try:
    import curses
    width, height = DEFAULT
    def func(scr):
      nonlocal width, height
      height, width = scr.getmaxyx()
    curses.wrapper(func)
    return (True, width, height)
  except:
    return (False, DEFAULT[0], DEFAULT[1])

def _tryTput():
  try:
    import subprocess
    try:
      width = int(subprocess.check_output(['tput', 'cols']))
    except OSError as E:
      debug("Invalid Command 'tput': exit status %d" % E.errno)
    except subprocess.CalledProcessError as F:
      debug("Command 'tput' returned non-zero exit status: %d"  % F.returncode)
    else:
      return (True, width, DEFAULT[1])
  except:
    return (False, DEFAULT[0], DEFAULT[1])

def _tryWindows():
  try:
    from ctypes import windll, create_string_buffer  # from: https://code.activestate.com/recipes/440694-determine-size-of-console-window-on-windows/
    h = windll.kernel32.GetStdHandle(-12)  # stdin handle is -10, stdout handle is -11, stderr handle is -12
    csbi = create_string_buffer(22)
    res = windll.kernel32.GetConsoleScreenBufferInfo(h, csbi)
    if res:
      import struct
      (bufx, bufy, curx, cury, wattr, left, top, right, bottom, maxx, maxy) = struct.unpack("hhhhHhhhhhh", csbi.raw)
      width = right - left + 1
      height = bottom - top + 1
      return (True, width, height)
    else:
      return (False, DEFAULT[0], DEFAULT[1])  # can't determine actual size - return default values
  except:
    return (False, DEFAULT[0], DEFAULT[1])

def _tryPosix():
  width = 0
  try:  # Posix attempt
    import struct, fcntl, termios
    s = struct.pack('HHHH', 0, 0, 0, 0)
    x = fcntl.ioctl(1, termios.TIOCGWINSZ, s)
    width = struct.unpack('HHHH', x)[1]
    return (True, width, DEFAULT[1])
  except IOError: pass
  if width <= 0:  # environment variable check
    try: width = int(os.environ['COLUMNS'])
    except: pass
  if width <= 0:
    return (False, DEFAULT[0], DEFAULT[1])
  return (True, width, DEFAULT[1])


if __name__ == '__main__':
  assert (190, 45) == getTermWidth()  # this only works on my development machine
