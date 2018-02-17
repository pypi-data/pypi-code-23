"""Ph — empowering p0rn users everywhere.

Usage:
  ph <search>... [--max=<n>] [--meta] [--download]
  ph (-h | --help)
  ph --version

Options:
  -h --help     Show this screen.
  --version     Show version.
  --max=<n>     Maximum number of videos to list [default: 25].
  --meta        Display video meta-data.
  --list        List categories.
  --download    Downloads videos.
"""

import crayons
from docopt import docopt
from phlib import PornHub


def main():
    args = docopt(__doc__, version='PH v1.0')
    ph = PornHub()

    if args['<search>']:
        for video in ph.search(args['<search>'], max=int(args['--max'])):
            print(crayons.white(video.title, bold=True))
            print(video.url)

            if args['--meta']:
                print('  View Count: {}, Percent Liked: {}'.format(video.meta['count'], video.meta['percent']))

            if args['--download']:
                video.download()

            print()


if __name__ == '__main__':

    main()

# ph =