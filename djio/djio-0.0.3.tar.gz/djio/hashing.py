#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. currentmodule:: djio.hashing
.. moduleauthor:: Pat Daburu <pat@daburu.net>

Need to know at a glance if two geometries are the same?
"""

import math
from typing import Iterable, Tuple


def int_to_bytes(i: int,
                 width: int,
                 unsigned: bool=False,
                 as_iterable: bool=False) -> bytearray or Iterable[int]:
    """
    Convert an integer to a fixed-width byte array.

    :param i: the integer
    :param width: the number of bytes in the array
    :param unsigned: `True` if the sign of the `int` may be disregarded, otherwise `False`
    :param as_iterable: when `True` the function returns a list of byte-sized `int`s instead of a `bytearray`.
    :return: the byte array
    """
    # We'll start by working with the absolute value and sort out negatives later.
    _i = i if (unsigned or i >=0) else int(math.fabs(i))
    # Create a list to hold the bite-sized integers (bsi) as we create them.
    bsis = [0] * width
    # We'll use a mask that spans eight bits (one [1] byte) which we'll shift in order to get only the bits in a given
    # byte's position.
    mask = 255
    # Let's get started...
    for idx in range(0, width):
        # We want the larger parts of the number to be "on the left", that is to say, in the lower orders of the
        # bsis array.  So as we go through this loop, the position to which we shift the mask will gradually move
        # from "left" (the higher-order bits) to "right" (the lower-order bits).
        shift = width - idx - 1
        # Shift the mask.
        _mask = mask << (shift * 8)
        # The value that goes into the
        bsis[idx] = (_i & _mask) >> (shift * 8)
    # Unless the caller indicated we don't need to worry about the sign, we have a little more work to do...
    if not unsigned:
        # If the original integer (i) was negative we'll flip on the highest-order bit (of the highest-order byte, which
        # is to say the one at index 0), otherwise we'll flip it off.
        bsis[0] = bsis[0] & 127 if i >= 0 else bsis[0] | 128
    # Return what we got.
    return bsis if as_iterable else bytes(bsis)


def bytes_to_int(b: bytes):
    """
    Convert a byte array to an integer.

    :param b: the byte array
    :return: the integer
    """
    neg = False  # Have we determined the value to be negative?  We'll see.
    i=0  # This is the variable in which we'll store the value.
    # Now we need to do some tap dancing to handle negative integers...
    # We can't directly modify the original bytearray, so let's create a new variable to reference it.
    _bytes = b
    # If we discover that the highest-order bit in the higest-order byte (which should be at index 0) is flipped on...
    if _bytes[0] >= 128:
        # ...we need to create a new list of bite-sized integers.
        _bytes = list(b)
        # Now we flip the higest-order bit off so processing below can continue without worrying about negatives...
        _bytes[0] = _bytes[0] & 127
        # ...but we'll make note that the final result *is* negative.
        neg = True
    # Now we need to know how many bytes (or byte-sized ints) we're dealing with.
    width = len(_bytes)
    # Let's go through them all, starting with the highest-order byte.
    for idx in range(0, width):
        # Since the higest-order bytes are in the lower indexes, we'll bit shift each value *fewer* positions to the
        # left as we move from lower index values to higher index values.
        i_at_idx = _bytes[idx] << (width - idx - 1) * 8  # (Shift it 8 bits, or 1 byte.)
        # Now we can just add it!
        i = i + i_at_idx
    # Return the number we have (or its negative twin).
    return i if not neg else i * -1


def djiohash_v1(geometry_type_code: int,
                srid: int,
                coordinates: Iterable[Tuple[float, float] or Tuple[float, float, float]],
                precision: int = 4) -> bytearray:
    """
    This is the first version of the djio hashing algorithm.
    :param geometry_type_code: an integer indicating the type of the geometry
    :param srid: the numeric spatial reference ID
    :param coordinates: a flattened, ordered iteration of coordinates in the geometry expressed as tuples
    :param precision: the maximum precision (points behind decimal places) to consider in the supplied coordinates
    :return: a hash value for the geometry

    .. sealso::

        :py:class:`djio.geometry.GeometryType`
    """
    # The first byte will hold the geometry type in the highest 4 bits of the first byte.
    # ☐☐☐☐0000
    b1_geometry_type = geometry_type_code << 4
    # The next bit tells us whether or not the geometry is a collection.
    # 0000☐000
    b1_is_collection = 0 << 3  # TODO: Revisit this when collections are implemented.
    # The next bit tells us whether or not this geometry has 3D coordinates (i.e. "M" values).
    # 00000☐00
    b1_has_m_values = 0 << 2  # TODO: Revisit this when we can determine this.
    # The last two bits in this byte are presently available.
    # 000000☐☐ <-- These are available.
    b1 = b1_geometry_type | b1_is_collection | b1_has_m_values

    # Bytes 2-4 contain the SRID.
    b2_4 = int_to_bytes(srid, width=3, as_iterable=True)

    # Bytes 5-7 contains the total number of vertices.  However, we won't know it until we complete the iteration.

    max_bits = 64  # the maximum number of bits in the coordinate hash TODO: This is a magic constant.
    mask = int(math.pow(2, max_bits)) - 1  # a mask that covers all the bits
    coords_bits = 0  # This is the value we're doing all this bit blasting against.
    # Let's go!
    coordinates_count = 0  # We'll keep the count as we iterate.
    offset = 0  # With each iteration we'll shift to the left by this offset, then increment it.
    for coord in coordinates:
        for ord in coord:
            # Pull everything from the fractional part of the floating-point number into the whole part.
            ordi = int(ord * math.pow(10, precision)) # if ord < 0 else ~(int(ord * math.pow(10, precision)))
            # Rotate the integer value by the offset:
            # Shift the number bitwise by the offset.  (Some of the bits will move beyond the high-order part of
            # the mask, as you'll see, we rotate them to the lower bits.)
            ordi_shift = ordi << offset
            # ordi_hi is the part of the number that rotates beyond the high order bits of the mask.
            ordi_hi = ordi >> max_bits - offset
            # Recombine the bits we shifted to the left with those that "rotated around" to end up on the right.
            ordi_rot = ordi_shift | ordi_hi
            # Apply an XOR
            coords_bits ^= ordi_rot
            # Increment (or reset) the offset.
            offset = offset + 1 if offset < max_bits else 0
            # We're keeping track of the total number of coordinates.
            coordinates_count += 1

    coords_bits = ~(coords_bits & mask)

    # Now we convert the bits to a series of byte-sized ints (bsi).
    coords_bsis = int_to_bytes(coords_bits, width=int(max_bits/8), unsigned=True, as_iterable=True)

    # We can now establish the contents of bytes 5-7 since we know the total number of verticies.
    b5_7 = int_to_bytes(coordinates_count, width=3, as_iterable=True) # TODO: We could cut this down to 2 if we forbid vertex counts over 65536 or if we allow collisions here.

    # Put all the byte-sized ints together into one big list.
    all_bsis = [b1] + b2_4 + b5_7 + coords_bsis

    # Convert our accumulated list of byte-sized ints into a single byte array.
    bytes = bytearray(all_bsis)
    # Whew.
    return bytearray(bytes)






