import json
import os
from definitions import *
from exps import *
from helpers import fresh_request_uid
from redis import StrictRedis


class RestfulRedisClient(object):

  def __init__(self, url=None, channel=default_channel):
    url = url or os.environ.get('REDIS_URL') or default_url
    self.redis = StrictRedis.from_url(url=url)
    self.channel = channel

  def request(self, target, data=None, timeout=60):
    data = data or {}

    # Create a uid for this specific request
    request_uid = fresh_request_uid()

    # Wrap custom data into payload, along with request uid
    payload = {
      'target': target,
      'data': data,
      'request_uid': request_uid
    }

    # Push the request data to the request queue
    self.redis.rpush(self.channel, json.dumps(payload))

    # Wait for response
    resp = self.redis.blpop(request_uid, timeout=timeout)

    # Response must exist or it's a timeout error
    if resp is None:
      raise RequestTimeout()

    try:
      # Attempt to parse JSON response
      parsed_resp = json.loads(resp[1])
    except:
      raise JSONParseException()

    succeeded = parsed_resp.get('ok')
    resp_data = parsed_resp.get('data')

    # Ensure request succeeded
    if not succeeded:
      raise ResponseError(resp_data)

    # Delete request key
    self.redis.delete(request_uid)

    return resp_data