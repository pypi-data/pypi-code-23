from __future__ import print_function, absolute_import
import sys
import datetime

from . import fastsearch

import argparse
import chemfp  # requires at least chemfp 1.3
from chemfp.bitops import hex_encode

from . import __version__ as _version

from . import fastsearch
from . import cmdsupport
die = cmdsupport.die
my_repr = cmdsupport.my_repr

epilog = """\

The Open Babel FastSearch stores fingerprints in a file with the
extension ".fs". Each record contains only the fingerprint and a byte
offset into a "datafile", which is the structure file containing the
original records. In Open Babel, the datafile may be in any format
that Open Babel supports. This converter uses its own I/O routines to
access the datafile, and only supports SMILES and SDF files. Unlike
Open Babel, gzip'ed data files are supported.

The .fs file contains the datafile filename used to generate the
fingerprints. By default this filename will be used to find the
datafile. Use --datafile to specify an alternate filename.

To get the identifier, which is required for the FPS format, the
converter will open the datafile, seek to the correct byte offset, and
read that line, excluding the newline. If the record is in SDF format,
the text will be used as the identifier.

As an alternative, the --use-index-as-id option uses the sequence 0,
1, 2, .. as the identifier, and --use-offset-as-id uses the record
offset from the .fs file. The datafile will not be opened.

If the datafile record is in SMILES format then the text will be
parsed according to the --delimiter option. The default option,
'to-eol', interprets the first term (up to the first whitespace) as
the SMILES and the rest of the text as the identifier. The 'space' and
'tab' delimiter styles interpret the text as space-delimited or
tab-delimited fields, where the second field is the identifier. The
'whitespace' delimiter style uses any sequence of one or more space or
tab characters as the delimiter.

The .fs file records the Open Babel fingerprint type. The converter
will translate that into a chemfp fingerprint type string for the
'type' line of the output header. Use --type to specify an alternative
type, or --no-type to exclude type information from the output header.

By default the datafile filename (from the --datafile option if given,
otherwise from the filename in the header) will be saved as a 'source'
field in the output header. Use --source to specify one or more
alternate different source fields, or use --no-source to exclude
source information.

By default the output will include the creation date of the fs file as
the 'date' field in the output header. Use --date to specify an
alterate date, or --no-date to exclude the date.

Use --software to specify the 'software' line in the output header.

Use --output to specify an output filename instead of writing to
stdout. The default output format is based on the filename
extension. Use --out to specify a different output format.

The --dump option writes the header and fingerprint records (structure
record byte offset and hex-encoded fingerprint) to stdout. It does not
use the --datafile.

Example #1: Show the fingerprints from 'drugs.fs' using the internal
filename to get the structure data file to use for identifier lookup:

  fs2fps drugs.fs

Example #2: Specify the structure data file and output file:

  fs2fps drugs.fs -d drugs.sdf -o drugs.fps.gz

"""

p = parser = argparse.ArgumentParser(
    description = "Convert an Open Babel FastSearch index into chemfp's FPS format.",
    epilog = epilog,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    )

p.add_argument("-d", "--datafile", metavar="FILENAME",
               help="Location of structure data file. Used to extract record identifiers. "
               "Only SD and SMILES files are supported.")

p.add_argument("--in", metavar="FORMAT", dest="in_format",
               choices=("smi", "smi.gz", "sdf","sdf.gz"), default=None,
               help="Structure data file format (default: guess based on the extension and default to 'smi')")
p.add_argument("--delimiter", choices=("to-eol", "tab", "whitespace", "space"),
               default="to-eol",
               help="delimiter style a SMILES file (default: 'to-eol')")

g = p.add_mutually_exclusive_group()
g.add_argument("--use-index-as-id", action="store_true",
               help="use the index as the identifier; do not get the identifiers from --datafile")
g.add_argument("--use-offset-as-id", action="store_true",
               help="use the offset as the identifier; do not get the identifiers from --datafile")


g = p.add_mutually_exclusive_group()
g.add_argument("--type",
               help="specify the 'type' metadata value (default: use the type from the index file)")
g.add_argument("--no-type", action="store_true",
               help="do not include the type in the metadata")

g = p.add_mutually_exclusive_group()
g.add_argument("--source",
               help="specify the 'source' metadata value (default: use the --datafile or the data filename in the index)")
g.add_argument("--no-source", action="store_true",
               help="do not include the source in the metadata")

cmdsupport.add_software_flag(parser)

cmdsupport.add_both_date_flags(parser)

cmdsupport.add_output(parser)

p.add_argument("--dump", action="store_true",
               help="show the raw content of the .fs file instead of converting to FPS/FPB format")

cmdsupport.add_version(p)

p.add_argument("fsindex", metavar="INDEX_FILENAME",
                help = "fastsearch index filename (usually ends with '.fs')")

def dump(args, fsindex):
    header = fsindex.header
    print("** Header from %r." % (args.fsindex,))
    print("Header length:", header.header_length)
    print("#entries:", header.num_entries)
    print("#words/fp: %d (#bits/fp: %d)" % (header.num_words, header.num_bits))
    print("Open Babel fingerprint type:", my_repr(header.fpid))
    print("chemfp fingerprint type:", my_repr(header.chemfp_type))
    print("datafile filename:", my_repr(header.data_filename))
    print("** End of header. Start of fingerprint records.")
    print("index\toffset\tfingerprint")
    for index, (offset, fp) in enumerate(fsindex):
        print("%d\t%s\t%s" % (index, offset, hex_encode(fp)))


def run():
    cmdsupport.run(main)

def main(argv=None):
    args = parser.parse_args(args=argv)

    index_filename = args.fsindex

    if args.dump:
        id_type = "offset"
    else:
        id_type = "id"
        if args.use_index_as_id:
            id_type = "index"
        elif args.use_offset_as_id:
            id_type = "offset"

    try:
        fsindex = fastsearch.open_index(args.fsindex, args.datafile, args.in_format,
                                        args.delimiter, id_type)
    except IOError as err:
        die(str(err))
    except chemfp.ParseError as err:
        die("Cannot process index file %s: %s" % (my_repr(args.fsindex), err))
    ## except Exception as err:
    ##     die("Unexpected error: %s" % (err,))

    if args.dump:
        with fsindex:
            dump(args, fsindex)
        return
        
    with fsindex:
        metadata = fsindex.metadata.copy()

        if args.no_type:
           metadata.type = None 
        elif args.type:
            metadata.type = args.type
        
        if args.no_source:
            metadata.sources = []
        elif args.source:
            metadata.sources = [args.source]

        if args.software:
            metadata.software = args.software
            
        if args.no_date:
            metadata.date = None
        elif args.date:
            # chemfp 1.3 requires a string. chemfp 3.1 accepts a datetime
            metadata.date = args.date.isoformat().split(".", 1)[0]

        try:
            writer = chemfp.open_fingerprint_writer(
                args.output,
                metadata = metadata,
                format = args.output_format)
        except IOError as err:
            die(str(err))
        ## except Exception as err:
        ##     if args.output is None:
        ##         msg = "Unexpected error opening fingerprint writer to stdout: "
        ##     else:
        ##         msg = "Unexpected error opening fingerprint writer to %r: "
        ##     die(msg + str(err))
        
        with writer:
            try:
                writer.write_fingerprints(fsindex)
            except chemfp.ParseError as err:
                die(str(err))
            
if __name__ == "__main__":
    main()
    
