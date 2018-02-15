from array import array
from collections import namedtuple
from sys import byteorder
from typing import Dict, Iterable, NamedTuple, Optional
import struct


class DataFormatError(ValueError):
    """Exception raised for format errors in binary data.
    """


def _binary_data_blocks(data: bytes) -> NamedTuple:
    """Generator function for the 'Scope, Lock, and Recorder Binary Data'
    format of the DLC pro that can be used to iterate over the contained
    blocks.

    Args:
        data: Input data to iterate over.

    Returns:
        A namedtuple with the following elements:
        'id': block id letter
        'payload': A memoryview with the block payload.
    """
    DataBlock = namedtuple('DataBlock', ['id', 'payload'])

    i = 0
    while i < len(data):
        # Block start, read block id
        blockid = data[i:i+1].decode()

        # Get payload length from zero terminated ASCII string following the
        # block id.
        try:
            header_terminator_index = data.index(0, i+1)
        except ValueError as exc:
            raise DataFormatError("Block header terminator not found in block '{}'".format(blockid)) from exc

        try:
            payload_len = int(data[i+1:header_terminator_index])
        except ValueError as exc:
            raise DataFormatError("Payload length incorrect in block '{}'".format(blockid)) from exc

        # Create payload view
        payload_start_index = header_terminator_index + 1

        if payload_start_index + payload_len > len(data):
            raise DataFormatError("Wrong payload size given in header of block '{}'".format(blockid))

        payload = memoryview(data)[payload_start_index:payload_start_index + payload_len]

        i = payload_start_index + payload_len

        yield DataBlock(blockid, payload)


def _letoh(raw: array) -> array:
    """Converts the endianess of an array from little endian to host byte order.

    Args:
        raw: Instance of array with elements in little endian byte order.

    Returns:
        Instance of array with elements in host byte order.
    """
    if byteorder != 'little':
        raw.byteswap()

    return raw


def extract_float_arrays(blockids: str, data: bytes) -> Dict[str, array]:
    """Extracts float arrays from raw scope, background trace, and recorder
    zoom binary data (block ids a, A, b, B, x, y, Y in the DLC pro 'Scope,
    Lock, and Recorder Binary Data' format).

    Args:
        blockids: String of requested block id letters. Block ids not
        available in the input data or in the above list are ignored.
        data: Input byte sequence.

    Returns:
        Dictionary with found block ids as keys and arrays of floats
        (typecode 'f') as values.

    Raises:
        DataFormatError: If the contents of `data` are not conform to the
        'Scope, Lock, and Recorder Binary Data' format.
    """
    retval = {}

    for block in _binary_data_blocks(data):
        if block.id in blockids and block.id in 'aAbBxyY':
            values = array('f')  # float (IEEE 754 single precision)

            try:
                values.frombytes(block.payload)
            except ValueError as exc:
                raise DataFormatError("Invalid payload length in block '{}'".format(block.id)) from exc

            retval[block.id] = _letoh(values)

    return retval


def extract_lock_points(blockids: str, data: bytes) -> Dict[str, Dict[str, Iterable]]:
    """Extracts lock points from raw lock point data (block ids l, c, t in the
    DLC pro 'Scope, Lock, and Recorder Binary Data' format).

    Args:
        blockids: String of requested block id letters. Block ids not
        available in the input data or in the above list are ignored.
        data: Input byte sequence.

    Returns:
        Dictionary with found block ids as keys with nested dicts as
        values. The nested dicts contain the keys x, y, t and lists of the
        respective field contents as values (float for keys x,y, str for key t).

    Raises:
        DataFormatError: If the contents of `data` are not conform to the
        'Scope, Lock, and Recorder Binary Data' format.
    """
    retval = {}

    for block in _binary_data_blocks(data):
        if block.id in blockids and block.id in 'clt':
            s = struct.Struct('<2f1c')

            try:
                retval[block.id] = dict([
                    ('x', list(i[0] for i in s.iter_unpack(block.payload))),
                    ('y', list(i[1] for i in s.iter_unpack(block.payload))),
                    ('t', ''.join(i[2].decode() for i in s.iter_unpack(block.payload)))
                ])
            except struct.error as exc:
                raise DataFormatError("Invalid payload format in block '{}'".format(block.id)) from exc

    return retval


def extract_lock_state(data: bytes) -> Optional[int]:
    """Extracts the state of the locking module from raw lock point data (block
    id s in the DLC pro 'Scope, Lock, and Recorder Binary Data' format).

    Args:
        data: Input byte sequence.

    Returns:
        Lock module's state as integer if available, otherwise None.

    Raises:
        DataFormatError: If the contents of `data` are not conform to the
        'Scope, Lock, and Recorder Binary Data' format.
    """
    for block in _binary_data_blocks(data):
        if block.id in 's':
            if len(block.payload) != 1:
                raise DataFormatError("Payload length incorrect in block '{}'".format(block.id))

            return block.payload[0]

    return None
