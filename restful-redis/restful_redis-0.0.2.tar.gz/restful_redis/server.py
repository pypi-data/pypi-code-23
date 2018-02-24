import json
import os
from definitions import *
from redis import StrictRedis
from exps import *


class RestfulRedisServer(object):

  def __init__(self, url=None, channel=default_channel, handlers=None):
    url = url or os.environ.get('REDIS_URL') or default_url
    self.redis = StrictRedis.from_url(url=url)
    self.channel = channel
    self.handlers = handlers or {}

  def run(self):
    while True:
      # Block infinitely until request received
      request = self.redis.blpop(self.channel)

      try:
        # Attempt to parse JSON request data
        payload = json.loads(request[1]) or {}
      except:
        raise JSONParseException(request)

      # Validate request body
      request_uid = payload.get('request_uid')
      target = payload.get('target')
      req_data = payload.get('data', {})

      if not request_uid or not target:
        raise InvalidRequestException(payload)

      handler = self.handlers.get(target)

      if not handler:
        raise UnknownHandlerException(handler)

      resp = {'ok': True}

      try:
        # Call handler function
        resp['data'] = handler(req_data)
      except BaseException as e:
        resp['ok'] = False
        resp['data'] = e.message

      # Push the JSON response to channel=request_uid
      self.redis.rpush(request_uid, json.dumps(resp))

  def register_handler(self, name, target):
    self.handlers[name] = target
