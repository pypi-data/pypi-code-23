import click
import os
from tensorci import log
from tensorci.helpers.auth_helper import auth_required
from tensorci.helpers.dynamic_response_helper import handle_error
from tensorci.utils.api import api, ApiException
from requests_toolbelt.downloadutils import stream
from tensorci.helpers.file_helper import break_file, add_ext, filenames_with_ext
from tensorci.helpers.multipart_request_helper import ProgressDownloadStream
from tensorci.proj_config.config_file import ConfigFile
from tensorci.utils import gitconfig


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
  # Require authed user
  auth_required()

  # Find this git project's remote url from inside .git/config
  git_repo, err = gitconfig.get_remote_url()

  # Error out if the remote git url couldn't be found.
  if err:
    log(err)
    return

  # Build our payload
  payload = {'git_url': git_repo}

  try:
    # Make streaming request
    resp = api.get('/repo/model', payload=payload, stream=True)
  except KeyboardInterrupt:
    return
  except ApiException as e:
    log(e.message)
    return

  # Handle error if request not successful
  if resp.status_code != 200:
    handle_error(resp)
    return

  # if output file was specified, create the absolute path from that
  if output:
    if output.startswith('/'):  # already abs path
      model_path = output
    else:  # create abs path from cwd
      model_path = os.path.join(os.getcwd(), output)
  else:
    # Load our config file
    config = ConfigFile().load()

    # Get the model file's absolute path based on cwd
    model_path = config.abs_model_path()

  # Get components of model_path
  direc, filename, ext = break_file(model_path)

  # Set ext to what type of file was fetched (only if output not specified)
  if not output:
    ext = resp.headers.get('Model-File-Type') or ext

  # Join filename with ext now that ext is solidified
  filename_w_ext = add_ext(filename, ext)

  # Create the model file's directory if it doesn't exist yet
  if direc and not os.path.exists(direc):
    os.makedirs(direc)

  # Path we're gonna save model to
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

      # if numbered file name hasn't been taken yet, use that name.
      if not files_with_same_ext.get(numbered_filename):
        save_to = os.path.join(direc, numbered_filename)
        break

  try:
    total_file_bytes = int(resp.headers.get('Content-Length'))

    # Set up progress bar buffer that will monitor the download while also writing to our desired file.
    dl_stream = ProgressDownloadStream(stream=resp, expected_size=total_file_bytes)
    dl_stream.stream_to_file(save_to)
  except KeyboardInterrupt:
    return
  except BaseException as e:
    log('\nError streaming model file to path {} with error: {}'.format(save_to, e))
    return

  log('\nSaved model file to {}'.format(save_to.replace('{}/'.format(os.getcwd()), '')))