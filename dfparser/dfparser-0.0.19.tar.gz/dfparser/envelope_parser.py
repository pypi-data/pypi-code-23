"""Dataforge envelope format parser utils."""

import io
import json
import re
import struct
import time
import zlib

from df_data.type_codes import ENVELOPE_HEADER_CODES as CODES

HEADER_RE = re.compile(b"(#~DF02.{10}~#|#!.{24}!#)", re.DOTALL)


def create_message(
        json_meta, data, data_type=0, version=b'\x00\x01@\x00'):
    """Create message, containing meta and data in df-envelope format.

    @json_meta - metadata
    @data - binary data
    @data_type - data type code for binary data
    @version - version of machine header
    @return - message as bytearray

    """
    __check_data(data)
    meta = __prepare_meta(json_meta)
    data = __compress(json_meta, data)
    header = __create_machine_header(
        json_meta, data, data_type, version)

    return header + meta + data


def parse_from_file(filename, nodata=False):
    """Parse df message from file.

    @filename - path to file
    @nodata - do not load data
    @return - [binary header, metadata, binary data]

    """
    header = None
    with open(filename, "rb") as file:
        header = read_machine_header(file)
        meta_raw = file.read(header['meta_len'])
        meta = __parse_meta(meta_raw, header)
        data = b''
        if not nodata:
            data = __decompress(meta, file.read(header['data_len']))

        return header, meta, data


def parse_message(message, nodata=False):
    """Parse df message from bytearray.

    @message - message data
    @nodata - do not load data
    @return - [binary header, metadata, binary data]

    """
    header = read_machine_header(message)
    h_len = __get_machine_header_length(header)
    meta_raw = message[h_len:h_len + header['meta_len']]
    meta = __parse_meta(meta_raw, header)
    data_start = h_len + header['meta_len']
    data = b''
    if not nodata:
        data = __decompress(
            meta,
            message[data_start:data_start + header['data_len']]
        )
    return header, meta, data


def read_machine_header(data):
    """Parse binary header.

    @data - bytearray, contains binary header of file opened in 'rb' mode
    @return - parsed binary header

    """
    if isinstance(data, (bytes, bytearray)):
        stream = io.BytesIO(data)
    elif isinstance(data, io.BufferedReader):
        stream = data
    else:
        raise ValueError("data should be either bytearray or file 'rb' mode.")

    header = dict()
    header_type = stream.read(6)
    if header_type == b"#!\x00\x01@\x00":
        header['type'] = header_type[2:6]
        header['time'] = struct.unpack('>I', stream.read(4))[0]
        header['meta_type'] = struct.unpack('>I', stream.read(4))[0]
        header['meta_len'] = struct.unpack('>I', stream.read(4))[0]
        header['data_type'] = struct.unpack('>I', stream.read(4))[0]
        header['data_len'] = struct.unpack('>I', stream.read(4))[0]
        stream.read(4)
    elif header_type == b"#~DF02":
        header['type'] = header_type[2:6]
        header['meta_type'] = stream.read(2)
        header['meta_len'] = struct.unpack('>I', stream.read(4))[0]
        header['data_len'] = struct.unpack('>I', stream.read(4))[0]
        stream.read(4)
    else:
        raise NotImplementedError(
            "Parser for machine header %s not implemented" %
            (header_type.decode()))

    return header


def get_messages_from_stream(data):
    """Extract complete messages from stream and cut out them from stream.

    @data - stream binary data
    @return - [list of messages, choped stream data]

    """
    messages = []
    iterator = HEADER_RE.finditer(data)
    last_pos = 0
    for match in iterator:
        pos = match.span()[0]
        header = read_machine_header(data[pos:])
        h_len = __get_machine_header_length(header)
        cur_last_pos = pos + h_len + header['meta_len'] + header['data_len']

        if cur_last_pos > len(data):
            break

        header, meta, bin_data = parse_message(data[pos:])
        messages.append({'header': header, 'meta': meta, 'data': bin_data})

        last_pos = cur_last_pos

    data = data[last_pos:]
    return messages, data


def __decompress(meta, data):
    if "compression" in meta:
        if meta["compression"] == "zlib":
            return zlib.decompress(data)
        else:
            raise NotImplementedError(
                "Only zlib compression supported"
            )
    return data


def __compress(meta, data):
    if "compression" in meta:
        if meta["compression"] == "zlib":
            return zlib.compress(data)
        else:
            raise NotImplementedError(
                "Only zlib compression supported"
            )
    return data


def __parse_meta(meta_raw, header):
    if header["type"] == b'\x00\x01@\x00':
        if header["meta_type"] == \
                CODES[header["type"]]["meta_types"]["JSON_METATYPE"]:
            return json.loads(meta_raw.decode())
        else:
            raise NotImplementedError("Meta type %s not implemented" %
                                      bin(header["meta_type"]))
    if header["type"] == b"DF02":
        if header["meta_type"] == \
                CODES[header["type"]]["meta_types"]["JSON_METATYPE"]:
            return json.loads(meta_raw.decode())
        else:
            raise NotImplementedError("Meta type %s not implemented." %
                                      (header["meta_type"]))
    else:
        raise NotImplementedError("Machine header %s not implemented" %
                                  header["type"])


def __prepare_meta(json_meta):
    if isinstance(json_meta, dict):
        json_meta = json.dumps(json_meta, indent=4).encode()
        json_meta += b'\r\n\r\n'
    elif not isinstance(json_meta, str):
        raise ValueError("Input meta should be dict or str")
    return json_meta


def __check_data(data):
    if not isinstance(data, bytes):
        raise ValueError("Input data should have bytes type")


def __create_machine_header(json_meta, data, data_type, version):
    json_meta = __prepare_meta(json_meta)
    __check_data(data)

    if version == b'\x00\x01@\x00':
        binary_header = b'#!'
        # binary header type
        binary_header += version
        millis = int(round(time.time() * 1000))
        # current time
        binary_header += struct.pack('>Q', millis)[4:]
        # meta type
        binary_header += struct.pack(
            '>I', CODES[version]["meta_types"]["JSON_METATYPE"])
        # meta length
        binary_header += struct.pack('>I', len(json_meta))
        # data type
        binary_header += struct.pack('>I', data_type)
        # data length
        binary_header += struct.pack('>I', len(data))

        binary_header += b'!#\r\n'

        return binary_header

    elif version == b"DF02":
        return b'#~%s%s%s%s~#\r\n' % (
            version,
            CODES[version]["meta_types"]["JSON_METATYPE"],
            struct.pack('>I', len(json_meta)), struct.pack('>I', len(data)))
    else:
        raise NotImplementedError(
            "Machine header %s not implemented" % version)


def __get_machine_header_length(header):
    return CODES[header["type"]]["header_len"]
