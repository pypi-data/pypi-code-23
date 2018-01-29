import click
import os
from tensorci import log
from tensorci.helpers.auth_helper import auth_required
from tensorci.utils.api import api, ApiException
from slugify import slugify
from tensorci.helpers.multipart_request_helper import create_callback
from tensorci.helpers.dynamic_response_helper import handle_error
from requests_toolbelt.multipart.encoder import MultipartEncoder, MultipartEncoderMonitor
from tensorci.utils import gitconfig


@click.command()
@click.option('--name', '-n')
@click.option('--file', '-f', required=True)
def dataset(name, file):
  """
  Create a TensorCI dataset from a JSON file.

  The dataset will be associated with the TensorCI project
  of the current working directory.

  Ex: tensorci create dataset -f mydataset.json
  """
  # Require authed user
  auth_required()

  # Find this git project's remote url from inside .git/config
  git_repo, err = gitconfig.get_remote_url()

  # Error out if the remote git url couldn't be found.
  if err:
    log(err)
    return

  # If dataset name was specified, slugify it.
  if name:
    dataset_slug = slugify(name, separator='-', to_lower=True)
  else:
    # Default dataset slug will just be the repo name
    dataset_slug = None

  # Make sure file actually exists
  if not os.path.exists(file):
    log('No file found at path {}'.format(file))
    return

  # Require dataset file to be JSON
  if not file.endswith('.json'):
    log('Dataset must be a JSON file (i.e. dataset.json)')
    return

  # Build payload
  payload = {
    'git_url': git_repo,
    'dataset_slug': dataset_slug,
    'file': ('dataset.json', open(file, 'rb'), 'application/json')
  }

  # Create a multipart encoder
  encoder = MultipartEncoder(fields=payload)

  # Create progress callback
  callback = create_callback(encoder)

  # Create a monitor for the encoder so we can track upload progress
  monitor = MultipartEncoderMonitor(encoder, callback)

  try:
    resp = api.post('/dataset',
                    data=monitor,
                    headers={'Content-Type': monitor.content_type},
                    mp_upload=True)
  except KeyboardInterrupt:
    return
  except ApiException as e:
    log(e.message)
    return

  if resp.status_code != 201:
    handle_error(resp)
    return

  log('Successfully created dataset.')