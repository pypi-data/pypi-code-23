from __future__ import print_function

# Convert to/from the Open Babel "FastSearch" format
#   http://openbabel.org/wiki/FastSearch

# FastSearch uses an index file with the extension ".fs".
# The index file contains:
#  1) a header of length 284 bytes
#    -   4 bytes for the header length (always 284?)
#    -   4 bytes for the number of record entries ('num_entries')
#    -   4 bytes for the number of integer words in a fingerprint ('num_words')
#    -  15 bytes for a fingerprint type string (eg, "FP2", or "MACCS")
#           and right-padded with NUL bytes
#    -   1 byte to specify if the file uses 32-bit or 64-bit offsets ('seek64')
#    - 256 bytes for the structure data filename, right-padded with
#            NUL bytes ("data filename")
# 
#  2) The fingerprints, stored as 'num_entries' contiguous fingerprint
#   records. Each fingerprint contains 'num_words' 32-bit integers.

#  3) Byte offsets for the original record in the structure data file,
#  stored as 'num_entries' integers, which may be 32- or 64-bit
#  integers, depending on the value of 'seek64'.
#
#  Identifiers are not stored in the index file but are kept in the
#  original structure file. An Open Babel similarity search records
#  the index positions of the fingerprints, looks up the corresponding
#  offsets, and reads the records from the structure 'data filename'.

import sys
import struct
import datetime
import os

import chemfp
import chemfp.io

from . import cmdsupport

#### Work with an index file

# Store the index header information
class FastSearchIndexHeader(object):
    def __init__(self, header_length, num_entries, num_words,
                 fpid, seek64, data_filename,
                 num_bits, chemfp_type):
        self.header_length = header_length
        self.num_entries = num_entries
        self.num_words = num_words
        self.fpid = fpid
        self.seek64 = seek64
        assert isinstance(data_filename, type(u""))
        self.data_filename = data_filename

        self.num_bits = num_bits
        self.num_bytes = (num_bits+7)//8
        self.chemfp_type = chemfp_type

    def __repr__(self):
        return (
            "FastSearchIndexHeader(header_length=%d, num_entries=%d, num_words=%d, "
            "fpid=%r, seek64=%d, data_filename=%r, num_bits=%d, chemfp_type=%r)"
            % (self.header_length, self.num_entries, self.num_words, self.fpid,
               self.seek64, self.data_filename, self.num_bits, self.chemfp_type))

# Open Babel doesn't store the details that chemfp wants, so
# use a lookup system 
class ChemFPInfo(object):
    def __init__(self, type, num_bits):
        self.type = type
        self.num_bits = num_bits
        self.num_words = (num_bits+31)//32
    def __repr__(self):
        return "ChemFPInfo(%r, %r)" % (self.type, self.num_bits)

_ob_types = {
    "FP2": (32, "OpenBabel-FP2/1", 1021),
    "FP3": ( 2, "OpenBabel-FP3/1",   55),
    "FP4": (16, "OpenBabel-FP3/1",  307), # Though it really only had 10 words.
    "MACCS": (8, "OpenBabel-MACCS/2", 166),
    }

def parse_error(msg):
    raise chemfp.ParseError(msg)
    
def get_chemfp_info(fpid, num_words):
    try:
        expected_num_words, chemfp_type, num_bits = _ob_types[fpid]
    except KeyError:
        # Odd. I wonder what this is about.
        chemfp_type = "FastSearch-" + str(fpid)
        num_bits = num_words * 32
    else:
        if num_words != expected_num_words:
            parse_error(
                "The %s fingerprint type should have %d words, not %d" %
                (fpid, expected_num_words, num_words))
    
    return ChemFPInfo(chemfp_type, num_bits)


    
## Read the header

# Helper functions to read fields from the file

def read_int(f, why):
    s = f.read(4)
    if len(s) != 4:
        parse_error("Cannot read the 4-byte integer for the %s" % (why,))
    n, = struct.unpack("<I", s)
    if n < 0:
        parse_error(
            "The 4-byte integer for the %s should not be negative. Got: %d"
            % (why, n))
    return n

def read_byte(f, why):
    s = f.read(1)
    if len(s) != 1:
        parse_error("Cannot read the byte for the %s" % (why,))

    n = ord(s)
    if n in (0, 1):
        return n
    parse_error("The byte for the %s must be 0 or 1, not %r" % (why, n))

def read_str(f, n, why):
    s = f.read(n)
    if len(s) != n:
        parse_error("Cannot read the %d bytes for the %s" % (n, why))
    return s.rstrip(b"\0")

    
