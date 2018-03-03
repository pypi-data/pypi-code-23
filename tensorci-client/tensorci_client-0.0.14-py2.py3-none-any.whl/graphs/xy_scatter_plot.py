import os
from tensorci_client.api import AbstractApi
from tensorci_client.definitions import train_cluster_header
from .data_series import DataSeries


class XYScatterPlot(object):

  def __init__(self, title=None, x_axis=None, y_axis=None):
    """
    Basic Usage:

    plot = XYScatterPlot(title='Loss vs. Iterations',
                         x_axis='Iterations',
                         y_axis='Loss')
    """
    # Set graph properties
    self.title = title
    self.x_axis = x_axis
    self.y_axis = y_axis

    if not title or not x_axis or not y_axis:
      raise BaseException('All current params required during instantiation.')

    self.uid = None
    self.deployment_uid = os.environ.get('DEPLOYMENT_UID')

    # Set up our authed API instance
    self.api = self.setup_api()

    if self.api:
      # Upsert this graph and get the uid
      self.upsert_graph()

  def upsert_graph(self):
    payload = {
      'title': self.title,
      'x_axis': self.x_axis,
      'y_axis': self.y_axis,
      'deployment_uid': self.deployment_uid
    }

    try:
      resp = self.api.post('/graph', payload=payload)
      data = resp.json() or {}
    except BaseException as e:
      print('Graph upsert failed: {}'.format(e))
      data = {}

    self.uid = data.get('uid')

  def setup_api(self):
    train_cluster_secret = os.environ.get('TENSORCI_TRAIN_SECRET')
    core_api_token = os.environ.get('CORE_API_TOKEN')

    if not train_cluster_secret or not core_api_token:
      return None

    return AbstractApi(base_url=(os.environ.get('CORE_URL') or 'https://api.tensorci.com/api'),
                       base_headers={'Core-Api-Token': core_api_token},
                       auth_header_name=train_cluster_header,
                       auth_header_value=train_cluster_secret)

  def series(self, name='default', color='#333'):
    return DataSeries(graph_uid=self.uid, name=name, color=color)