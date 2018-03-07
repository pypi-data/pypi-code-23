from __future__ import print_function, absolute_import, unicode_literals

# Dave Cosgrove's flush format
#   https://github.com/OpenEye-Contrib/Flush

# magic signature is b"100F"
# <int> number of bytes in fingerprint ('num_bytes')
# followed by records of the form:
#    <int> number of bytes in the id
#    identifier
#    num_bytes for the fingerprint

# num_bytes is always a multiple of 4, and interpreted as 32-bit integers

import os
import struct
import sys

import chemfp
import chemfp.io

from . import cmdsupport



###

# The bit patterns
# 0                                   63
# 1000000000000000000000000 ... 0000000
# 0100000000000000000000000 ... 0000000
# 0010000000000000000000000 ... 0000000
#    ...
# 0000000000000000000000000 ... 0000010
# 0000000000000000000000000 ... 0000001

# are stored as bytes in the flush file as:
#  00 00 00 80 00 00 00 00
#  00 00 00 40 00 00 00 00
#  00 00 00 20 00 00 00 00
#  00 00 00 10 00 00 00 00
#  00 00 00 08 00 00 00 00
#  00 00 00 04 00 00 00 00
#  00 00 00 02 00 00 00 00
#  00 00 00 01 00 00 00 00
#  00 00 80 00 00 00 00 00
#  00 00 40 00 00 00 00 00
#   ...
#  04 00 00 00 00 00 00 00
#  02 00 00 00 00 00 00 00
#  01 00 00 00 00 00 00 00
#  00 00 00 00 00 00 00 80
#  00 00 00 00 00 00 00 40
#    ...
#  00 00 00 00 01 00 00 00

# Chemfp expects them to be:
#  01 00 00 00 00 00 00 00
#  02 00 00 00 00 00 00 00
#  04 00 00 00 00 00 00 00
#  08 00 00 00 00 00 00 00
#  10 00 00 00 00 00 00 00
#  20 00 00 00 00 00 00 00
#   ...
#  00 00 00 40 00 00 00 00
#  00 00 00 80 00 00 00 00
#  00 00 00 00 01 00 00 00
#  00 00 00 00 02 00 00 00
#   ...
#  00 00 00 00 00 00 00 80

# That is, it Flush uses the opposite bit endian as chemfp, and reverses each set of 4 bytes.

# The conversion from a bitstring like:
#   s = "0101000000001100110000101000101010000000011010100111010000111000"
# to bytes in the Flush file is:
#   import struct
#   t = b"".join([struct.pack("I", int(s[i:i+32], 2)) for i in range(0, len(s), 32)])
# which in this example gives:
#   b'\x8a\xc2\x0cP8tj\x80'


_transtable = (
    b'\x00\x80@\xc0 \xa0`\xe0\x10\x90P\xd00\xb0p\xf0\x08\x88H\xc8(\xa8h'
    b'\xe8\x18\x98X\xd88\xb8x\xf8\x04\x84D\xc4$\xa4d\xe4\x14\x94T\xd44'
    b'\xb4t\xf4\x0c\x8cL\xcc,\xacl\xec\x1c\x9c\\\xdc<\xbc|\xfc\x02\x82B'
    b'\xc2"\xa2b\xe2\x12\x92R\xd22\xb2r\xf2\n\x8aJ\xca*\xaaj\xea\x1a\x9aZ'
    b'\xda:\xbaz\xfa\x06\x86F\xc6&\xa6f\xe6\x16\x96V\xd66\xb6v\xf6\x0e'
    b'\x8eN\xce.\xaen\xee\x1e\x9e^\xde>\xbe~\xfe\x01\x81A\xc1!\xa1a\xe1'
    b'\x11\x91Q\xd11\xb1q\xf1\t\x89I\xc9)\xa9i\xe9\x19\x99Y\xd99\xb9y\xf9'
    b'\x05\x85E\xc5%\xa5e\xe5\x15\x95U\xd55\xb5u\xf5\r\x8dM\xcd-\xadm\xed'
    b'\x1d\x9d]\xdd=\xbd}\xfd\x03\x83C\xc3#\xa3c\xe3\x13\x93S\xd33\xb3s'
    b'\xf3\x0b\x8bK\xcb+\xabk\xeb\x1b\x9b[\xdb;\xbb{\xfb\x07\x87G\xc7\''
    b'\xa7g\xe7\x17\x97W\xd77\xb7w\xf7\x0f\x8fO\xcf/\xafo\xef\x1f\x9f_'
    b'\xdf?\xbf\x7f\xff'
    )