def read_index_header(index_filename, index_file):
    f = index_file
    try:
        header_length = read_int(f, "header length")
        expected_header_length = 4*3 + 15 + 1 + 256
        if header_length != expected_header_length:
            parse_error("Expected a header size of %d but actually got %d. Is this an Open Babel fastindex file?"
                        % (header_length, expected_header_length))

        num_entries = read_int(f, "number of records")
        num_words = read_int(f, "number of integer words in a fingerprint")
        fpid = read_str(f, 15, "fingerprint type string")
        try:
            fpid = fpid.decode("utf8")
        except UnicodeDecodeError as err:
            parse_error("Cannot decode fingerprint type id %r as UTF-8: %s" % (fpid, err))

        seek64 = read_byte(f, "32/64 bit offset flag")
        data_filename = read_str(f, 256, "structure data filename")
        try:
            data_filename = data_filename.decode("utf8")
        except UnicodeDecodeError as err:
            parse_error("Could not decode data filename %r as UTF-8: %s" % (
                data_filename, err))

        loc = f.tell()
        if loc != header_length:
            parse_error("Should be at offset %d but actually at offset %d"
                        % (header_length, loc))

        chemfp_info = get_chemfp_info(fpid, num_words)
        
    except chemfp.ParseError as err:
        err.location = chemfp.io.Location.from_source(index_filename)
        raise
    
    return FastSearchIndexHeader(
        header_length = header_length,
        num_entries = num_entries,
        num_words = num_words,
        fpid = fpid, 
        seek64 = seek64,
        data_filename = data_filename,

        num_bits = chemfp_info.num_bits,
        chemfp_type = chemfp_info.type,
        )


class FastSearchIndex(object):
    def __init__(self, header, index_filename, data_filename,
                 index_file, index_file_close, data_file, index_date):
        self.header = header
        self.index_filename = index_filename
        self.data_filename = data_filename
        self.index_file = index_file
        self._index_file_close = index_file_close
        self.data_file = data_file
        self.index_date = index_date

        self._reader = None

        self.metadata = chemfp.Metadata(
            num_bits = header.num_bits,
            type = header.chemfp_type,
            sources = [data_filename],
            # chemfp 1.3 requires a string. chemfp 3.1 accepts a datetime
            date = index_date.isoformat().split(".", 1)[0]

            )

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def close(self):
        self.data_file.close() # Always close this file, because I opened it.
        if self._index_file_close is not None:
            self._index_file_close() # Only close this file if I opened it.

    def __iter__(self):
        if self._reader is None:
            self._reader = read_fingerprints(
                self.header, self.index_filename, self.index_file, self.data_file)
        return self._reader

##
CHUNK_SIZE = 1000

def read_entries(header, index_filename, index_file):
    fp_start = index_file.tell()

    fp_size = 4 * header.num_words
    num_bytes = header.num_bytes
    offset_start = fp_start + header.num_entries * fp_size

    if header.seek64:
        offset_size = 8
        unpack_offset = struct.Struct("<Q").unpack  # XXX "Q" or "q"?
    else:
        offset_size = 4
        unpack_offset = struct.Struct("<I").unpack # XXX "I" or "i"?
        
    for start in range(0, header.num_entries, CHUNK_SIZE):
        end = min(header.num_entries, start + CHUNK_SIZE)
        delta = end - start

        start_byte = fp_start + start * fp_size
        index_file.seek(start_byte)
        fingerprint_block = index_file.read(delta * fp_size)
        if len(fingerprint_block) != delta * fp_size:
            raise chemfp.ParseError("Tried to read %d fingerprint bytes (from seek offset), actually read %d"
                                    % (delta * fp_size, start_byte, len(fingerprint_block)),
                                    chemfp.io.Location.from_source(index_filename))

        start_byte = offset_start + start * offset_size
        index_file.seek(start_byte)
        offset_block = index_file.read(delta * offset_size)
        if len(offset_block) != delta * offset_size:
            raise chemfp.ParseError("Tried to read %d offset bytes (from seek offset %d), actually read %d"
                                    % (delta * fp_size, start_byte, len(fingerprint_block)),
                                    chemfp.io.Location.from_source(index_filename))

        for i in range(delta):
            offset_bytes = offset_block[i*offset_size:(i+1)*offset_size]
            offset, = unpack_offset(offset_bytes)
            
            yield fingerprint_block[i*fp_size:i*fp_size+num_bytes], offset

    
def read_fingerprints(header, index_filename, index_file, data_file):
    for index, (fp, offset) in enumerate(read_entries(header, index_filename, index_file)):
        #print("fp", fp, "offset", offset)
        id = data_file.get_id(index, offset)
        yield id, fp
    
