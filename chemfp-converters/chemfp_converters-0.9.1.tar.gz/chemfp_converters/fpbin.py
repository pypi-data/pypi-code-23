from __future__ import print_function, absolute_import

# OEChem's FastFingerprintDatabase format.
# The OEChem API doesn't have a way to read/write a .fpbin file.
# Instead, I do it myself.

# The file contains a header with 800 bytes.

# The header starts with a set of lines, ending with b"\n":
# - line 1 is b"LE\n". I assume it means "little endian". I don't have a big-endian
#    machine for testing
# - line 2 is the 'moldb' filename containing the molecules used to generate the fingerprints
# - line 3 is the OEGraphSim fingerprint type string
# - line 4 is the number of fingerprints, as ASCII text
#
# The header is then NUL padded to 784 bytes.
#
# The next 8 bytes is the size of the fingerprint, as a multiple of an 8-byte word.
# The last 8 bytes is the number of fingerprints. This must match the earlier number.

import os
import errno
import sys
import struct
import re

import chemfp
import chemfp.io
from chemfp import bitops

from . import cmdsupport

class FPBinIOError(IOError):
    pass

class MolDBIOError(IOError):
    pass

class MismatchError(ValueError):
    pass

class LicenseError(ValueError):
    pass

class FPBinHeader(object):
    def __init__(self, signature, moldb_filename, oetype_str, oetype, num_fingerprints, num_words):
        self.signature = signature
        self.moldb_filename = moldb_filename
        self.oetype_str = oetype_str
        self.oetype = oetype
        self.num_fingerprints = num_fingerprints
        self.num_words = num_words

    def __repr__(self):
        return "FPBinHeader(signature=%r, moldb_filename=%r, oetype_str=%r, num_fingerprints=%d, num_words=%d)" % (
            self.signature, self.moldb_filename, self.oetype_str, self.num_fingerprints, self.num_words)

    def get_metadata(self):
        if self.oetype is None:
            type = self.oetype_str
        else:
            try:
                type = self.oetype.to_chemfp_type()
            except ValueError as err:
                sys.stderr.write("Cannot convert to a chemfp fingerprint type: %s" % (err,))
            
        return chemfp.Metadata(
            num_bytes = self.num_words*8,
            type = type,
            )


def _getline(header, offset, what, location):
    i = header.find(b"\n", offset)
    if i == -1:
        raise chemfp.ParseError("unable to read %d header line", location)
    #print("Looking for", what, "got", header[offset:i])
    return i+1, header[offset:i]

def read_header(infile, location):
    header = infile.read(800)
    if type(header) != type(b""):
        raise chemfp.ParseError("file must be open in binary mode", location)
    
    if not header:
        raise chemfp.ParseError("missing header", location)
        
    if len(header) != 800:
        raise chemfp.ParseError("unexpected format", location)

    signature = header[:3]
    if signature != b"LE\n":
        raise chemfp.ParseError(
            "unsupported header signature %r" % (signature,),
            location)

    offset, moldb_filename_bytes = _getline(header, 3, "filename", location)
    try:
        moldb_filename = moldb_filename_bytes.decode("utf8")
    except UnicodeDecodeError as err:
        raise chemfp.ParseError(
            "non-UTF-8 characters in filename: %s" % (err,),
            location)
    
    offset, oetype_bytes = _getline(header, offset, "type", location)
    try:
        oetype_str = oetype_bytes.decode("ascii")
    except UnicodeDecodeError:
        raise chemfp.ParseError(
            "non-ASCII characters in oetype: %r"
            % (oetype_bytes,),
            location)
    try:
        oetype = parse_oetype_string(oetype_str)
    except ValueError:
        oetype = None
    
    offset, num_fingerprints_str = _getline(header, offset, "size", location)
    try:
        num_fingerprints = int(num_fingerprints_str)
    except ValueError:
        raise chemfp.ParseError(
            "number of fingerprints must contain an integer: %r"
            % (num_fingerprints_str,),
            location)
    
    if num_fingerprints < 0:
        raise chemfp.ParseError(
            "number of fingerprints must be non-negative: %r"
            % (num_fingerprints,),
            location)

    if offset > 784:
        raise chemfp.ParseError("field overrun header", location)

    remainder = header[offset:784]
    if remainder.count(b"\0") != len(remainder):
        raise chemfp.ParseError(
            "unexpected non-NUL content header",
            location)
    
    num_words, num_fingerprints2 = struct.unpack("QQ", header[784:])

    if num_words < 0:
        raise chemfp.ParseError(
            "fingerprint word count must be positive: %d"
            % (num_words,),
            location)

    if num_words*64 > 16384:
        # While I could, no one should (?), and this also serves as a check that 
        raise chemfp.ParseError(
            "chemfp_converter does not support OEChem .fpbin files with fingerprints longer than longer 16384 bits: %d"
            % (num_words*64,),
            location)

    if num_fingerprints != num_fingerprints2:
        raise chemfp.ParseError("mismatch between header fingerprint counts: %d != %d"
                             % (num_fingerprints, num_fingerprints2),
                             location)
    
    return FPBinHeader(
        signature,
        moldb_filename,
        oetype_str,
        oetype,
        num_fingerprints,
        num_words)

