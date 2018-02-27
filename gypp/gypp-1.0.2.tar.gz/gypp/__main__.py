'''
Interact with GPG Encrypted password files in YAML format.

This script provides readonly access to a structured password
file in YAML syntax.

The YAML file has a structure like:

# Comments start with a "#"
DESCRIPTION: |
  This is a human readable description of this file.

RECIPIENTS:
  - list of
  - recipients of
  - the encrypted file

some_key:
  user: name of account (required)
  password: the password or phrase (required)
  name: human readable name of entry (optional)
  note: |
    optional note. The pipe char indicates that
    line breaks will be preserved, but the
    preceding space on each line will not.
  other: Other properties may be added as needed.

'''

import sys
import argparse
import logging
import pyperclip
import textwrap
from . import passwords_yaml


#==============================================
def main():
  parser = argparse.ArgumentParser(description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument('-l', '--log_level',
                      action='count',
                      default=0,
                      help='Set logging level, multiples for more detailed.')
  parser.add_argument('-k', '--key',
                      default=None,
                      help='Key of entry')
  parser.add_argument('-s', '--show',
                      default=False,
                      action='store_true',
                      help='Show entry at key')
  parser.add_argument('-p', '--print',
                      default=False,
                      action='store_true',
                      help='Print out password as opposed to clipboard')
  parser.add_argument('-c', '--command',
                      default=False,
                      action='store_true',
                      help='Show command for file encryption')
  parser.add_argument('source',
                      nargs='?',
                      default=None,
                      help='Path to password source')
  args = parser.parse_args()
  # Setup logging verbosity
  levels = [logging.WARNING, logging.INFO, logging.DEBUG]
  level = levels[min(len(levels) - 1, args.log_level)]
  logging.basicConfig(level=level,
                      format="%(asctime)s %(levelname)s %(message)s")
  #override logging in gnupg module
  glogger = logging.getLogger('gnupg')
  glogger.setLevel(logging.ERROR)

  if args.source is None:
    logging.error("source is required.")
    sys.exit(1)

  p = passwords_yaml.PasswordsYAML(args.source)
  if not p.load_ok:
    logging.error("Unable to load from source: %s", args.source)
    sys.exit(1)

  if args.command:
    print( p.encryptCommand() )
    sys.exit(0)

  if args.key is None:
    keys = sorted(p.keys())
    print("Source: {}".format(p.source))
    print("Description: {}".format(p._description))
    print("Keys available:")
    for key in keys:
      name = key
      try:
        name = p.entry(key)['name']
      except KeyError:
        pass
      print("  {:18}: {}".format(key,name))
    sys.exit(0)

  if args.show:
    entry = p.entry(args.key)
    for k in entry:
      v = entry[k]
      if k != "password":
        if k == "note":
          print("{:8}".format(k))
          print(textwrap.indent(v,'  '))
        else:
          print("{:8} : {}".format(k,v))
    sys.exit(0)

  if args.print:
    print(p.password(args.key))
    sys.exit(0)

  pyperclip.copy( p.password(args.key) )
  logging.info("Password for {} placed on clipboard.".format(args.key) )


if __name__ == "__main__":
  main()