##

_filename_types = (type(b""), type(u""))

def open_index(index_filename, data_filename=None, data_format=None,
               delimiter=None, id_type="id"):
    """Open the FastSearch .fs index file
    """
    if id_type is None:
        id_type = "id"
    if id_type not in ("id", "index", "offset"):
        raise ValueError("id_type must be one of 'id', 'index', or 'offset'")

    index_file_close = data_file_close = None
    
    try:
        if index_filename is None:
            raise ValueError("The chemfp_converters FastSearch file reader does not support reading from stdin.")
        elif isinstance(index_filename, _filename_types):
            # Open the index file, if it's a filename
            index_file = open(index_filename, "rb")
            # I opened it. I need to remember to close it.
            index_file_close = index_file.close
        else:
            # Otherwise, leave it as-is.
            # Don't need to close anything.
            index_file = index_filename
            index_file_close = None
            # Try to get a more useful filename
            index_filename = getattr(index_filename, "name", None)

        # Read the header.
        header = read_index_header(index_filename, index_file)

        if id_type in ("index", "offset"):
            if data_filename is None:
                try:
                    data_filename = find_data_filename(header, index_filename)
                except ValueError:
                    data_filename = header.data_filename
            if id_type == "index":
                data_file = IndexAsIdDatafile()
            else:
                data_file = OffsetAsIdDatafile()

        else:
            if data_filename is None:
                data_filename = find_data_filename(header, index_filename)
            # Open the structure data filename. The name can be specified,
            # otherwise the name from the index header will be used.
            data_file = open_datafile(data_filename, in_format=data_format, delimiter=delimiter)
            data_file_close = data_file.close

        # Chemfp would like a date. I'll use the file creation date.
        index_date = cmdsupport.get_file_creation_date(index_filename)

        return FastSearchIndex(header, index_filename, data_filename,
                               index_file, index_file_close, data_file, index_date)
    except:
        if data_file_close is not None:
            data_file_close()
        if index_file_close is not None:
            index_file_close()
        raise

#### Work with a structure data file

_use_unicode = cmdsupport.chemfp_supports_unicode

class Datafile(object):
    def __init__(self, datafile, parse_id_from_line):
        self.datafile = datafile
        self._parse_id_from_line = parse_id_from_line

    def close(self):
        self.datafile.close()

    def get_line(self, index):
        self.datafile.seek(index)
        line = self.datafile.readline().rstrip(b"\r\n")
        if _use_unicode:
            return line.decode("utf8", errors="replace")
        return line

    def get_id(self, index, offset):
        line = self.get_line(offset)
        return self._parse_id_from_line(line)

class IndexAsIdDatafile(object):
    def close(self):
        pass
    def get_id(self, index, offset):
        return str(index)

class OffsetAsIdDatafile(object):
    def close(self):
        pass
    def get_id(self, index, offset):
        return str(offset)

def find_data_filename(header, index_filename):
    data_filename = header.data_filename
    
    if os.path.exists(data_filename):
        return data_filename

    dirname = os.path.dirname(index_filename)
    if dirname != "":
        data_filename2 = os.path.join(dirname, data_filename)
        if os.path.exists(data_filename2):
            return data_filename2
        
    raise ValueError(
        "Could not find the data file %r referenced by %r"
        % (data_filename, index_filename))

## Open a structure data file given a filename.

# Need to detect the format and compression type
def guess_format(filename, args_format):
    if args_format is not None:
        format, compression = format.split(".")
        return format, compression

    s = filename.lower()
    if s.endswith(".gz"):
        compression = "gz"
        s = s[:-3]
    else:
        compression = None
        
    if s.endswith(".sdf") or s.endswith(".sd") or s.endswith(".mdl"):
        format = "sdf"
    else:
        format = "smi"
    return format, compression

def open_binary(filename, compression):
    if compression == "gz":
        import gzip
        f = gzip.open(filename, "rb")
    else:
        f = open(filename, "rb")
    return f


### Functions to get a record identifier given the first line of the record

def parse_sdf_title(line):
    return line

def parse_smi_whitespace(line):
    fields = line.split()
    if len(fields) > 1:
        return fields[1]
    else:
        return None

def parse_smi_to_eol(line):
    fields = line.split(None, 1)
    if len(fields) > 1:
        return fields[1]
    else:
        return None
    
def parse_smi_tab(line):
    fields = line.split("\t")
    if len(fields) > 1:
        return fields[1]
    else:
        return None
    
def parse_smi_space(line):
    fields = line.split(" ")
    if len(fields) > 1:
        return fields[1]
    else:
        return None

