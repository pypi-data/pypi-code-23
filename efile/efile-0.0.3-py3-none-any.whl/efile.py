import base64
import os.path
import shutil
import struct


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
        filename = base64.standard_b64decode(
            f.read(filename_len)).decode('utf-8')

        print(filename)


def encode(file_path):
    filename = os.path.basename(file_path)
    new_filename = get_md5(filename)

    dfilename = base64.b64encode(filename.encode('utf-8'))
    lfilename = len(dfilename)

    shutil.copy(file_path, new_filename)

    bdata = None
    bdata_len = 0
    with open(file_path, mode='rb') as f:
        bdata = base64.b64encode(f.read(100))
        bdata_len = len(bdata)

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
    filename_len = 0
    data_len = 0
    with open(file_path, mode='rb') as f:
        old = f.read(4)
        filename_len, data_len = struct.unpack('HH', old)
        filename = base64.b64decode(f.read(filename_len)).decode('utf-8')
        head100 = base64.b64decode(f.read(data_len))
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