###

_str_is_bytes = type("") == type(b"")

def open_moldb(filename):
    from openeye.oechem import OEMolDatabase, OEChemIsLicensed

    if not OEChemIsLicensed():
        raise LicenseError("OEChem could not find a valid license")
    moldb = OEMolDatabase()

    if isinstance(filename, type(u"")):
        if _str_is_bytes:
            filename = filename.encode("utf8")
    if not moldb.Open(filename):
        # See if I can get Python to raise an exception for me.
        try:
            open(filename).close()
        except IOError as err:
            raise MolDBIOError(err.errno, err.strerror, err.filename)
        raise MolDBIOError(err.EIO, "OEChem cannot open the file", err.filename)
            
    return MolDB(moldb)

class MolDB(object):
    def __init__(self, moldb):
        self.moldb = moldb
        self._num_molecules = moldb.NumMols()

    def __len__(self):
        return self._num_molecules
        
    def get_id(self, i):
        if 0 <= i < self._num_molecules:
            return self.moldb.GetTitle(i)
        return None
    
    def close(self):
        # XXX Is there no way to close an OEChem MolDB?
        pass
        

class IntegerIdMolDB(object):
    def __init__(self, num_fingerprints):
        self._num_fingerprints = num_fingerprints
    def __len__(self):
        return self._num_fingerprints
    def close(self):
        pass
    def get_id(self, i):
        return str(i)

class BaseFPBinReader(object):
    def __init__(self, metadata, fpbin_header, reader):
        self.metadata = metadata
        self.fpbin_header = fpbin_header
        self.reader = reader

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def __iter__(self):
        return self.reader

    def close(self):
        self.reader.close()

class FPBinRecordReader(BaseFPBinReader):
    pass

class FPBinFingerprintReader(BaseFPBinReader):
    pass

    
    
_filename_types = (type(b""), type(u""))

def _open_fpbin(fpbin_filename, location):
    if location is None:
        location = chemfp.io.Location.from_source(fpbin_filename)
    location.save(record_format="fpbin")
    
    fpbin_close = None
    fpbin_date = None
    if fpbin_filename is None:
        fpbin = getattr(sys.stdin, "buffer", sys.stdin)
        fpbin_close = None
    elif isinstance(fpbin_filename, _filename_types):
        try:
            fpbin = open(fpbin_filename, "rb")
        except IOError as err:
            raise FPBinIOError(err.errno, err.strerror, err.filename)
        fpbin_close = fpbin.close
        fpbin_date = cmdsupport.get_file_creation_date(fpbin_filename)
    else:
        fpbin = fpbin_filename
        fpbin_filename = getattr(fpbin, "name", None)

    return fpbin, fpbin_close, fpbin_date, location

def read_fpbin_records(fpbin_filename, location=None):
    fpbin, fpbin_close, fpbin_date, location = _open_fpbin(fpbin_filename, location)
    try:
        fpbin_header = read_header(fpbin, location)
            
        num_bytes = fpbin_header.num_words * 8
        return FPBinRecordReader(
            metadata = fpbin_header.get_metadata().copy(date=fpbin_date),
            fpbin_header = fpbin_header,
            reader = iter_fpbin_fingerprints(fpbin, fpbin_close, None, num_bytes, location)
            )
    except:
        if fpbin_close is not None:
            fpbin_close()
        raise


def read_fpbin_fingerprints(fpbin_filename, moldb_filename=None,
                            use_index_as_id=False, location=None):
    moldb = None
    fpbin, fpbin_close, fpbin_date, location = _open_fpbin(fpbin_filename, location)
    try:
        fpbin_header = read_header(fpbin, location)

        if use_index_as_id:
            # iterate using indices as ids
            moldb = IntegerIdMolDB(fpbin_header.num_fingerprints)
        else:
            if moldb_filename is None:
                # Use a search path?
                moldb_filename = fpbin_header.moldb_filename
                if not moldb_filename:
                    raise chemfp.ParseError(
                        "No moldb_filename given and the .fpbin file contains an empty filename",
                        location)
            
            moldb = open_moldb(moldb_filename)

        if len(moldb) != fpbin_header.num_fingerprints:
            raise MismatchError(
                "fpbin file %r contains %d fingerprints while moldb file %r contains %d molecules"
                % (location.filename, fpbin_header.num_fingerprints, moldb_filename, len(moldb)))

        metadata = fpbin_header.get_metadata().copy(date=fpbin_date)
        
        return FPBinFingerprintReader(
            metadata = metadata,
            fpbin_header = fpbin_header,
            reader = iter_fpbin_fingerprints(fpbin, fpbin_close, moldb, metadata.num_bytes, location)
            )
        
    except:
        if moldb is not None:
            moldb.close()
        if fpbin_close is not None:
            fpbin_close()
        raise
    

