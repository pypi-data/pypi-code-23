from __future__ import print_function, absolute_import

import sys
import argparse

import chemfp
from chemfp.bitops import hex_encode

from . import fpbin
from . import cmdsupport
from .cmdsupport import die

epilog = """\
THIS INTERFACE IS EXPERIMENTAL! IT USES AN UNDOCUMENTED FILE FORMAT.

The OpenEye OEFastFPDatabase stores fingerprints in a file with the
extension ".fpbin". Each record contains only the fingerprint and an
integer index into a "moldb" ("molecule database"). It does not store
the fingerprint identifiers. See
https://docs.eyesopen.com/toolkits/cpp/graphsimtk/OEGraphSimClasses/OEFastFPDatabase.html
for information about the OEGraphSim API.

There is currently no way to use the API to read the fingerprints from
an fpbin file. Instead, this converter reades the file format
directly. The format is not documented, I may have messed up, and
OpenEye makes no promises that the format will not change.

Each fingerprint record in an fpbin file contains a fingerprint and a
molecule index. To get the identifier, which is required for the FPS
format, the converter will use OEMolDatabase() to open the 'moldb'
molecule database file (which can be a .smi, .sdf, .oeb or other
OEChem-supported molecule file format) and get the title corresponding
to each index.

By default the converter will use the moldb filename stored in the
header of the fpbin file. Use --moldb to specify an alternate
location.

Use the --use-index-as-id option to skip the identifier lookup and
simply use the index (which starts with 0) as the identifier.

Use the --dump option to display the fpbin header and records to
stdout instead of converting them to 

By default the OEGraphSim fingerprint type string will be converted to
a chemfp fingerprint type string. Use --keep-type to keep the original
OEGraphSim type. Use --type to specify an alternative type, or
--no-type to exclude type information from the output header.

By default the moldb filename (from the --moldb option if given,
otherwise from the filename in the header) will be saved as a 'source'
field in the output header. Use --source to specify one or more
alternate different source fields, or use --no-source to exclude
source information.

By default the output will include the creation date of the fpbin file
as the 'date' field in the output header. Use --date to specify an
alterate date, or --no-date to exclude the date.

Use --software to specify the 'software' line in the output header.

Use --output to specify an output filename instead of writing to
stdout. The default output format is based on the filename
extension. Use --out to specify a different output format.

The --dump option writes the header and fingerprint records (index and
hex-encoded fingerprint) to stdout. It does not use the --datafile.

Example #1: Show the fingerprints from 'drugs.fpbin' using the
internal filename to get the structure data file to use for identifier
lookup:

  fpbin2fps drugs.fpbin

Example #2: Specify the molecule database (structure) and output files:

  fpbin2fps drugs.fpbin --moldb drugs.sdf -o drugs.fps.gz
"""

p = parser = argparse.ArgumentParser(
    description = "Convert an OEChem FastFPDatabase (.fpbin) file into a chemfp fingerprint file.",
    epilog = epilog,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    )


p.add_argument("--moldb", metavar="FILENAME",
               help="location of the molecule file containing identifiers "
                    "(default: use the filename in the .fpbin file)")
p.add_argument("--use-index-as-id", action="store_true",
               help="use the index as the identifier; do not get the identifiers from --moldb")

g = parser.add_mutually_exclusive_group()
g.add_argument("--keep-type", action="store_true",
                help="keep the OEGraphSim type string instead of converting to a chemfp type string")
cmdsupport.add_type_flag(g)
cmdsupport.add_no_type_flag(g)

cmdsupport.add_software_flag(parser)

g = p.add_mutually_exclusive_group()
g.add_argument("--source",
               help="specify the 'source' metadata value (default: use moldb filename from the .fpbin file)")
g.add_argument("--no-source", action="store_true",
               help="do not include the source in the metadata")

cmdsupport.add_both_date_flags(parser)

cmdsupport.add_output(parser)
p.add_argument("--dump", action="store_true",
               help="show the raw content of the .fpbin file instead of converting to FPS/FPB format")
cmdsupport.add_version(p)
p.add_argument("fpbin_filename", metavar="FILENAME",
               help="the .fpbin fingerprint database filename")

def check_oechem():
    try:
        from openeye.oechem import OEChemIsLicensed
    except ImportError as err:
        die("OEChem Python toolkit not found: %s" % (err,))
    if not OEChemIsLicensed():
        import subprocess
        p = subprocess.Popen([sys.executable, "-c", "from openeye.oechem import OEMol; OEMol()"],
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        msg = p.stdout.read()
        p.wait()
        if not isinstance(msg, str):
            msg = msg.decode("utf8")
        sys.stderr.write(msg)
        die("Your OEChem license is not valid.")
        
    return

def dump(args):
    try:
        reader = fpbin.read_fpbin_records(args.fpbin_filename)
    except (ValueError, IOError) as err:
        die("Cannot open .fpbin file: %s" % (err,))
    with reader:
        header = reader.fpbin_header
        print("** Header from %r." % (args.fpbin_filename,))
        print("line 1:", repr(header.signature))
        print("moldb filename:", repr(header.moldb_filename))
        print("oegraphsim type:", repr(header.oetype_str))
        print("parsed type:", repr(header.oetype))
        print("count:", header.num_fingerprints)
        print("#words/fp: %d (#bits/fp: %d)" % (header.num_words, 64*header.num_words))
        print("** End of header. Start of fingerprint records.")
        print("index\tpopcount\tfingerprint")
        for index, popcount, fp in reader:
            print("%d\t%d\t%s" % (index, popcount, hex_encode(fp)))

def convert(args):
    try:
        reader = fpbin.read_fpbin_fingerprints(
            fpbin_filename = args.fpbin_filename,
            moldb_filename = args.moldb,
            use_index_as_id = args.use_index_as_id,
            )
    except fpbin.FPBinIOError as err:
        die("Cannot open .fpbin file: %s" % (err,))
    except chemfp.ParseError as err:
        die("Cannot parse .fpbin file: %s" % (err,))
    except fpbin.MolDBIOError as err:
        die("Cannot open --moldb file: %s" % (err,))
    except fpbin.MismatchError as err:
        die("Size mismatch: %s" % (err,))
    except ValueError as err:
        die("Cannot open .fpbin file: %s" % (err,))

    if args.source is None and reader.fpbin_header.moldb_filename:
        args.source = [reader.fpbin_header.moldb_filename]

    metadata = reader.metadata
    if args.keep_type:
        metadata = metadata.copy(type=reader.fpbin_header.oetype_str)
    metadata = cmdsupport.get_output_metadata(metadata, args)
    
    with reader:
        try:
            writer = chemfp.open_fingerprint_writer(
                args.output, metadata = metadata, format=args.output_format)
                
        except (ValueError, IOError) as err:
            die("Cannot open output file: %s" % (err,))
        
        with writer:
            writer.write_fingerprints(reader)



def run():
    cmdsupport.run(main)

def main(argv=None):
    args = parser.parse_args(args=argv)

    if args.dump:
        dump(args)
        return
    else:
        if not args.use_index_as_id:
            check_oechem()
        convert(args)
        

if __name__ == "__main__":
    main()
    
