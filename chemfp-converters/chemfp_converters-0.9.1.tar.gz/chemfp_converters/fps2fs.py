from __future__ import print_function, absolute_import

import sys
import os
import argparse

import chemfp

try:
    # Using chemfp 1.3
    from chemfp import sdf_reader
    has_text_toolkit = False
except ImportError:
    # Introduced in chemfp 2.0
    from chemfp import text_toolkit
    has_text_toolkit = True
    

from . import fastsearch
from . import cmdsupport
from .cmdsupport import die

epilog = """\

The Open Babel FastSearch stores fingerprints in a file with the
extension ".fs". A .fs file is created from a "datafile", which is a
structure file. In Open Babel, the datafile may be in any format that
Open Babel supports. This converter uses its own I/O routines to
access the datafile, and only supports SMILES and SDF files. Unlike
Open Babel, gzip'ed data files are supported.

The .fs file contains a header followed by fingerprint records. The
header stores the Open Babel fingerprint type string, the datafile
filename, and a few other fields. Each fingerprint record contains the
offset to the first byte of the record in the (uncompressed) datafile,
and the fingerprint. The fingerprint identifier is not stored.

By default the converter reads fingerprints in FPS format from
stdin. Use FINGERPRINT_FILENAME to specify a file. The converter will
use the filename extension to determine the file format, or you can
specify the --in to specify the format.

Use --datafile to specify the datafile. This is required because the
.fs file needs the record offsets, which is not available from an
FPS/FPB file. Instead, the converter will parse the file and for each
record determine the offset to the first byte and the record
identifier. If the datafile filename (in lowercase) ends with ".sdf",
".sd", or ".mdl", or with the additional ".gz" extension for gzip
compression, then it will be parsed as an SD file. Otherwise it will
be parsed as a SMILES file.

If the datafile record is in SMILES format then the text will be
parsed according to the --delimiter option. The default option,
'to-eol', interprets the first term (up to the first whitespace) as
the SMILES and the rest of the text as the identifier. The 'space' and
'tab' delimiter styles interpret the text as space-delimited or
tab-delimited fields, where the second field is the identifier. The
'whitespace' delimiter style uses any sequence of one or more space or
tab characters as the delimiter.

Use --has-header to ignore the first line of the SMILES file; likely
because it contains column headers.

Use --output to specify the filename for the .fs file. If it is not
given then the name will be the datafile filename, with the last
extension (or last extensions, if the last extension is ".gz")
replaced with ".fs".

Example: Combine fingerprints from "drugs.fps" (containing FP2
fingerprints) and identifiers from "drugs.sdf" to make "drugs.fpbin":

    fps2fs --datafile drugs.sdf drugs.fps -o drugs.fpbin
"""

p = parser = argparse.ArgumentParser(
    description = "Convert a chemfp fingerprint file into Open Babel's FastSearch format",
    epilog = epilog,
    formatter_class = argparse.RawDescriptionHelpFormatter,
    )

p.add_argument("--in", metavar="FORMAT", dest="in_format",
               choices=("fps", "fps.gz", "fpb"), default=None,
               help="Input fingerprint file format (default: guess based on the extension and default to 'fps')")

p.add_argument("-d", "--datafile", required=1, metavar="STRUCTURE_FILENAME",
               help="Location of the structure data file. Used to get record locations. "
               "Only SD and SMILES files are supported.")

p.add_argument("--delimiter", choices=("to-eol", "tab", "whitespace", "space"),
               default="to-eol",
               help="delimiter style a SMILES file (default: 'to-eol')")
p.add_argument("--has-header", action="store_true",
               help="Skip the first line of the SMILES file")
p.add_argument("--output", "-o", metavar="FS_FILENAME",
               help="save the fingerprints to FS_FILENAME")
p.add_argument("-q", "--quiet", action="store_true",
               help="do not show progress or warnings")

cmdsupport.add_version(p)
p.add_argument("filename", metavar="FINGERPRINT_FILENAME", nargs="?",
               help="input fingerprint filename (default: use stdin)")

## Adapters to work with chemfp 1.3

