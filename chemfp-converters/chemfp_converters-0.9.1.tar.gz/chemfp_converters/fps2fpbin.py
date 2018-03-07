import argparse

import os
import sys

import chemfp
from . import fpbin
from . import cmdsupport
die = cmdsupport.die

epilog = """\
THIS INTERFACE IS EXPERIMENTAL! IT USES AN UNDOCUMENTED FILE FORMAT.

The OpenEye OEFastFPDatabase stores fingerprints in a file with the
extension ".fpbin". The file only contains the fingerprint and an
integer index into a "moldb" ("molecule database"). It does not store
the fingerprint identifiers. See
https://docs.eyesopen.com/toolkits/cpp/graphsimtk/OEGraphSimClasses/OEFastFPDatabase.html
for information about the OEGraphSim API.

There is currently no way to use the API to create an fpbin file with
pre-computed fingerprints. Instead, this converter writes the file
format directly. The format is not documented, I may have messed up,
and OpenEye makes no promises that the format will not change.

The input FPS/FPB fingerprint type must an OEChem fingerprint type,
either as an chemfp type string (starting "OpenEye-Path",
"OpenEye-Tree", "OpenEye-Circular", or "OpenEye-MACCS166") or as an
OEGraphSim type string (starting "Path", "Tree", "Circular", or
"MACCS166"). For examples:

  OpenEye-Path/2 numbits=4096 minbonds=0 maxbonds=5 atype=Arom|AtmNum|Chiral|EqHalo|FCharge|HvyDeg|Hyb btype=Order|Chiral
  Path,ver=2.0.0,size=4096,bonds=0-5,atype=AtmNum|Arom|Chiral|FCharge|HvyDeg|Hyb|EqHalo,btype=Order|Chiral
  MACCS,ver=2.0.0
  OpenEye-MACCS166/3

The fpbin format requires a moldb filename, which is why the '--moldb'
parameter is required. By default the filename is simply included in
the header.

Be default the fingerprints are written to the file in the same order
as they appeared in the input FPS/FPB file. If you use the
'--match-moldb' flag then the fingerprints will be written in the same
order as they appear in the moldb file.

More specifically, it will read all of the fingerprints into memory,
then use OEMolDatabase to iterate through the titles/identifiers in
the molecule file, look up the corresponding fingerprint, and save it
to the fpbin file. If the identifier does not exist then the empty
fingerprint will be written.

If the --output is not specified then the output filename will be the
same as the input FPS/FPB file, but with the extension replaced with
".fpbin". If the input is from stdin then the --output filename must
be specified.

Example #1: Convert the fingerprints from 'drugs.fps' into
'drugs.fpbin', using the same order as the FPS file. The fingerprint
order must match the --moldb is required but the file is not used.

  fps2fpbin drugs.fpbin --moldb drugs.sdf

Example #2: Reorder tbe fingerprint so they match the --moldb record
order. This uses OEChem to read the OEMolDatabase.

  fps2fpbin drugs.fpbin --moldb drugs.sdf --match-moldb

"""

p = parser = argparse.ArgumentParser(
    description = "Convert a chemfp fingerprint file into an OEChem FastFPDatabase (.fpbin) file.",
    epilog = epilog,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    )

p.add_argument("--in", metavar="FORMAT", dest="in_format",
               choices=("fps", "fps.gz", "fpb"), default=None,
               help="Input fingerprint file format (default: guess based on the extension and default to 'fps')")
p.add_argument("--moldb", metavar="FILENAME", required=True,
               help="location of the molecule database file")
p.add_argument("--match-moldb", action="store_true",
               help="(possibly) reorder the fingerprints so they match the molecules in --moldb")
p.add_argument("--output", "-o", metavar="FILENAME",
                help="output .fpbin filename")

p.add_argument("-q", "--quiet", action="store_true",
               help="do not show warnings")
cmdsupport.add_version(parser)
p.add_argument("filename", metavar="FINGERPRINT_FILENAME", nargs="?",
               help="input fingerprint filename (default: use stdin)")

