import base64
import os.path
import shutil
import struct

from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Hash import SHA256


def get_md5(input):
    import hashlib
    md5 = hashlib.md5()
    md5.update(input.encode('utf-8'))
    return md5.hexdigest()


def get_name(file_path):
    filename_len = 0
    with open(file_path, mode='rb') as f:
        old = f.read(4)
        filename_len, _ = struct.unpack('HH', old)
        filename = base64.standard_b64decode(f.read(filename_len)).decode()

        print(filename)


def encrypt(key, source, encode=True):
    key = SHA256.new(key).digest()
    IV = Random.new().read(AES.block_size)
    encryptor = AES.new(key, AES.MODE_CBC, IV)
    padding = AES.block_size - len(source) % AES.block_size
    source += bytes([padding]) * padding
    data = IV + encryptor.encrypt(source)
    return base64.b64encode(data) if encode else data


def decrypt(key, source, decode=True):
    if decode:
        source = base64.b64decode(source)

    key = SHA256.new(key).digest()
    IV = source[:AES.block_size]
    encryptor = AES.new(key, AES.MODE_CBC, IV)
    data = encryptor.decrypt(source[AES.block_size:])
    padding = data[-1]
    if data[-padding:] != bytes([padding]) * padding:
        raise ValueError('Invalid padding ...')
    return data[:-padding]


def encode(file_path):
    filename = os.path.basename(file_path)
    new_filename = get_md5(filename)
    key = new_filename.encode('utf-8')

    dfilename = encrypt(key, filename.encode('utf-8'))
    lfilename = len(dfilename)
    print(lfilename)

    print(decrypt(new_filename.encode('utf-8'), dfilename))
    shutil.copy(file_path, new_filename)

    bdata = None
    bdata_len = 0
    with open(file_path, mode='rb') as f:
        data = f.read(100)
        bdata = encrypt(key, data)
        bdata_len = len(bdata)
        print(bdata_len)

    head = struct.pack('HH', lfilename, bdata_len)

    with open(new_filename, mode='rb+') as f:
        f.seek(100)
        old = f.read()
        f.seek(0)
        f.write(head)
        f.write(dfilename)
        f.write(bdata)
        f.write(old)


def decode(file_path):
    filename = os.path.basename(file_path)
    key = filename.encode('utf-8')

    filename_len = 0
    data_len = 0
    with open(file_path, mode='rb') as f:
        old = f.read(4)
        filename_len, data_len = struct.unpack('HH', old)
        filename = decrypt(key, f.read(filename_len)).decode('utf-8')
        head100 = decrypt(key, f.read(data_len))
        others = f.read()

        with open(filename, 'wb+') as ff:
            ff.write(head100)
            ff.write(others)


def main(args):
    if args.e:
        encode(args.f)
    elif args.d:
        decode(args.f)
    elif args.l:
        if os.path.isdir(args.f):
            for p, d, fs in os.walk(args.f):
                for f in fs:
                    get_name(os.path.join(p, f))
        else:
            get_name(args.f)
