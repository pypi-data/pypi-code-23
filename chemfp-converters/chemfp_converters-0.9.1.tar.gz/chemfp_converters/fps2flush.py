from __future__ import print_function, absolute_import

import argparse
import chemfp

from . import flush
from . import cmdsupport
from .cmdsupport import die

epilog = """

A Flush file stores identifiers and fingerprints in a file with the
extension ".flush". The Flush format is used by Dave Cosgrove's
fingerprint tools at https://github.com/OpenEye-Contrib/Flush .

If you do not specify an --output filename then the flush file output
(which is a binary file) will be sent to stdout.

Example: 

  fps2flush drugs.fps -o drugs.flush

"""

p = parser = argparse.ArgumentParser(
    description = "Convert a chemfp fingerprint file into a fingerprint file in flush format.",
    epilog = epilog,
    formatter_class = argparse.RawDescriptionHelpFormatter,
    )

p.add_argument("--in", metavar="FORMAT", dest="in_format",
               choices=("fps", "fps.gz", "fpb"), default=None,
               help="Input fingerprint file format (default: guess based on the extension and default to 'fps')")

p.add_argument("--output", "-o", metavar="FLUSH_FILENAME",
               help="save the fingerprints to FLUSH_FILENAME")

cmdsupport.add_version(p)
p.add_argument("filename", metavar="FINGERPRINT_FILENAME", nargs="?",
               help="input fingerprint filename (default: use stdin)")

def run():
    cmdsupport.run(main)

def main(argv=None):
    args = parser.parse_args(argv)

    try:
        reader = chemfp.open(args.filename, args.in_format)
    except IOError as err:
        die("Cannot open fingerprint file: " + str(err))
    except chemfp.ParseError as err:
        die("Cannot parse fingerprint file: " + str(err))
    
    with reader:
        try:
            writer = flush.open_fingerprint_writer(args.output, reader.metadata)
        except IOError as err:
            die("Cannot open output file: " + str(err))
        
        with writer:
            writer.write_fingerprints(reader)


if __name__ == "__main__":
    main()
    