def read_smiles(infile, delimiter, has_header, location):
    reader = _read_smiles(infile, delimiter, has_header, location)
    next(reader)
    return reader

def _read_smiles(infile, delimiter, has_header, location):
    lineno = 0
    offset_start = offset_end = 0
    _use_unicode = cmdsupport.chemfp_supports_unicode

    def get_lineno():
        return lineno
    
    def get_offsets():
        return (offset_start, offset_end)

    location.save(record_format="smi")
    location.register(get_lineno=get_lineno,
                      get_offsets=get_offsets)
    try:
        yield "ready!"
        if has_header:
            header = infile.readline()
            if header:
                lineno += 1
                offset_start = offset_end = offset_end + len(header)


        if delimiter == "whitespace":
            for lineno, line in enumerate(infile, lineno+1):
                offset_end = offset_start + len(line)
                terms = line.split()
                try:
                    id = terms[1]
                except IndexError:
                    raise chemfp.ParseError("Missing SMILES identifier", location)
                if _use_unicode:
                    yield (id.decode("utf8"), None)
                else:
                    yield (id, None)
                offset_start = offset_end
                
        elif delimiter == "tab":
            for lineno, line in enumerate(infile, lineno+1):
                offset_end = offset_start + len(line)
                terms = line.split(b"\t")
                try:
                    id = terms[1]
                except IndexError:
                    raise chemfp.ParseError("Missing SMILES identifier", location)
                if id[-1:] == b"\n":
                    id = id[:-1]
                if not id:
                    raise chemfp.ParseError("Empty SMILES identifier", location)
                if _use_unicode:
                    yield (id.decode("utf8"), None)
                else:
                    yield (id, None)
                offset_start = offset_end
                
        elif delimiter == "space":
            for lineno, line in enumerate(infile, lineno+1):
                offset_end = offset_start + len(line)
                terms = line.split(b" ")
                try:
                    id = terms[1]
                except IndexError:
                    raise chemfp.ParseError("Missing SMILES identifier", location)
                if id[-1:] == b"\n":
                    id = id[:-1]
                if not id:
                    raise chemfp.ParseError("Empty SMILES identifier", location)
                if _use_unicode:
                    yield (id.decode("utf8"), None)
                else:
                    yield (id, None)
                offset_start = offset_end
                
        elif delimiter == "to-eol":
            for lineno, line in enumerate(infile, lineno+1):
                offset_end = offset_start + len(line)
                terms = line.split(None, 1)
                try:
                    id = terms[1]
                except IndexError:
                    raise chemfp.ParseError("Missing SMILES identifier", location)
                if id[-1:] == b"\n":
                    id = id[:-1]
                if not id:
                    raise chemfp.ParseError("Empty SMILES identifier", location)
                if _use_unicode:
                    yield (id.decode("utf8"), None)
                else:
                    yield (id, None)
                offset_start = offset_end

        else:
            raise AssertionError(delimiter)

    finally:
        location.save(lineno=get_lineno(),
                      offsets=get_offsets())
                              
def track_sdf_offsets(reader, location):
    reader = _track_sdf_offsets(reader, location)
    next(reader)
    return reader
    
def _track_sdf_offsets(reader, location):
    start_offset = end_offset = 0
    def get_offsets():
        return (start_offset, end_offset)
    location.register(get_offsets=get_offsets)
    try:
        yield "Ready!"
        
        for record in reader:
            start_offset = end_offset
            end_offset += len(record)
            title, _, _ = record.partition("\n")
            if title[-1:] == "\r":  # In case the newline convention is "\r\n"
                title = title[:-1]
            yield title, record
    finally:
        location.save(offsets=get_offsets())

def _open_without_text_toolkit(filename, delimiter, has_header):
    location = chemfp.io.Location.from_source(filename)

    format, compression = fastsearch.guess_format(filename, None)

    f = fastsearch.open_binary(filename, compression)

    if format == "sdf":
        reader = sdf_reader.open_sdf(f)
        # The SDF reader in 1.3 didn't handle offset tracking so do it myself
        reader = track_sdf_offsets(reader, location)

    else:
        reader = read_smiles(f, delimiter, has_header, location)
    
    return reader, location

