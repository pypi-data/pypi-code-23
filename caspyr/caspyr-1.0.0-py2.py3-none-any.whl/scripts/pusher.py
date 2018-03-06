#!/usr/bin/env python
"""Usage:
  pusher [options] <title>

Options:
  -b BODY, --body BODY  Message text (default: {id}|{time})
  -i ID, --id ID        Message topic or device ID [default: news]
  -e SEC, --expiry SEC  Seconds before message expires [default: 60*60*24:int]
  --log LEVEL           CRITICAL|ERROR|WARN(ING)|[default: INFO]|DEBUG
"""
from argopt import argopt
from os import getenv
import sys
import requests
from time import ctime
import logging

__all__ = ["run", "RunArgs", "script", "main"]
__version__ = "0.3.0"
URL = "https://fcm.googleapis.com/fcm/send"


def run(args):
  """@param args: RunArgs"""
  log = logging.getLogger(__name__)

  if not args.id.startswith('/') and len(args.id) < 99:
    # inject short topic id into message body if necessary
    if args.body is None:
      args.body = str(args.id)
    else:
      args.body = args.body.replace("{id}", args.id)
    # prefix /topics/
    args.id = "/topics/" + args.id

  # long id with no body -> time
  if args.body is None:
    args.body = "{time}"
  args.body = args.body.\
      replace("{time}", ctime()).\
      replace("{title}", args.title)
  log.debug(args)

  auth_key = getenv("FCM_PUSHER_AUTH_KEY", None)
  if auth_key is None:
    raise EnvironmentError("Please set FCM_PUSHER_AUTH_KEY and try again")

  headers = dict(Authorization="key=" + auth_key)
  data = dict(to=args.id, priority="high", time_to_live=args.expiry,
              notification=dict(title=args.title,
                                body=args.body,
                                sound="default"))
  log.debug(str(headers))
  log.debug(str(data))
  r = requests.post(URL, headers=headers, json=data)
  log.info(r.content)
  return r.json()


class RunArgs(object):
  def __init__(self, title, body=None, id="news", expiry=60 * 60 * 24):
    """Default arguments for run()"""
    self.body = body
    self.id = id
    self.expiry = expiry
    self.title = title


def script(*args, **kwargs):
  """alias for run(RunArgs(...))"""
  return run(RunArgs(*args, **kwargs))


def main():
  args = argopt(__doc__, version=__version__).parse_args()
  if args.body == 'None':
    args.body = None
  logging.basicConfig(level=getattr(logging, args.log, logging.NOTSET))
  log = logging.getLogger(__name__)
  log.debug(args)
  run(args)


if __name__ == "__main__":
  sys.exit(main() or 0)