def iter_fpbin_records(fpbin, fpbin_close, num_bytes, location):
    it = _iter_fpbin_records(fpbin, fpbin_close, None, num_bytes, location)
    assert next(it) == "Ready!"
    return it

def iter_fpbin_fingerprints(fpbin, fpbin_close, moldb, num_bytes, location):
    it = _iter_fpbin_records(fpbin, fpbin_close, moldb, num_bytes, location)
    assert next(it) == "Ready!"
    return it

def _iter_fpbin_records(fpbin, fpbin_close, moldb, num_bytes, location):
    assert num_bytes > 0

    record_size = 16 + num_bytes
    
    recno = 0
    def get_recno():
        return recno
    
    record_bytes = None
    def get_record():
        return record_bytes
    
    def get_offsets():
        start = 800 + (recno-1)*record_size
        return start, start+record_size
    
    mol = None
    def get_mol():
        return mol
    
    location.register(
        get_recno=get_recno,
        get_record=get_record,
        get_offsets=get_offsets,
        get_mol=get_mol
        )
    max_popcount = num_bytes * 8

    unpack = struct.Struct("QQ%ds" % (num_bytes,)).unpack
    
    try:
        yield "Ready!"
        while 1:
            record_bytes = fpbin.read(record_size)
            if not record_bytes:
                break
            recno += 1
            if len(record_bytes) != record_size:
                raise chemfp.ParseError("Incomplete record", location)
            index, popcount, fp = mol = unpack(record_bytes)
            if popcount < 0 or popcount > max_popcount:
                raise chemfp.ParseError("Popcount out of range", location)

            if moldb is None:
                # Iterate over records, as a "molecule"
                yield mol
            else:
                # Iterate over (id, fingerprint)
                id = moldb.get_id(index)
                if id is None:
                    # XXX pass in 'errors'?
                    sys.stderr.write("Missing id for index %d. Skipping record.\n"
                                     % (index,))
                else:
                    yield id, fp
    
    finally:
        location.save(
            recno=recno,
            record=None,
            offsets=None,
            mol=None,
            )

        if moldb is not None:
            moldb.close()
        if fpbin_close is not None:
            fpbin_close()

########  Writer

def pack_fpbin_header(fpbin_header, num_fingerprints=None):
    # Allow an override (used during close to set the final count)
    if num_fingerprints is None:
        num_fingerprints = fpbin_header.num_fingerprints

    header_bytes = (
        b"LE\n" +
        fpbin_header.moldb_filename.encode("utf8") + b"\n" +
        fpbin_header.oetype_str.encode("utf8") + b"\n" +
        str(num_fingerprints).encode("ascii") + b"\n"
        )
        
    n = len(header_bytes)
    if n < 784:
        header_bytes += b"\0"*(784-n)
    elif n > 784:
        raise ValueError("Not enough space in the header (is the moldb filename or type string very long?)")

    header_bytes += struct.pack("QQ", fpbin_header.num_words, num_fingerprints)
    assert len(header_bytes) == 800, len(header_bytes)

    return header_bytes
        
            
def open_fpbin_writer(destination, moldb_filename, oetype_str, num_bytes, num_fingerprints=0):
    if not oetype_str:
        raise ValueError("Missing oetype_str")
    
    if not (num_bytes > 0):
        raise ValueError("num_bytes must be positive")
        
    if num_bytes % 8 != 0:
        raise ValueError("num_bytes must be a multiple of 8")

    fpbin_header = FPBinHeader(
        b"LE\n",
        moldb_filename,
        oetype_str,
        None,
        num_fingerprints,
        num_bytes // 8
        )
    header_bytes = pack_fpbin_header(fpbin_header)
    
    outfile = open(destination, "wb")
    outfile_close = outfile.close
    try:
        outfile.write(header_bytes)
        return FPBinWriter(fpbin_header, outfile, outfile_close)
    except:
        outfile_close()
        raise
    