###

def _open_with_text_toolkit(filename, delimiter, has_header):
    # There is a bug in the chemfp 3.1 SMILES file parser. The size of the
    # header was not included in the offset calculations.
    fmt = text_toolkit.get_output_format_from_destination(filename)
    if has_header and fmt.name in ("smi", "can", "ism"):
        return _open_without_text_toolkit(filename, delimiter, has_header)
    
    reader = text_toolkit.read_ids_and_molecules(
        filename, reader_args={"delimiter": delimiter, "has_header": has_header})
    return reader, reader.location

def find_datafile_record_offsets(
        parser, datafilename, delimiter, has_header, verbose):
    table = {}
    
    try:
        if has_text_toolkit:
            reader, loc = _open_with_text_toolkit(
                datafilename, delimiter, has_header)
        else:
            reader, loc = _open_without_text_toolkit(
                datafilename, delimiter, has_header)

    except (IOError, ValueError) as err:
        die("Cannot open --datafile: " + str(err))

    erase_msg = ""
    
    try:
        try:
            recno = 0
            for recno, (id, record) in enumerate(reader, 1):
                if verbose and (recno == 1 or recno % 10000 == 0):
                    msg = ("Indexing %s datafile record #%d (id=%r, start=%d)"
                            % (loc.record_format, recno, id, loc.offsets[0]))
                    sys.stderr.write(erase_msg)
                    sys.stderr.write(msg)
                    sys.stderr.flush()
                    erase_msg = "\r" + " "*len(msg) + "\r"

                table[id] = loc.offsets[0]
        except chemfp.ParseError as err:
            if erase_msg:
                sys.stderr.write("\n")
            die("Cannot parse --datafile: " + str(err))
    finally:
        reader.close()

    if verbose:
        sys.stderr.write(erase_msg)
        sys.stderr.write("Indexed %d datafile records.\n" % (len(table),))
    return table
    

def run():
    cmdsupport.run(main)

def main(argv=None):
    args = parser.parse_args(argv)

    verbose = not args.quiet

    if not args.filename:
        # Read from stdin
        input_filename = None
    else:
        # Read from a file.
        input_filename = args.filename

    
    if args.output is not None:
        fs_filename = args.output
    else:
        if input_filename is None:
            parser.error("Must specify --output when reading fingerprints from stdin.")
            
        # No output filename given. Use the fingerprint filename as the base.
        basename, _ = os.path.splitext(input_filename)

        fs_filename = basename + ".fs"
        if verbose:
            sys.stderr.write("WARNING: No --output filename given, using %r.\n" % (fs_filename,))

    # Open the fingerprint file to see if it's possible
    try:
        reader = chemfp.open(input_filename)
    except IOError as err:
        die("Cannot open fingerprint file: " + str(err))
    except chemfp.ParseError as err:
        die("Cannot parse fingerprint file: " + str(err))
        
    with reader:
        try:
            openbabel_typeinfo = fastsearch.get_openbabel_typeinfo(reader.metadata)
        except ValueError as err:
            die("Unable to use the input fingerprint type: %s" % (err,))
        
        # Parse the structure  id -> record start byte
        data_filename = args.datafile
        record_offsets = find_datafile_record_offsets(
            parser, data_filename, args.delimiter, args.has_header, verbose)

        if verbose and not record_offsets:
            sys.stderr.write("WARNING: no records found in the datafile\n")

        try:
            outfile = open(fs_filename, "wb")
        except IOError as err:
            die("Cannot open output file: " + str(err))
            
        with outfile:
            status = fastsearch.write_index(
                outfile, openbabel_typeinfo, data_filename,
                reader, record_offsets, verbose)

        if verbose and status.num_failed != 0:
            sys.stderr.write("WARNING: Unable to index %d of %d fingerprint records.\n"
                             % (status.num_failed, status.num_fingerprints))
                

if __name__ == "__main__":
    main(sys.argv[1:])
    
