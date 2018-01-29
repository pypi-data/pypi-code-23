#! usr/bin/env/ python3


# ------------------------------------------------------------------------------
import gnupg
gpg = gnupg.GPG(homedir='/Users/jpls/.gnupg')

pubkeys = gpg.list_keys()
seckeys = gpg.list_keys(secret=True)

for group in keyring:
    for k in sorted(group.keys()):
        print(k, ':', group[k])
    print('\n')



friend_keyid = 'A4FC428CD1C50019'


gpg.encrypt(fn, friend_keyid, output='test_files/enc_test_01', cipher_algo='AES256')

fn_enc = 'test_files/enc_test_01.asc'
gpg.decrypt_file(fn_enc, output='test_files/decoded.txt')


# import gnupg._parsers
# gnupg._parsers.Verify.TRUST_LEVELS["ENCRYPTION_COMPLIANCE_MODE"] = 23

fn = 'test_files/mpl_rcParams.txt'
fn_enc = 'test_files/enc_test_01'
fn_dec = 'test_files/decoded.txt'
pw = 'TESTPW5069'
key_settings = gpg.gen_key_input(key_type='RSA', key_length=1024, key_usage='ESCA', passphrase=pw)
key = gpg.gen_key(key_settings)
gpg.encrypt(fn, key.fingerprint, symmetric=True, output=fn_enc)

gpg.decrypt_file(fn_enc, passphrase=pw, output=fn_dec)



def encryptor(fn, fn_enc, pw):
    key_settings = gpg.gen_key_input(key_type='RSA', key_length=1024, key_usage='ESCA', passphrase=pw)
    key = gpg.gen_key(key_settings)
    with open(fn, 'rb') as infile:
        x = gpg.encrypt(infile, key.fingerprint, symmetric=True, output=fn_enc, passphrase=pw, armor=False)
    print(x.status)
    return x
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------

from cryptography.fernet import Fernet
key = Fernet.generate_key()
f = Fernet(key)
token = f.encrypt(b"secret")
f.decrypt(token)



import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


password = b"password"
salt = os.urandom(16)

kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=salt,
    iterations=100000,
    backend=default_backend()
    )

key = base64.urlsafe_b64encode(kdf.derive(password))

f = Fernet(key)
token = f.encrypt(b"Secret message!")
f.decrypt(token)



def load_key(passphrase, salt):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
        )

    return base64.urlsafe_b64encode(kdf.derive(passphrase))


def f_encrypt(key, fn, fnout):
    algo = Fernet(key)
    with open(fnout, 'wb') as outfile:
        with open(fn, 'rb') as infile:
            outfile.write(algo.encrypt(infile.read()))


def f_decrypt(key, fn, fnout):
    algo = Fernet(key)
    with open(fnout, 'wb') as outfile:
        with open(fn, 'rb') as infile:
            outfile.write(algo.decrypt(infile.read()))


def run_crypto(crypt_algo, fp_out, fp_in):
    with open(fp_out, 'wb') as outfile:
        with open(fp_in, 'rb') as infile:
            outfile.write(crypt_algo(infile.read()))


def crypto_test(key, fp):
    filename, ext = os.path.splitext(fp)
    encrypted = filename + '_enc' + ext
    decrypted = filename + '_dec' + ext

    s1 = perf_counter()
    f_encrypt(key, fp, encrypted)
    s2 = perf_counter()
    f_decrypt(key, encrypted, decrypted)
    s3 = perf_counter()

    print('-> enc: {:.4f} sec, -> dec: {:.4f} sec'.format(s2-s1, s3-s2))
    print('Filesize: {:,} kb'.format(os.path.getsize(fp) // 1000))
    print('Encrypted filesize ratio: {:.2%}'.format(os.path.getsize(encrypted) / os.path.getsize(fp)))
    status = md5_hash(fp) == md5_hash(decrypted)
    print('Status:', status)
