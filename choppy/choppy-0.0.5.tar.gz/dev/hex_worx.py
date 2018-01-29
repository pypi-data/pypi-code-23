#! usr/bin/env/ python3

import struct

# ------------------------------------------------------------------------------
cat = ''.join



def fmt_hex(n):
    hx = '{:x}'.format(n)
    if len(hx) % 2:
        hx = hx.zfill(len(hx) + 1)
    return hx

# >>> ---------------------------------------- >>>
# struct.pack('>H', 26).hex()
def hex_16bit(n):
    return '{:0>4x}'.format(n)

def hex16(n):
    return struct.pack('>H', n)

# >>> ----------------------------------------

def hex_byte_read_len(hx):
    return hex_16bit(len(hx) // 2)


# bytes(s, 'utf-8')
def encode_str_hex(word):
    hex_vals = []
    for char in word:
        hex_vals.append(fmt_hex(ord(char)))
    return cat(hex_vals)


# bx.decode('utf-8')
def decode_hex_str(hx):
    hex_str = []
    for chars in map(cat, zip(hx[::2], hx[1::2])):
        hex_str.append(chr(int(chars, 16)))
    return cat(hex_str)

HEX_FP = encode_str_hex('ch0ppyFP')

# ------------------------------------------------------------------------------

# n = struct.pack('>H', 26)

def test_convert(s):
    bx = bytearray(s, 'utf-8')
    bx.insert(0, len(bx))
    return bx


# def bxcat(*args):

def bcat(*args):
    bx = chain.from_iterable(args)
    return bytearray(bx)

# HEX_FP = bytes('ch0ppyFP', 'utf-8')


x16 = struct.Struct('>H')
x64 = struct.Struct('>Q')

def encode_uint16(n):
    return x16.pack(n)

def encode_uint64(n):
    return x64.pack(n)


""" --> v01
[fingerprint][group id hash][index][index total]
[read next][byte len of partition]
[read next][encoded filename]
[read next][file hash]
"""


""" --> v02

[fingerprint][group id hash][index total] || [rd][encoded filename][rd][file hash]
16, 16, 2 || 2, rd, 2, rd


[ix] || [rd][byte len of partition]
2 || 2, rd

"""

x = 1234
n1 = X16.pack(x).hex()
n2 = B16.pack(x).hex()


def cnb(n):

    if n.bit_length() <= 64:
        nbx = encode_uint64(n)
    else:
        nbx = encode_uint(n)

    return byte_len(nbx), nbx
