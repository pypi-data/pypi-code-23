"""
Helper methods and classes related to multi-part file uploads or downloads
"""
import os
from clint.textui.progress import Bar as ProgressBar
from tensorci import log


def create_callback(encoder, completion_log=None):
  """
  Create a progress callback function for a multi-part file upload

  :param encoder:
    Multipart file encoder
    :type: requests_toolbelt.multipart.encoder.MultipartEncoder
  :param str completion_log:
    Log to display when the file upload has completed
  :return: Upload progress callback function
  :rtype: function
  """
  # Create a progress bar with the given size, specifying which character to show for progress.
  bar = ProgressBar(expected_size=encoder.len, filled_char='=')

  # Function to be called as the upload progresses
  def callback(monitor):
    # If upload has completed...
    if monitor.bytes_read == encoder.len:
      # Hack around that this callback is called twice when completed.
      if not hasattr(monitor, 'finished'):
        setattr(monitor, 'finished', True)

        # Show upload progress.
        bar.show(monitor.bytes_read)

        # Display completion log if provided.
        if completion_log:
          log(completion_log)
    else:
      # Show upload progress.
      bar.show(monitor.bytes_read)

  return callback


class ProgressDownloadStream(object):
  """
  Progress bar buffer class that can monitor a file download by displaying
  progress to the user while also writing to the desired file.

  Basic usage:

    download_stream = ProgressDownloadStream(stream=api_response_obj,
                                             expected_size=total_file_bytes)

    download_stream.stream_to_file(desired_file_path)

  """

  def __init__(self, stream=None, expected_size=None, chunk_size=512):
    """
    :param stream:
      Streaming API response object returned by the 'requests' library
      :type: requests.Response
    :param int expected_size:
      Total size of file being downloaded (in bytes)
    :param int chunk_size:
      Chunk size to use when iterating over streamed response content
    """
    self.stream = stream
    self.prog_bar = ProgressBar(expected_size=expected_size, filled_char='=')
    self.progress = 0
    self.chunk_size = chunk_size

  def stream_to_file(self, path):
    """
    Download file to given path and display progress to user

    :param str path: Desired file path
    """
    # Using default state of files being overwritten for now
    if os.path.exists(path):
      os.remove(path)

    # Stream downloaded contents to file and show progress
    with open(path, 'wb') as f:
      for chunk in self.stream.iter_content(chunk_size=self.chunk_size):
        f.write(chunk)
        self.progress += int(len(chunk))
        self.prog_bar.show(self.progress)