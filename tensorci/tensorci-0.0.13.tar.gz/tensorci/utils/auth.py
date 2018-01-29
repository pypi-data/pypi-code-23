from tinynetrc import Netrc
from tensorci.config import config


def create(password=None):
  netrc = Netrc()

  # delete old creds
  delete(netrc)

  # upsert new creds
  netrc[config.DOMAIN]['password'] = password

  # save dat bish
  netrc.save()


def delete(netrc=None):
  netrc = netrc or Netrc()

  if config.DOMAIN in netrc.keys():
    del netrc[config.DOMAIN]
    netrc.save()


def authed():
  creds = get_creds()
  return bool(creds.get('password'))


def get_password():
  return get_creds().get('password')


def get_creds():
  return Netrc().get(config.DOMAIN)