class FPBinWriter(object):
    def __init__(self, fpbin_header, outfile, outfile_close):
        self._fpbin_header = fpbin_header
        self._outfile = outfile
        self._outfile_close = outfile_close
        self._num_bytes = num_bytes = fpbin_header.num_words * 8
        self._pack = struct.Struct("QQ%ds" % (num_bytes,)).pack
        self._recno = self._output_recno = 0

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def __del__(self):
        self.close()
        
    def close(self):
        if self._outfile_close is not None:
            self._outfile.seek(0)
            self._outfile.write(pack_fpbin_header(self._fpbin_header, self._output_recno))
            self._outfile_close()
            self._outfile_close = None

    def write_fingerprint(self, id, fp):
        self._recno += 1
        if len(fp) != self._num_bytes:
            raise ValueError("fingerprint %d must contain %d bytes not %d"
                                 % (self._recno, self._num_bytes, len(fp)))

        popcount = bitops.byte_popcount(fp)
        self._outfile.write(self._pack(index, popcount, fp))
        self._output_recno += 1

    def write_fingerprints(self, id_fp_iter):
        num_bytes = self._num_bytes
        pack = self._pack
        byte_popcount = bitops.byte_popcount

        for id, fp in id_fp_iter:
            self._recno += 1
            index = self._output_recno
            popcount = byte_popcount(fp)
            self._outfile.write(self._pack(index, popcount, fp))
            self._output_recno = index + 1
        
        
            
########  Convert from OEGraphSim <-> chemfp fingerprint type strings

class BaseOEFPType(object):
    pass

def _check_keys(kv_pairs, keys, oetype):
    if len(kv_pairs) != len(keys):
        raise ValueError("expected %d key=value pairs in oetype %r" % (len(kv_pairs), oetype))
    for pos, (kv_pair, expected_k) in enumerate(zip(kv_pairs, keys), 1):
        if kv_pair[0] != expected_k:
            raise ValueError("expected key %r in position %d, got key %r"
                             % (expected_k, pos, kv_pair[0]))

def _check_size(kv_pair, oetype):
    k, v = kv_pair
    if not v.isdigit():
        raise ValueError("unable to parse %s in oetype %r" % (k, oetype))
    size = int(v)
    if size == 0:
        raise ValueError("%s must be positive in oetype %r" % (k, oetype))
    return size
        
def _check_range(kv_pair, oetype):
    k, v = kv_pair
    left, mid, right = v.partition("-")
    if ((not left) or (mid != "-") or (not right)
            or (not left.isdigit()) or (not right.isdigit())):
        raise ValueError("cannot parse %s range in oetype %r" % (k, v, oetype))
    min = int(left)
    max = int(right)
    if min < 0 or not (min <= max):
        raise ValueError("unsupported %s range in oetype %r" % (k, oetype))
    return (min, max)

_canonical_atype_terms = ( # These are in OEChem canonical order
    "AtmNum",
    "Arom",
    "Chiral",
    "FCharge",
    "HvyDeg",
    "Hyb",
    "InRing",
    "HCount",
    "EqArom",
    "EqHalo",
    "EqHBAcc",
    "EqHBDon",
    )

def _check_atype(kv_pair, oetype):
    k, v = kv_pair
    assert k == "atype", k
    if v == "None":
        return []
    terms = v.split("|")
    for term in terms:
        if term not in _canonical_atype_terms:
            raise ValueError("unexpected atype term %r in oetype %r" % (term, oetype))
    return terms

_canonical_btype_terms = ("Order", "Chiral", "InRing") # These are in OEChem canonical order

def _check_btype(kv_pair, oetype):
    k, v = kv_pair
    assert k == "btype", k
    if v == "None":
        return []
    terms = v.split("|")
    for term in terms:
        if term not in _canonical_btype_terms:
            raise ValueError("unexpected btype term %r in oetype %r" % (term, oetype))
    return terms


# Path,ver=2.0.0,size=4096,bonds=0-5,atype=AtmNum|Arom|Chiral|FCharge|HvyDeg|Hyb|EqHalo,btype=Order|Chiral
# OpenEye-Path/2 numbits=4096 minbonds=0 maxbonds=5 atype=Arom|AtmNum|Chiral|EqHalo|FCharge|HvyDeg|Hyb btype=Order|Chiral

def _oe_atype(atype_terms):
    if not atype_terms:
        return "None"
    # XXX What if a term isn't available? There will be a ValueError.
    return "|".join(sorted(atype_terms, key=_canonical_atype_terms.index))
    
def _oe_btype(btype_terms):
    if not btype_terms:
        return "None"
    # XXX What if a term isn't available? There will be a ValueError.
    return "|".join(sorted(btype_terms, key=_canonical_btype_terms.index))

def _chemfp_atype(atype_terms):
    if not atype_terms:
        return "0"
    return "|".join(sorted(atype_terms))

