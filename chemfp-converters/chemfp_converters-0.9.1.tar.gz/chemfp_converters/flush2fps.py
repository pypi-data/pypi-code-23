from __future__ import print_function, absolute_import

import argparse
import datetime
import sys

import chemfp

from . import flush
from . import cmdsupport

epilog = """\

A Flush file stores identifiers and fingerprints in a file with the
extension ".flush". The Flush format is used by Dave Cosgrove's
fingerprint tools at https://github.com/OpenEye-Contrib/Flush .

A Flush file does not contain fingerprint type information. Use --type
to specify a type line in the output header.

Use --software to specify the 'software' line in the output
header. Use --source to specify a 'source' line in the output
header. Multiple sources may be specified by specifying --source
multiple times.

By default the output will include the creation date of the flush file
as the 'date' field in the output header. Use --date to specify an
alterate date, or --no-date to exclude the date.

Use --output to specify an output filename instead of writing to
stdout. The default output format is based on the filename
extension. Use --out to specify a different output format.

Example:

  flush2fps drugs.flush

"""

p = parser = argparse.ArgumentParser(
    description = "Convert a Flush fingerprint file into chemfp's FPS format.",
    epilog = epilog,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    )

cmdsupport.add_type_flag(parser)
cmdsupport.add_software_flag(parser)
cmdsupport.add_source_flag(parser)
cmdsupport.add_both_date_flags(parser, "(default: use the creation date of the flush file)")

cmdsupport.add_output(parser)
cmdsupport.add_version(parser)
p.add_argument("flush", metavar="FLUSH_FILENAME",
                help = "Flush filename to process (usually ends with '.flush')")


def run():
    cmdsupport.run(main)

def main(argv=None):
    args = parser.parse_args(argv)

    try:
        reader = flush.open_flush(args.flush)
    except IOError as err:
        cmdsupport.die("Cannot open flush file: %s" % (err,))
    except chemfp.ParseError as err:
        cmdsupport.die("Problem parsing flush file: %s" % (err,))

    with reader:
        metadata = cmdsupport.get_output_metadata(reader.metadata, args)

        try:
            writer = chemfp.open_fingerprint_writer(args.output, format=args.output_format, metadata=metadata)
        except IOError as err:
            cmdsupport.die("Cannot open output file: %s" % (err,))
        
        with writer:
            try:
                writer.write_fingerprints(reader)
            except chemfp.ParseError as err:
                cmdsupport.die("Problem parsing flush file: %s" % (err,))


if __name__ == "__main__":
    main()
    