_parse_smi_table = {
    None: parse_smi_to_eol,
    "to-eol": parse_smi_to_eol,
    "whitespace": parse_smi_whitespace,
    "tab": parse_smi_tab,
    "space": parse_smi_space,
    }
    
##

def open_datafile(filename, in_format=None, delimiter=None):
    format, compression = guess_format(filename, in_format)

    try:
        f = open_binary(filename, compression)
    except IOError as err:
        die("Cannot open structure data file: %s" % (err,))

    try:
        # This can occur if you say the file is gzip'ed but it is not.
        try:
            f.read(0)
        except Exception as err:
            die("Cannot read from %r: %s" % (data_filename, err))

        if format == "sdf":
            parse_id = parse_sdf_title
        elif format == "smi":
            parse_id = _parse_smi_table[delimiter]
        else:
            raise ValueError("Unknown format %r" % (format,))

        return Datafile(f, parse_id)
    except:
        f.close()
        raise

#### For output

class OpenBabelTypeInfo(object):
    def __init__(self, fpid, num_words):
        self.fpid = fpid
        self.num_words = num_words
    
def get_openbabel_typeinfo(metadata):
    if metadata.num_bits is None:
        raise ValueError("metadata num_bits must be specified")
    
    for fpid, (num_words, chemfp_typename, num_bits) in _ob_types.items():
        if metadata.type == chemfp_typename:
            if metadata.num_bits != num_bits:
                raise ValueError("metadata num_bits must be %d, not %d" % (num_bits, metadata.num_bits))
            
            return OpenBabelTypeInfo(fpid, num_words)
        
    # See if it uses the "FastSearch-" hack
    chemfp_type = metadata.type
    if chemfp_type.startswith("FastSearch-"):
        ob_type = ob_typename[11:]
    else:
        # Use it as-is
        ob_type = chemfp_type
    if len(ob_type) > 15:
        raise ValueError("metadata type is too long: %r" % (chemfp_type,))

    return OpenBabelTypeInfo(ob_type, (chemfp.num_bits+31) // 32)
        
def write_int(outfile, i):
    outfile.write(struct.pack("I", i))
    
def write_fpid(outfile, fpid):
    fpid = fpid.encode("ascii")
    if len(fpid) > 15:
        raise ValueError("fpid may not have more than 15 characters")
    outfile.write(fpid + (b"\0"*(15-len(fpid))))

def write_byte(outfile, i):
    if i == 0:
        outfile.write(b"\0")
    elif i == 1:
        outfile.write(b"\1")
    else:
        raise AssertionError("Not implemented", i)

def write_data_filename(outfile, data_filename):
    data_filename = data_filename.encode("utf8")
    if len(data_filename) > 256:
        raise ValueErrror("UTF-8 encoded data filename must be no longer than 256 bytes")
    data_filename += b"\0" * (256 - len(data_filename))
    outfile.write(data_filename)

class WriteStatus(object):
    def __init__(self, num_output, num_failed):
        self.num_fingerprints = num_output + num_failed
        self.num_output = num_output
        self.num_failed = num_failed
    
def write_index(outfile, openbabel_typeinfo, data_filename,
                reader, record_offsets, verbose):
    write_int(outfile, 284)
    num_records_location = outfile.tell()
    write_int(outfile, 0) # Need to write this at the end
    write_int(outfile, openbabel_typeinfo.num_words)
    write_fpid(outfile, openbabel_typeinfo.fpid)

    if record_offsets and max(record_offsets.values()) > 2**31-1:
        seek64 = 1
        pack_code = "Q"
    else:
        seek64 = 0
        pack_code = "I"
        
    write_byte(outfile, seek64)

    write_data_filename(outfile, data_filename)

    num_failed = 0
    output_indices = []
    padding = None
    for id, fp in reader:
        try:
            offset = record_offsets[id]
        except KeyError:
            if verbose:
                sys.stderr.write("WARNING: Fingerprint %r not found in datafile.\n"
                                 % (id,))
            num_failed += 1
            continue

        if padding is None:
            padding = b"\0" * (openbabel_typeinfo.num_words*4 - len(fp))
            
        outfile.write(fp + padding)
        output_indices.append(offset)

    pack_1000 = struct.Struct(pack_code * 1000)
    for i in range(0, len(output_indices), 1000):
        subset = output_indices[i:i+1000]
        if len(subset) == 1000:
            output = pack_1000.pack(*subset)
        else:
            output = struct.pack(pack_code * len(subset), *subset)
        outfile.write(output)

    outfile.seek(num_records_location)
    write_int(outfile, len(output_indices))
        
    return WriteStatus(len(output_indices), num_failed)
