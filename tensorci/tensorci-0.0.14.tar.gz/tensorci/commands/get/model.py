import click
import os
from requests_toolbelt.downloadutils import stream
from tensorci import log
from tensorci.helpers.auth_helper import auth_required
from tensorci.helpers.file_helper import path_to_components, add_ext, filenames_with_ext
from tensorci.helpers.multipart_request_helper import ProgressDownloadStream
from tensorci.proj_config.config_file import ConfigFile
from tensorci.utils import gitconfig
from tensorci.utils.api import api


@click.command()
@click.option('--output', '-o')
def model(output):
  """
  Fetch the latest trained model.

  If the --output (-o) option is provided, the model file will be saved to
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

  # If output file was specified, create the absolute path from that.
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

  # Get components of model_path.
  direc, filename, ext = path_to_components(model_path)

  # Set ext to what type of file was fetched (only if output not specified).
  if not output:
    ext = resp.headers.get('Model-File-Type') or ext

  # Join filename with ext now that ext is solidified.
  filename_w_ext = add_ext(filename, ext)

  # Create the model file's directory if it doesn't exist yet.
  if direc and not os.path.exists(direc):
    os.makedirs(direc)

  # Specify path to save model.
  save_to = os.path.join(direc, filename_w_ext)

  # If the model file already exists, modify it with a number on the end to prevent overwriting.
  if os.path.exists(model_path):
    # Get a map of files in the directory that have the same ext as our desired save_to path.
    files_with_same_ext = filenames_with_ext(direc, ext)

    # Iterate until <filename><i>.<ext> is available, then create new save_to with that.
    i = 1
    while True:
      i += 1
      numbered_filename = add_ext('{}{}'.format(filename, i), ext)

      # If numbered file name hasn't been taken yet, use that name.
      if not files_with_same_ext.get(numbered_filename):
        save_to = os.path.join(direc, numbered_filename)
        break

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

  log('\nSaved model file to {}'.format(save_to.replace('{}/'.format(os.getcwd()), '')))