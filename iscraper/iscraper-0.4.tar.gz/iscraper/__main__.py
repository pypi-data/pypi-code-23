import argparse
from .get_iplayer import download_history, get_iplayer
from .search import episodes, programme_id, films

#iscraper.py [--simulate] title output-dir

parser = argparse.ArgumentParser(prog='iscraper')
search = parser.add_mutually_exclusive_group(required=True)
search.add_argument('-t', '--title', type=str, 
                    help='title of series to download')
search.add_argument('-f', '--films', action='store_true',
                    help='download films')
parser.add_argument('outputdir', help='directory to download to')
parser.add_argument('-s', '--simulate', action='store_true',
                    help='find programmes but do not download')
args = parser.parse_args()
print(args)
if args.films:
  progs = films()
  print('Available films:')
else:
  prog_id = programme_id(args.title)
  if prog_id:
    progs = episodes(prog_id)
    print('Available episodes:')
  else:
    print('No episodes available.')
for p in progs:
  print('\t', p)
history = download_history()
progs = [p for p in progs if p['pid'] not in history]
for prog in progs:
  print('Downloading: ', prog)
  if not args.simulate:
    get_iplayer(prog, args.outputdir)
  else:
    print('Simulation only, no download')
