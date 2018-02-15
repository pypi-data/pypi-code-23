import argparse
from .get_iplayer import download_history, get_iplayer
from .search import episodes, programme_id

#iscraper.py [--simulate] title output-dir

parser = argparse.ArgumentParser()
parser.add_argument('title', help='programme title to download')
parser.add_argument('outputdir', help='directory to download to')
parser.add_argument('-s', '--simulate', action='store_true',
                    help='find programmes but do not download')
args = parser.parse_args()
print(args)
prog_id = programme_id(args.title)
if prog_id:
  progs = episodes(prog_id)
  print('Available episodes:')
  for p in progs:
    print('\t', p)
  history = download_history()
  progs_to_get = [p for p in progs if p['pid'] not in history]

  for prog in progs_to_get:
    print('Downloading: ', prog)
    if not args.simulate:
      get_iplayer(prog, args.outputdir)
    else:
      print('Simulation only, no download')
else:
  print('No episodes available.')