# The terms should be in alphabetical order, but internally it sorted
# on the flags "BondOrder" rather than "Order".
# As a result, the order is "Order", "Chiral", "InRing"
def _chemfp_btype(btype_terms):
    if not btype_terms:
        return "0"
    return "|".join(sorted(btype_terms, key=_canonical_btype_terms.index))


class PathFPType(BaseOEFPType):
    def __init__(self, version, size, minbonds, maxbonds, atype_terms, btype_terms):
        self.version = version
        self.size = size
        self.minbonds = minbonds
        self.maxbonds = maxbonds
        self.atype_terms = atype_terms
        self.btype_terms = btype_terms

    def __eq__(self, other):
        return (isinstance(other, PathFPType)
                and self.version == other.version
                and self.size == other.size
                and self.minbonds == other.minbonds
                and self.maxbonds == other.maxbonds
                and sorted(self.atype_terms) == sorted(other.atype_terms)
                and sorted(self.btype_terms) == sorted(other.btype_terms))
    
    def __repr__(self):
        return "PathFPType(version=%r, size=%d, minbonds=%d, maxbonds=%d, atype_terms=%r, btype_terms=%r)" % (
            self.version, self.size, self.minbonds, self.maxbonds, self.atype_terms, self.btype_terms)
        
    def to_oetype(self):
        return "Path,ver=%s,size=%d,bonds=%d-%d,atype=%s,btype=%s" % (
            self.version, self.size, self.minbonds, self.maxbonds,
            _oe_atype(self.atype_terms), _oe_btype(self.btype_terms))

    def to_chemfp_type(self):
        if self.version == "2.0.0":
            t = "OpenEye-Path/2"
        else:
            t = "OpenEye-Path/" + self.version
            
        t += " numbits=%d minbonds=%d maxbonds=%d" % (self.size, self.minbonds, self.maxbonds)

        t += " atype=" + _chemfp_atype(self.atype_terms)
        t += " btype=" + _chemfp_btype(self.btype_terms)
        return t

def _parse_oe_path(oetype, kv_pairs):
    _check_keys(kv_pairs, ("ver", "size", "bonds", "atype", "btype"), oetype)

    version = kv_pairs[0][1]
    size = _check_size(kv_pairs[1], oetype)
    min, max = _check_range(kv_pairs[2], oetype)
    atype_terms = _check_atype(kv_pairs[3], oetype)
    btype_terms = _check_btype(kv_pairs[4], oetype)

    return PathFPType(version, size, min, max, atype_terms, btype_terms)

def _check_settings(chemfp_type, tokenized_type, allowed_settings):
    tt = tokenized_type
    d = {}
    for (name, value) in tt.settings:
        if name not in allowed_settings:
            raise ValueError("%s does not take a %s parameter: %r"
                                 % (tt.base_name, name, chemfp_type))
        if name in d:
            raise ValueError("parameter %r must occur only once: %r"
                                 % (name, chemfp_type))
        if name == "numbits":
            if not value.isdigit():
                raise ValueError("numbits must be an integer: %r"
                                     % (chemfp_type,))
            n = int(value)
            if not (1 <= n <= 32768):
                raise ValueError("numbits must be between 1 and 32768, inclusive: %r"
                                     % (chemfp_type,))
            d["numbits"] = n
            
        elif name == "minbonds":
            if not value.isdigit():
                raise ValueError("minbonds must be an integer: %r"
                                     % (chemfp_type,))
            d["minbonds"] = int(value)
            
        elif name == "maxbonds":
            if not value.isdigit():
                raise ValueError("maxbonds must be an integer: %r"
                                     % (chemfp_type,))
            d["maxbonds"] = int(value)

        elif name == "minradius":
            if not value.isdigit():
                raise ValueError("minradius must be an integer: %r"
                                     % (chemfp_type,))
            d["minradius"] = int(value)
            
        elif name == "maxradius":
            if not value.isdigit():
                raise ValueError("maxradius must be an integer: %r"
                                     % (chemfp_type,))
            d["maxradius"] = int(value)
            
        elif name == "atype":
            if value == "0":
                terms = []
            else:
                terms = value.split("|")
                for term in terms:
                    if term not in _canonical_atype_terms:
                        raise ValueError("unsupported atype term %r: %r"
                                             % (term, chemfp_type))
            d["atype"] = terms
            
        elif name == "btype":
            if value == "0":
                terms = []
            else:
                terms = value.split("|")
                for term in terms:
                    if term not in _canonical_btype_terms:
                        raise ValueError("unsupported atype term %r: %r"
                                             % (term, chemfp_type))
            d["btype"] = terms

        else:
            # Should not get here
            raise AssertionError((name, chemfp_type))

    for setting in allowed_settings:
        if setting not in d:
            raise ValueError("fingerprint type missing field %r: %r"
                                 % (setting, chemfp_type))

    retval = {
        "size": d["numbits"],
        "atype_terms": d["atype"],
        "btype_terms": d["btype"],
        }
        
    if "minbonds" in d:
        if d["minbonds"] > d["maxbonds"]:
            raise ValueError("maxbonds must not be smaller than minbonds: %r"
                                 % (chemfp_type,))
        retval["minbonds"] = d["minbonds"]
        retval["maxbonds"] = d["maxbonds"]
        assert "minradius" not in d
        assert "maxradius" not in d
    else:
        assert "minradius" in d
        assert "maxbonds" not in d
        if d["minradius"] > d["maxradius"]:
            raise ValueError("maxradius must not be smaller than minradius: %r"
                                 % (chemfp_type,))
        retval["minradius"] = d["minradius"]
        retval["maxradius"] = d["maxradius"]

    return retval
            
        
            
                