###

class FlushFile(chemfp.FingerprintIterator):
    pass

_filename_types = (type(b""), type(u""))

def open_flush(flush_filename, location=None):
    creation_date = None
    
    def flush_file_close():
        pass
    
    if flush_filename is None:
        flush_file = sys.stdout
        # Get the binary stdout under Python 3
        flush_file = getattr(flush_file, "buffer", flush_file)
        source = None
        
    elif isinstance(flush_filename, _filename_types):
        creation_datetime = cmdsupport.get_file_creation_date(flush_filename)
        if creation_datetime is not None:
            # chemfp 1.3 requires a string. chemfp 3.1 accepts a datetime
            creation_date = creation_datetime.isoformat().split(".", 1)[0]

        # Open the file
        flush_file = open(flush_filename, "rb")
        flush_file_close = flush_file.close
        source = flush_filename
    else:
        # Should be a file object
        flush_file = flush_filename
        source = getattr(flush_file, "name", None)

    try:
        if location is None:
            location = chemfp.io.Location.from_source(source)
        
        magic = flush_file.read(4)
        if magic != b"100F":
            location.save(offsets=(0, 4))
            s = repr(magic)
            if s[:1] == "b":
                s = s[1:]
            raise chemfp.ParseError("Expected flush file identifier '100F' but got %s"
                                     % (s,), location)

        fp_size_bytes = flush_file.read(4)
        if len(fp_size_bytes) != 4:
            location.save(offsets=(4, 8))
            raise chemfp.ParseError(
                "Incomplete read for the number of bytes in a Flush file fingerprint.",
                location)

        fp_size, = struct.unpack("I", fp_size_bytes)
        assert fp_size >= 0
        if fp_size == 0:
            location.save(offsets=(4, 8))
            raise chemfp.ParseError(
                "Chemfp does not support fingerprints with length 0.",
                location)
        if fp_size % 4 != 0:
            locations.save(offsets=(4, 8))
            raise chemfp.ParseError(
                "Fingerprint size %d is not a multiple of 4" % (fp_size,),
                location)
            
        if fp_size > 16384:
            # Is this too low?
            location.save(offsets=(4, 8))
            raise chemfp.ParseError(
                "Fingerprint size of %d is larger than 16384, which is the largest supported fingerprint size.",
                location)
        
        id_fp_iter = iter_flush_records(fp_size, flush_file, flush_file_close, location)
        
        metadata = chemfp.Metadata(
            num_bytes = fp_size,  # XXX If I leave this out I get an interesting error message
            date = creation_date,
            )
            
        return FlushFile(metadata, id_fp_iter, location, id_fp_iter.close)
    except:
        flush_file_close()
        raise
    
def iter_flush_records(fp_size, infile, close, location):
    id_fp_iter = _iter_flush_records(fp_size, infile, close, location)
    next(id_fp_iter)
    return id_fp_iter

def _iter_flush_records(fp_size, infile, close, location):
    recno = 0
    start_offset = end_offset = 8

    unpack_int = struct.Struct("I").unpack
    
    def get_recno():
        return recno

    def get_offsets():
        return (start_offset, end_offset)

    transtable = _transtable
    use_unicode = cmdsupport.chemfp_supports_unicode
    try:
        yield "Ready!"

        while 1:
            s = infile.read(4)
            if not s:
                break
            if len(s) != 4:
                raise chemfp.ParseError("Incomplete record at identifier length", location)
            n, = unpack_int(s)
            assert n >= 0
            if n == 0:
                raise chemfp.ParseError("Empty identifier", location)
            if n > 4000:
                raise chemfp.ParseError("Identifier length too long", location)
            id = infile.read(n)
            if len(id) != n:
                raise chemfp.ParseError("Incomplete record in indentifier", location)
            fp = infile.read(fp_size)
            if len(fp) != fp_size:
                raise chemfp.ParseError("Incomplete record in fingerprint", location)
            fp = fp.translate(transtable)
            fp = b"".join(fp[i:i+4][::-1] for i in range(0, len(fp), 4))
            
            end_offset = start_offset + 4 + n + fp_size
            if use_unicode:
                yield (id.decode("utf8"), fp)
            else:
                yield id, fp
            start_offset = end_offset
        
    finally:
        location.save(recno = get_recno(),
                      offsets = get_offsets())

        close()
        
    
