import subprocess
import os

def file_prefix(prog):
  return '{}-s{:02}e{:02}-{}'.format(
    prog['brand'],
    prog['series'],
    prog['episode'],
    prog['episode_title']
  )
  pass

def get_iplayer(prog, output_dir):
  subprocess.call([
    '/usr/bin/get-iplayer',
    '--type' ,'tv',
    '--pid', prog['pid'],
    '--file-prefix', file_prefix(prog),
    '--output', output_dir,
  ])

def download_history():
  with open(os.path.expanduser('~/.get_iplayer/download_history')) as downloads:
    return [d.split('|',1)[0] for d in downloads]
