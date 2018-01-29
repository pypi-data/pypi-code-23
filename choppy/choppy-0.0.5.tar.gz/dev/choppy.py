#! usr/bin/env/ python3

from collections import defaultdict
import hashlib
from itertools import chain, count
from operator import itemgetter
import os
import tempfile
from time import perf_counter
# ------------------------------------------------------------------------------

cat = ''.join

# HEX UTILS --------------------------------------------------------------------
def fmt_hex(n):
    hx = '{:x}'.format(n)
    if len(hx) % 2:
        hx = hx.zfill(len(hx) + 1)
    return hx


def hex_16bit(n):
    return '{:0>4x}'.format(n)


def hex_byte_read_len(hx):
    return hex_16bit(len(hx) // 2)


def encode_str_hex(word):
    hex_vals = []
    for char in word:
        hex_vals.append(fmt_hex(ord(char)))
    return cat(hex_vals)


def decode_hex_str(hx):
    hex_str = []
    for chars in map(cat, zip(hx[::2], hx[1::2])):
        hex_str.append(chr(int(chars, 16)))
    return cat(hex_str)


# ------------------------------------------------------------------------------
def md5_hash(fp):
    chunk = 2**12
    f_hash = hashlib.md5()
    with open(fp, 'rb') as file_:
        data = file_.read(chunk)
        while data:
            f_hash.update(data)
            data = file_.read(chunk)

    return f_hash.hexdigest()


def file_info(fp):
    return os.path.getsize(fp), md5_hash(fp)


# ------------------------------------------------------------------------------
def calculate_byte_lengths(n_bytes, partitions):
    chunk_size = n_bytes // partitions
    byte_reads = [chunk_size] * partitions
    for ix in range(n_bytes % partitions):
        byte_reads[ix] += 1
    return tuple(byte_reads)


def convert_filename(fp):
    fn_hex = encode_str_hex(os.path.basename(fp))
    return hex_byte_read_len(fn_hex), fn_hex


def convert_hash(fp, hash_func=md5_hash):
    fn_hash = hash_func(fp)
    return hex_byte_read_len(fn_hash), fn_hash


def convert_nbytes(n):
    nhex = fmt_hex(n)
    return hex_byte_read_len(nhex), nhex


# ------------------------------------------------------------------------------
def partition_file(fp, tmpdir, partitions):

    byte_reads = calculate_byte_lengths(os.path.getsize(fp), partitions)
    id_tot = hex_16bit(partitions)
    fmap_end = cat(chain(convert_filename(fp), convert_hash(fp)))

    def metabytes(idx, nbytes):
        ix = hex_16bit(idx)
        nb_rd, nb_hex = convert_nbytes(nbytes)
        return bytes.fromhex(cat((ix, id_tot, nb_rd, nb_hex, fmap_end)))

    with open(fp, 'rb') as file_:
        for ix, nbytes in enumerate(byte_reads):
            fp_ix = os.path.join(tmpdir.name, str(ix))
            with open(fp_ix, 'wb') as file_ix:
                file_ix.write(metabytes(ix, nbytes))
                file_ix.write(file_.read(nbytes))
                yield file_ix.name


# ------------------------------------------------------------------------------
# def read_int(file_, n=2):
#     return int(file_.read(n).hex(), 16)


# ------------------------------------------------------------------------------
def read_int(file_, r=2):
    try:
        n = int(file_.read(r).hex(), 16)
    except ValueError:
        n = 0
    return n


def merge_file(meta_paths, fn):
    with open(fn, 'wb') as outfile:
        for _, seek, nbytes, fp in meta_paths:
            with open(fp, 'rb') as file_ix:
                file_ix.seek(seek)
                outfile.write(file_ix.read(nbytes))


def load_paths(paths):

    metadata = defaultdict(list)

    for fp in paths:
        with open(fp, 'rb') as file_ix:
            seek = 4
            ix = read_int(file_ix)
            tot = read_int(file_ix)

            read_next = read_int(file_ix)
            nbytes = int(file_ix.read(read_next).hex(), 16)
            seek += read_next + 2

            read_next = read_int(file_ix)
            filename = file_ix.read(read_next).hex()
            seek += read_next + 2

            read_next = read_int(file_ix)
            filehash = file_ix.read(read_next).hex()
            seek += read_next + 2

            metadata[(tot, filename, filehash)].append((ix, seek, nbytes, fp))

    return metadata


def verify_paths(paths):
    get_ix = itemgetter(0)
    metadata = load_paths(paths)

    valid_keys = (k for k, v in metadata.items() if k[0] == len(v))

    for key in valid_keys:
        tot, filename, filehash = key
        vals = metadata[key]
        if sorted(map(get_ix, vals)) == [i for i in range(tot)]:
            vals.sort(key=get_ix)
            filename = decode_hex_str(filename)
            yield filename, filehash, vals


def recombine(paths):
    for filename, filehash, valid_paths in verify_paths(paths):
        merge_file(valid_paths, filename)
        if md5_hash(filename) == filehash:
            print('File contents verified for:', filename)
        else:
            print('File contents unverified:', filename, filehash)


# ------------------------------------------------------------------------------
def test_chop(fn, fnout, n=10):
    start = perf_counter()

    tmpdir = tempfile.TemporaryDirectory()

    paths = tuple(partition_file(fn, tmpdir, n))
    print('File partitioned:', len(paths))

    tracker = merge_file(paths, fnout)
    print('Files merged')

    check = file_info(fn) == file_info(fnout)
    print('Status:', check)

    tmpdir.cleanup()

    print('{:.4f} sec'.format(perf_counter() - start))
    return tracker