### write

def _check_num_bytes(num_bytes):
    if num_bytes is None:
        raise ValueError("metadata num_bytes must be specified")
    if num_bytes <= 0:
        raise ValueError("metadata num_bytes must be positive")
    if num_bytes % 4 != 0:
        raise ValueError("metadata num_bytes (%d) must be a multiple of 4" % (num_bytes,))
    if num_bytes > 16384:
        raise ValueError("metadata num_bytes (%d) must be no larger than 16384" % (num_bytes,))

def _write_header(outfile, num_bytes):
    outfile.write(b"100F")
    fp_size_bytes = struct.pack("I", num_bytes)
    outfile.write(fp_size_bytes)
        
def open_fingerprint_writer(destination, metadata=None, location=None):
    if metadata is not None:
        num_bytes = metadata.num_bytes
        _check_num_bytes(num_bytes)
    else:
        num_bytes = None

    if location is None:
        location = chemfp.io.Location.from_destination(destination)
    
    def close():
        pass
    
    if destination is None:
        outfile = sys.stdout
        # Get the binary output under Python 3
        outfile = getattr(outfile, "buffer", outfile)
        
    elif isinstance(destination, _filename_types):
        outfile = open(destination, "wb")
        close = outfile.close
        
    else:
        outfile = destination

    # Write the header
    if num_bytes is not None:
        _write_header(outfile, num_bytes)
    
    return FlushFingerprintWriter(outfile, close, num_bytes, metadata, location)

_pack_int = struct.Struct("I").pack
class FlushFingerprintWriter(chemfp.FingerprintWriter):
    def __init__(self, outfile, close, num_bytes, metadata, location):
        self._outfile = outfile
        self._close = close
        self._num_bytes = num_bytes
        self.metadata = metadata
        self.location = location

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def close(self):
        self._close()

    def _finish_header(self, fp):
        assert self._num_bytes is None
        num_bytes = len(fp)
        _check_num_bytes(num_bytes)
        _write_header(self._outfile, num_bytes)
        self._num_bytes = num_bytes
        
    def write_fingerprint(self, id, fp):
        id_bytes = id.encode("utf8")
        id_size_bytes = _pack_int(len(id_bytes))
        if self._num_bytes is None:
            self._finish_header(fp)
        if len(fp) != self._num_bytes:
            raise ValueError("fingerprint is %d bytes long but it should be %d"
                             % (len(fp), self._num_bytes))
        # Convert to Flush byte order
        fp = b"".join(fp[i:i+4][::-1] for i in range(0, len(fp), 4))
        fp = fp.translate(_transtable)
        
        self._outfile.write(id_size_bytes + id_bytes + fp)

    def write_fingerprints(self, id_fp_pairs):
        pack = _pack_int
        num_bytes = self._num_bytes
        write = self._outfile.write
        transtable = _transtable
        
        for id, fp in id_fp_pairs:
            id_bytes = id.encode("utf8")
            id_size_bytes = pack(len(id_bytes))
            if len(fp) != num_bytes:
                if num_bytes is None:
                    self._finish_header(fp)
                    num_bytes = self._num_bytes
                else:
                    raise ValueError("fingerprint is %d bytes long but it should be %d"
                                    % (len(fp), self._num_bytes))
            # Convert to Flush byte order
            fp = b"".join(fp[i:i+4][::-1] for i in range(0, len(fp), 4))
            fp = fp.translate(transtable)
            write(id_size_bytes + id_bytes + fp)