def _parse_chemfp_path(chemfp_type, tokenized_type):
    tt = tokenized_type
    if tt.version == "2":
        version = "2.0.0"
    else:
        version = tt.version

    d = _check_settings(chemfp_type, tokenized_type,
                        ("numbits", "minbonds", "maxbonds", "atype", "btype"))
    return PathFPType(version=version, **d)
    

# Circular,ver=2.0.0,size=4096,radius=0-5,atype=AtmNum|Arom|Chiral|FCharge|HCount|EqHalo,btype=Order
# OpenEye-Circular/2 numbits=4096 minradius=0 maxradius=5 atype=Arom|AtmNum|Chiral|EqHalo|FCharge|HCount btype=Order

class CircularFPType(BaseOEFPType):
    def __init__(self, version, size, minradius, maxradius, atype_terms, btype_terms):
        self.version = version
        self.size = size
        self.minradius = minradius
        self.maxradius = maxradius
        self.atype_terms = atype_terms
        self.btype_terms = btype_terms

    def __eq__(self, other):
        return (isinstance(other, CircularFPType)
                and self.version == other.version
                and self.size == other.size
                and self.minradius == other.minradius
                and self.maxradius == other.maxradius
                and sorted(self.atype_terms) == sorted(other.atype_terms)
                and sorted(self.btype_terms) == sorted(other.btype_terms))

    def __repr__(self):
        return "CircularFPType(version=%r, size=%d, minradius=%d, maxradius=%d, atype_terms=%r, btype_terms=%r)" % (
            self.version, self.size, self.minradius, self.maxradius, self.atype_terms, self.btype_terms)
        
    def to_oetype(self):
        return "Circular,ver=%s,size=%d,radius=%d-%d,atype=%s,btype=%s" % (
            self.version, self.size, self.minradius, self.maxradius,
            _oe_atype(self.atype_terms), _oe_btype(self.btype_terms))

    def to_chemfp_type(self):
        if self.version == "2.0.0":
            t = "OpenEye-Circular/2"
        else:
            t = "OpenEye-Circular/" + self.version
            
        t += " numbits=%d minradius=%d maxradius=%d" % (self.size, self.minradius, self.maxradius)

        t += " atype=" + _chemfp_atype(self.atype_terms)
        t += " btype=" + _chemfp_atype(self.btype_terms)
        return t

def _parse_oe_circular(oetype, kv_pairs):
    _check_keys(kv_pairs, ("ver", "size", "radius", "atype", "btype"), oetype)

    version = kv_pairs[0][1]
    size = _check_size(kv_pairs[1], oetype)
    min, max = _check_range(kv_pairs[2], oetype)
    atype_terms = _check_atype(kv_pairs[3], oetype)
    btype_terms = _check_btype(kv_pairs[4], oetype)

    return CircularFPType(version, size, min, max, atype_terms, btype_terms)

def _parse_chemfp_circular(chemfp_type, tokenized_type):
    tt = tokenized_type
    if tt.version == "2":
        version = "2.0.0"
    else:
        version = tt.version

    d = _check_settings(chemfp_type, tokenized_type,
                        ("numbits", "minradius", "maxradius", "atype", "btype"))
    return CircularFPType(version=version, **d)



# Tree,ver=2.0.0,size=4096,bonds=0-4,atype=AtmNum|Arom|Chiral|FCharge|HvyDeg|Hyb,btype=Order
# OpenEye-Tree/2 numbits=4096 minbonds=0 maxbonds=4 atype=Arom|AtmNum|Chiral|FCharge|HvyDeg|Hyb btype=Order

