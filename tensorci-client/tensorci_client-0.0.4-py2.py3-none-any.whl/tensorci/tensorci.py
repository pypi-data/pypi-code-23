import os
from api import AbstractApi
from definitions import auth_header_name
from slugify import slugify
from ex import *


class TensorCI:

  def __init__(self, client_id=None, client_secret=None, team=None, project=None):
    # set instance vars using environment vars as fallback values
    self.client_id = client_id or os.environ.get('TENSORCI_CLIENT_ID')
    self.client_secret = client_secret or os.environ.get('TENSORCI_CLIENT_SECRET')
    self.team = team or os.environ.get('TENSORCI_TEAM')
    self.project = project or os.environ.get('TENSORCI_PROJECT')

    # Create the API url from the project specified
    team_slug = slugify(self.team or '', separator='-', to_lower=True)
    project_slug = slugify(self.project or '', separator='-', to_lower=True)
    api_url = 'https://{}-{}.tensorci.com/api'.format(team_slug, project_slug)

    # Set up our authed API instance
    self.api = AbstractApi(base_url=api_url,
                           auth_header_name=auth_header_name,
                           auth_header_value=self.client_secret)

  def validate_creds(f):
    """
    Decorator validating the credentials required to make a successful API request.
    Raise a MissingCredentialsException if credentials are false-y.

    Credentials:
      - client_id
      - client_secret
      - project

    :return: decorated instancemethod
    """
    def wrapper(self, **kwargs):
      # Instance vars we're validating, with their associated backup env var names.
      creds = [
        ('client_id', 'TENSORCI_CLIENT_ID'),
        ('client_secret', 'TENSORCI_CLIENT_SECRET'),
        ('team', 'TENSORCI_TEAM'),
        ('project', 'TENSORCI_PROJECT')
      ]

      # Which instance vars are false-y?
      missing_creds = [c for c in creds if not getattr(self, c[0])]

      if missing_creds:
        raise MissingCredentialsException(missing_creds)

      return f(self, **kwargs)

    return wrapper

  @validate_creds
  def predict(self, features=None):
    payload = self.build_payload(features=features or {})
    return self.api.post('/predict', payload=payload)

  @validate_creds
  def update_dataset(self, records=None):
    payload = self.build_payload(records=records or [])
    return self.api.put('/dataset', payload=payload)

  def build_payload(self, **kwargs):
    payload = kwargs
    payload['client_id'] = self.client_id # Add client_id to each payload
    return payload