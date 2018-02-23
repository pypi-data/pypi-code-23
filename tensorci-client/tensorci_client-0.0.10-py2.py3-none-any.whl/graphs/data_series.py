import json
from tensorci_client.pyredis import redis
from tensorci_client.definitions import graph_update_queue


class DataSeries(object):

  def __init__(self, graph_uid=None, name='default', color='#333'):
    self.graph_uid = graph_uid
    self.name = name
    self.color = color

  def add_data_point(self, **kwargs):
    if not redis or not self.graph_uid:
      return

    payload = kwargs
    payload['graph_uid'] = self.graph_uid
    payload['series'] = self.name
    payload['color'] = self.color

    try:
      redis.rpush(graph_update_queue, json.dumps(payload))
    except BaseException as e:
      print('Error pushing to redis graph event queue: {}'.format(e))