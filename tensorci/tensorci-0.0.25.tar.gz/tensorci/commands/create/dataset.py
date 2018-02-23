import click
import os
from requests_toolbelt.multipart.encoder import MultipartEncoder, MultipartEncoderMonitor
from tensorci import log
from tensorci.helpers.multipart_request_helper import create_callback
from tensorci.utils import gitconfig
from tensorci.utils.api import api
from tensorci.utils.auth import auth_required
from tensorci.utils.slug import to_slug


@click.command()
@click.option('--name', '-n')
@click.option('--file', '-f', required=True)
def dataset(name, file):
  """
  Create a TensorCI dataset from a JSON file.
  The dataset will be associated with the TensorCI project of the current working directory.
  The dataset's name will default to the name of the project if not specified.

  Ex: tensorci create dataset -f mydataset.json
  """
  # Must already be logged in to perform this command.
  auth_required()

  # Find this git project's remote url from inside .git/config
  git_repo = gitconfig.get_remote_url()

  # If dataset name was specified, slugify it.
  if name:
    dataset_slug = to_slug(name)
  else:
    # Default dataset slug will just be the repo name.
    dataset_slug = None

  # Make sure file actually exists.
  if not os.path.exists(file):
    log('No file found at path {}'.format(file))
    return

  # Require dataset file to be JSON.
  if not file.endswith('.json'):
    log('Dataset must be a JSON file (i.e. dataset.json)')
    return

  # Build the payload.
  payload = {
    'git_url': git_repo,
    'dataset_slug': dataset_slug,
    'file': ('dataset.json', open(file, 'rb'), 'application/json')
  }

  # Create a multipart encoder.
  encoder = MultipartEncoder(fields=payload)

  # Create progress callback, specifying message to show when upload completes.
  callback = create_callback(encoder,
                             completion_log='\nConverting dataset to database...')

  # Create a monitor for the encoder so we can track upload progress.
  monitor = MultipartEncoderMonitor(encoder, callback)

  headers = {'Content-Type': monitor.content_type}

  try:
    # Upload the dataset.
    api.post('/dataset', headers=headers, mp_upload_monitor=monitor)
  except KeyboardInterrupt:
    return

  log('Successfully created dataset.')