class TreeFPType(BaseOEFPType):
    def __init__(self, version, size, minbonds, maxbonds, atype_terms, btype_terms):
        self.version = version
        self.size = size
        self.minbonds = minbonds
        self.maxbonds = maxbonds
        self.atype_terms = atype_terms
        self.btype_terms = btype_terms

    def __eq__(self, other):
        return (isinstance(other, TreeFPType)
                and self.version == other.version
                and self.size == other.size
                and self.minbonds == other.minbonds
                and self.maxbonds == other.maxbonds
                and sorted(self.atype_terms) == sorted(other.atype_terms)
                and sorted(self.btype_terms) == sorted(other.btype_terms))
    
    def __repr__(self):
        return "TreeFPType(version=%r, size=%d, minbonds=%d, maxbonds=%d, atype_terms=%r, btype_terms=%r)" % (
            self.version, self.size, self.minbonds, self.maxbonds, self.atype_terms, self.btype_terms)
        
    def to_oetype(self):
        return "Tree,ver=%s,size=%d,bonds=%d-%d,atype=%s,btype=%s" % (
            self.version, self.size, self.minbonds, self.maxbonds,
            _oe_atype(self.atype_terms), _oe_btype(self.btype_terms))

    def to_chemfp_type(self):
        if self.version == "2.0.0":
            t = "OpenEye-Tree/2"
        else:
            t = "OpenEye-Tree/" + self.version
            
        t += " numbits=%d minbonds=%d maxbonds=%d" % (self.size, self.minbonds, self.maxbonds)

        t += " atype=" + _chemfp_atype(self.atype_terms)
        t += " btype=" + _chemfp_btype(self.btype_terms)
        return t

def _parse_oe_tree(oetype, kv_pairs):
    _check_keys(kv_pairs, ("ver", "size", "bonds", "atype", "btype"), oetype)

    version = kv_pairs[0][1]
    size = _check_size(kv_pairs[1], oetype)
    min, max = _check_range(kv_pairs[2], oetype)
    atype_terms = _check_atype(kv_pairs[3], oetype)
    btype_terms = _check_btype(kv_pairs[4], oetype)

    return TreeFPType(version, size, min, max, atype_terms, btype_terms)

def _parse_chemfp_tree(chemfp_type, tokenized_type):
    tt = tokenized_type
    if tt.version == "2":
        version = "2.0.0"
    else:
        version = tt.version

    d = _check_settings(chemfp_type, tokenized_type,
                        ("numbits", "minbonds", "maxbonds", "atype", "btype"))
    return TreeFPType(version=version, **d)

# MACCS,ver=2.0.0
# OpenEye-MACCS166/3

class MACCS166FPType(BaseOEFPType):
    def __init__(self, version):
        self.version = version

    def __eq__(self, other):
        return (isinstance(other, MACCS166FPType)
                and self.version == other.version)
    
        
    def __repr__(self):
        return "MACCS166FPType(version=%r)" % (self.version,)
        
    def to_oetype(self):
        return "MACCS166,ver=%s" % (self.version,)
    
    def to_chemfp_type(self):
        if self.version == "2.2.0":
            t = "OpenEye-MACCS166/3"
        else:
            t = "OpenEye-MACCS166/" + self.version

        return t

def _parse_oe_maccs166(oetype, kv_pairs):
    _check_keys(kv_pairs, ("ver",), oetype)

    version = kv_pairs[0][1]
    return MACCS166FPType(version)

def _parse_chemfp_maccs166(chemfp_type, tokenized_type):
    tt = tokenized_type
    if tt.settings:
        raise ValueError("OpenEye-MACCS166 type takes no parameters: %r" % (chemfp_type,))
    if tt.version == "3":
        return MACCS166FPType("2.2.0")
    elif tt.version == "2":
        return MACCS166FPType("2.0.0")
    else:
        return MACCS166FPType(tt.version)

##


_oetype_handlers = {
    "Path": _parse_oe_path,
    "Tree": _parse_oe_tree,
    "Circular": _parse_oe_circular,
    "MACCS166": _parse_oe_maccs166,
    }
    
def parse_oetype_string(oetype):
    terms = oetype.split(",")
    if not terms:
        raise ValueError("Empty oetype")
    
    kv_pairs = []
    for term in terms[1:]:
        k, sep, v = term.partition("=")
        if not k or not sep or not v:
            raise ValueError("invalid term %r in oetype %r" % (term, oetype))
        kv_pairs.append( (k, v) )

    handler = _oetype_handlers.get(terms[0], None)
    if handler is None:
        raise ValueError("unable to parse OEGraphSim fingerprint type %r" % (terms[0],))
    
    return handler(oetype, kv_pairs)

_chemfp_type_handlers = {
    "OpenEye-Path": _parse_chemfp_path,
    "OpenEye-Tree": _parse_chemfp_tree,
    "OpenEye-Circular": _parse_chemfp_circular,
    "OpenEye-MACCS166": _parse_chemfp_maccs166,
    }

## From chemfp 3.1

