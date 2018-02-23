import click
import os
from tensorci import log
from tensorci.helpers.file_helper import create_model_save_path, upsert_parent_dirs, extract_in_place
from tensorci.helpers.multipart_request_helper import ProgressDownloadStream
from tensorci.proj_config.config_file import ConfigFile
from tensorci.utils import gitconfig
from tensorci.utils.api import api
from tensorci.utils.auth import auth_required


@click.command()
@click.option('--output', '-o')
def model(output):
  """
  Fetch the latest trained model.

  If the --output (-o) option is provided, the model will be saved to
  that specified file path. Otherwise, it will be saved to the value of
  the 'model' key provided in .tensorci.yml.

  Ex: tensorci get model
  """
  # Must already be logged in to perform this command.
  auth_required()

  # Find this git project's remote url from inside .git/config
  git_repo = gitconfig.get_remote_url()

  # Build the payload.
  payload = {'git_url': git_repo}

  try:
    # Download the model file.
    resp = api.get('/repo/model', payload=payload, stream=True)
  except KeyboardInterrupt:
    return

  # If output file was specified, create an absolute path from that.
  if output:
    if output.startswith('/'):  # already abs path
      model_path = output
    else:  # create abs path from cwd
      model_path = os.path.join(os.getcwd(), output)
  else:
    # Load our config file.
    config = ConfigFile().load()

    # Get the model file's absolute path based on cwd.
    model_path = config.abs_model_path()

  # Get the path where we should save the model.
  model_ext = resp.headers.get('Model-File-Type')
  save_to = create_model_save_path(model_path, model_ext)

  # Ensure all parent dirs of 'save_to' file path exist before saving the model.
  upsert_parent_dirs(save_to)

  # Stream model contents to file.
  try:
    total_file_bytes = int(resp.headers.get('Content-Length'))

    # Set up progress bar buffer that will monitor the download while also writing to our desired file.
    dl_stream = ProgressDownloadStream(stream=resp.response_obj, expected_size=total_file_bytes)
    dl_stream.stream_to_file(save_to)
  except KeyboardInterrupt:
    return
  except BaseException as e:
    log('\nError streaming model file to path {} with error: {}'.format(save_to, e))
    return

  # Unzip model file if it's an archive.
  if save_to.endswith('.zip'):
    saved_to = extract_in_place(save_to)
  else:
    saved_to = save_to

  # Get the relative path to the saved model for display purposes.
  relative_saved_to = saved_to.replace('{}/'.format(os.getcwd()), '')

  log('\nSaved model to {}'.format(relative_saved_to))