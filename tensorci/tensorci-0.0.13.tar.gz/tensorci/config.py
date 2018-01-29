import os
from utils.env import env


class Config:
  DEBUG = True


class ProdConfig(Config):
  DEBUG = False

  def __init__(self):
    self.DOMAIN = os.environ.get('TENSORCI_DOMAIN') or 'api.tensorci.com'
    self.DASH_URL = os.environ.get('TENSORCI_DASH_URL') or 'https://app.tensorci.com'
    self.API_URL = os.environ.get('TENSORCI_API_URL') or 'https://{}/api'.format(self.DOMAIN)


class StagingConfig(Config):
  DEBUG = False

  def __init__(self):
    self.DOMAIN = os.environ.get('TENSORCI_DOMAIN') or 'staging.api.tensorci.com'
    self.DASH_URL = os.environ.get('TENSORCI_DASH_URL') or 'https://app.staging.tensorci.com'
    self.API_URL = os.environ.get('TENSORCI_API_URL') or 'https://{}/api'.format(self.DOMAIN)


class DevConfig(Config):

  def __init__(self):
    self.DOMAIN = os.environ.get('TENSORCI_DOMAIN') or 'dev.api.tensorci.com'
    self.DASH_URL = os.environ.get('TENSORCI_DASH_URL') or 'https://app.dev.tensorci.com'
    self.API_URL = os.environ.get('TENSORCI_API_URL') or 'https://{}/api'.format(self.DOMAIN)


class TestConfig(Config):

  def __init__(self):
    self.DOMAIN = os.environ.get('TENSORCI_DOMAIN') or 'localhost'
    self.DASH_URL = os.environ.get('TENSORCI_DASH_URL') or 'http://localhost:3000'
    self.API_URL = os.environ.get('TENSORCI_API_URL') or 'http://{}/api'.format(self.DOMAIN)


def get_config():
  config_class = globals().get('{}Config'.format(env().capitalize()))
  return config_class()


config = get_config()