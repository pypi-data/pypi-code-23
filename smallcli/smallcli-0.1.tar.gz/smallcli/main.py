from __future__ import unicode_literals
import os
import sys
from six import text_type
from smallcli.libs.shell import Shell


def main(argv):
    parser = argparse.ArgumentParser("Knet Test app")
    parser.add_argument("--input-file", required=True, help="connections Step")
    argv = sys.argv[1:]
    cpath = "smallcli/commands"
    cprefix = "commands."
    cli = Shell(appname="suresh-cli", symbol="#", cmdpath=cpath,
                cmdprefix=cprefix)
    cli()
    print "exiting"

# if __name__ == "__main__":
#    main(sys.argv)
