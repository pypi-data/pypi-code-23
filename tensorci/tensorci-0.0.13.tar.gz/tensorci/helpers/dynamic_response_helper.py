from tensorci.definitions import tci_keep_alive
from tensorci import log


def handle_dynamic_log_response(resp):
  if resp.status_code != 200:
    handle_error(resp)
    return

  if resp.headers.get('Content-Type') == 'application/json':
    return handle_json_result(resp)
  else:
    handle_stream_result(resp)


def handle_json_result(resp):
  try:
    data = resp.json() or {}
  except KeyboardInterrupt:
    exit(0)
  except:
    data = {}

  if data.get('log'):
    log(data.get('log'))

  return data


def handle_stream_result(resp):
  try:
    for line in resp.iter_lines(chunk_size=10):
      if line and line != tci_keep_alive:
        log(line)
  except KeyboardInterrupt:
    exit(0)
  except BaseException as e:
    log('Error while parsing logs: {}'.format(e))


def handle_error(resp):
  try:
    data = resp.json() or {}
  except KeyboardInterrupt:
    exit(0)
  except:
    data = {}

  if data.get('log'):
    log(data.get('log'))
    return

  if data.get('error'):
    log(data.get('error'))
    return

  log('Unknown error occured with status code {}'.format(resp.status_code))