def make_match_reader(moldb_filename, arena, verbose=True):
    from openeye.oechem import OEMolDatabase
    moldb = OEMolDatabase()
    if not moldb.Open(moldb_filename):
        open(moldb_filename).close()
        raise AssertionError("XXX need an IOError here")
    
    return MatchReader(moldb, arena, verbose)
    
class MatchReader(object):
    def __init__(self, moldb, arena, verbose):
        self.moldb = moldb
        self.arena = arena
        self.num_found = self.num_missing = 0
        self._verbose = verbose

    @property
    def num_processed(self):
        return self.num_found + self.num_missing
        
    def __iter__(self):
        empty = b"\0" * self.arena.metadata.num_bytes
        
        for index, title in enumerate(self.moldb.GetTitles()):
            fp = self.arena.get_fingerprint_by_id(title)
            if fp is None:
                if self._verbose:
                    sys.stderr.write("No fingerprint found for %r (#%d).\n" % (title, index))
                self.num_missing += 1
                yield title, empty
            else:
                self.num_found += 1
                yield title, fp
    

def run():
    cmdsupport.run(main)

def main(argv=None):
    args = parser.parse_args(args=argv)
    
    verbose = not args.quiet
    destination = args.output
    
    if not args.filename:
        # Read from stdin
        input_filename = None
        if not destination:
            parser.error("Must specify --output if the input is from stdin")
    else:
        # Read from a file.
        input_filename = args.filename
        if not destination:
            destination = os.path.splitext(input_filename)[0] + ".fpbin"
            if verbose:
                sys.stderr.write("WARNING: No --output filename given, using %s.\n"
                                     % (cmdsupport.my_repr(destination),))

    match_moldb = args.match_moldb
    moldb_filename = args.moldb

    # Open the fingerprint file to see if it's possible
    try:
        if match_moldb:
            reader = chemfp.load_fingerprints(input_filename, format=args.in_format)
        else:
            reader = chemfp.open(input_filename, format=args.in_format)
    except IOError as err:
        die("Cannot open fingerprint file: " + str(err))
    except chemfp.ParseError as err:
        die("Cannot parse fingerprint file: " + str(err))

    with reader:
        num_bytes = reader.metadata.num_bytes
        if not num_bytes:
            die("Unable to determine the number of bytes in the input fingerprints")
        if num_bytes % 8:
            if reader.metadata.type is None:
                die("The fpbin format requires fingerprint sizes which are a multiple of 8 bytes long.\n"
                        "Input has %d bytes per fingerprint." % (num_bytes,))
            else:
                die("The fpbin format requires fingerprint sizes which are a multiple of 8 bytes long.\n"
                        "Input type %s has %d bytes per fingerprint."
                        % (cmdsupport.my_repr(reader.metadata.type), num_bytes))

        # See if it's an OEGraphSim fingerprint type already
        fptype = reader.metadata.type
        if not type:
            die("Fingerprint file must have a fingerprint type string")

        try:
            fptype_obj = fpbin.parse_oetype_string(fptype)
        except ValueError as err1:
            try:
                fptype_obj = fpbin.parse_chemfp_type_string(fptype)
            except ValueError as err2:
                die("Fingerprint type must a OEGraphSim fingerprint type (in OEGraphSim or chemfp format): %r" % (fptype,))

        oetype_str = fptype_obj.to_oetype()

        ## Will I be matching the moldb order?
        if args.match_moldb:
            try:
                reader = make_match_reader(moldb_filename, reader, verbose)
            except IOError as err:
                die("Unable to open --moldb file: %s" % (err,))
            
        
        try:
            writer = fpbin.open_fpbin_writer(
                destination,
                moldb_filename,
                oetype_str,
                num_bytes,
                )
        except IOError as err:
            die("Unable to open --output file: %s" % (err,))

        with writer:
            writer.write_fingerprints(reader)
            
        if args.match_moldb:
            num_missing = reader.num_missing
            if num_missing and verbose:
                sys.stderr.write("Missing identifiers for %d of %d records.\n"
                                     % (num_missing, reader.num_processed))
                

if __name__ == "__main__":
    main()
    