_name_pat = re.compile(r"([!-.0-~]+)(/([!-.0-~]+))?$")

_not_allowed_char_pat = re.compile(r"[^!-.0-~]")
def _contains_special_characters(name):
    return _not_allowed_char_pat.search(name) is not None


def _verify_name(name):
    "Verify that the type string name is correct"
    # Quick check to see if it's in the right form.
    m = _name_pat.match(name)
    if m is not None:
        return m.group(1), m.group(3)

    # Something went wrong. Let's see if I can give a better report.
    if not name:
        raise ValueError("Unable to use an empty fingerprint type name")
    if not name.strip():
        raise ValueError("Unable to use a blank fingerprint type name: %r" % (name,))

    n = name.count("/")
    if n == 0:
        if _contains_special_characters(name):
            raise ValueError("Fingerprint type name contains an unexpected character: %r" % (name,))
        return name, None
    if n == 1:
        base_name, version = name.split("/")

        if not base_name:
            raise ValueError("Missing fingerprint type name before the first '/': %r" % (name,))
        if _contains_special_characters(base_name):
            raise ValueError("Fingerprint type name contains an unexpected character: %r" % (name,))

        if not version:
            raise ValueError("Missing version after the first '/' of the fingerprint type: %r" % (name,))
        if _contains_special_characters(version):
            raise ValueError("Fingerprint type version contains an unexpected character: %r" % (name,))

        return base_name, version
class TokenizedType(object):
    """A tokenized type string

    `name` is the type name, which may or may not have a version
    string. `base_name` is the type name without the version,
    and `version` is the version component, or None if there is
    no version.

    `settings` is a list of argument pairs as the 2-element
    tuple (argument name, argument value), where both the name
    and value are strings.
    """

    def __init__(self, base_name, version, settings):
        self.base_name = base_name
        self.version = version
        if version is None:
            self.name = base_name
        else:
            self.name = base_name + "/" + version
        self.settings = settings

def tokenize_type_string(type):
    """Convert a type string into a TokenizedType instance

    This is most easily understood as an example.

    >>> tokens = tokenize_type_string("ABC/123 a=1 b=xyz")
    >>> tokens.name, tokens.base_name, tokens.version
    ('ABC/123', 'ABC', '123')
    >>> tokens.settings
    [('a', '1'), ('b', 'xyz')]
    """
    base_name, version, settings = _split_type_string(type)

    # It starts off correct. Now parse the name/value settings.

    seen = set()
    tokens = []

    for term in settings:
        try:
            left, right = term.split("=")
        except ValueError:
            raise ValueError("Term %r in type %r must have one and only one '='" %
                             (term, type))
        if left in seen:
            raise ValueError("Duplicate parameter %r in type %r" % (left, type))

        seen.add(left)
        tokens.append( (left, right) )

    return TokenizedType(base_name, version, tokens)

def _split_type_string(type):
    """Break up a type string into its (base name, version, settings)"""
    if not type:
        if type is None:
            raise ValueError("Must specify a fingerprint type string")
        raise ValueError("Unable to use an empty fingerprint type")
    if type.isspace():
        raise ValueError("Empty fingerprint type (%r)" % (type,))
    if type[:1].isspace():
        raise ValueError("Fingerprint type must not begin with whitespace: %r" % (type,))

    terms = type.split()
    if not terms:
        raise AssertionError("Unexpected empty fingerprint type (%r)" % (type,))

    name = terms[0]
    base_name, version = _verify_name(name)
    return base_name, version, terms[1:]


##

def parse_chemfp_type_string(chemfp_type):
    tokenized_type = tokenize_type_string(chemfp_type)
    base_name = tokenized_type.base_name
    handler  = _chemfp_type_handlers.get(base_name, None)
    if handler is None:
        raise ValueError("Unable to convert %r to an OEGraphSim type" % (base_name,))

    return handler(chemfp_type, tokenized_type)

if __name__ == "__main__":
    s = "OpenEye-Tree/2 numbits=4096 minbonds=0 maxbonds=4 atype=Arom|AtmNum|Chiral|FCharge|HvyDeg|Hyb btype=Order"
    #s = "OpenEye-Circular/2 numbits=4096 minradius=0 maxradius=5 atype=Arom|AtmNum|Chiral|EqHalo|FCharge|HCount btype=Order"
    #s = "OpenEye-Path/2 numbits=4096 minbonds=0 maxbonds=5 atype=Arom|AtmNum|Chiral|EqHalo|FCharge|HvyDeg|Hyb btype=Order|Chiral"
    #s = "OpenEye-MACCS166/3"
    
    obj = parse_chemfp_type_string(s)
    print("s:", s)
    t = obj.to_chemfp_type()
    print("t:", t)
    assert s == t
    print(obj.to_oetype())
