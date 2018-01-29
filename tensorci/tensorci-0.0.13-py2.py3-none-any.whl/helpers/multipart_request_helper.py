import os
from tensorci import log
from clint.textui.progress import Bar as ProgressBar


def create_callback(encoder):
  bar = ProgressBar(expected_size=encoder.len, filled_char='=')

  def callback(monitor):
    if monitor.bytes_read == encoder.len:
      if not hasattr(monitor, 'finished'):
        bar.show(monitor.bytes_read)
        setattr(monitor, 'finished', True)
        log('\nConverting dataset to database...')
    else:
      bar.show(monitor.bytes_read)

  return callback


class ProgressDownloadStream(object):

  def __init__(self, stream=None, expected_size=None, chunk_size=512):
    self.stream = stream
    self.prog_bar = ProgressBar(expected_size=expected_size, filled_char='=')
    self.progress = 0
    self.chunk_size = chunk_size

  def stream_to_file(self, path):
    assert not os.path.exists(path), 'File already exists at path: {}'.format(path)

    with open(path, 'wb') as f:
      for chunk in self.stream.iter_content(chunk_size=self.chunk_size):
        f.write(chunk)
        self.progress += int(len(chunk))
        self.prog_bar.show(self.progress)