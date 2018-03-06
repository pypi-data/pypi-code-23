"""Hashing, symmetric encryption, and public/private key encryption functions.

Example:
    >>> # hashing
    >>> from dtplib.encrypt import hashText
    >>> message = "Hello, World!"
    >>> hashText(message)
    '\xdf\xfd`!\xbb+\xd5\xb0\xafgb\x90\x80\x9e\xc3\xa51\x91\xdd\x81\xc7\xf7\nK(h\x8a6!\x82\x98o'
    >>> # symmetric encryption/decryption
    >>> from dtplib.encrypt import newKey, passwordToKey, symmetricEncrypt, symmetricDecrypt
    >>> newKey()
    'ivogckdeDlfDBQVgVquFdHSWhCclVyJ5livo8hbiGRg='
    >>> password = "password123"
    >>> key = passwordToKey(password)
    >>> key
    'y0fp6WXSMjb_mENcyx9289Bx18jh-FOH7vhTiH7SNpw='
    >>> ciphertext = symmetricEncrypt(message, key)
    >>> ciphertext
    'gAAAAABab5Ar3pUlQJOWRQK6TdpEEXPVCReT3mOoYSdEukkESmieaSdvNOmaWZnv2oUVC23KxIgGgWxLvvlvz2hTmvOeLanc-w=='
    >>> symmetricDecrypt(ciphertext, key)
    'Hello, World!'
    >>> # public/private key encryption/decryption
    >>> from dtplib.encrypt import newKeyPair, encrypt, decrypt
    >>> pub, priv = newKeyPair()
    >>> ciphertext = encrypt(message, pub)
    >>> ciphertext
    'J$_S\xdc$\xd1,\x9bB\x11\x10\x0b\x1c\xb10K\xdc&\xac\x9a\x1eJ\xa7\x97@\x91\xe1\xf5\xb8\x89uD\xa1#+\x1b\x92\xd4\xbf\xe7\x17/\xa6\xe0\x05\xaf%\xb4\xd0p.\x94\x90\x01\xcd\xa8\xd33\x9a0\xe1\x1aK'
    >>> decrypt(ciphertext, priv)
    'Hello, World!'
"""

import base64
import hashlib
import rsa
from rsa.bigfile import encrypt_bigfile, decrypt_bigfile
from cryptography.fernet import Fernet
from io import BytesIO

hashAlgorithm = "sha256"
keysize = 512

def hashText(text):
    """Hash some text."""
    hashed = hashlib.new(hashAlgorithm, text).digest()
    return hashed

def newKey():
    """Generate a new symmetric key."""
    key = Fernet.generate_key()
    return key

def passwordToKey(password):
    """Convert a password into a useable encryption/decryption key."""
    key = hashlib.new("sha256", password).digest()
    key = base64.urlsafe_b64encode(key)
    return key

def symmetricEncrypt(plaintext, key):
    """Encrypt text symmetrically with a key. Use passwordToKey if
    using a password instead of a generated key.
    """
    cipher = Fernet(key)
    ciphertext = cipher.encrypt(plaintext)
    return ciphertext

def symmetricDecrypt(ciphertext, key):
    """Decrypt text symmetrically with a key. Use passwordToKey if
    using a password instead of a generated key.
    """
    cipher = Fernet(key)
    plaintext = cipher.decrypt(ciphertext)
    return plaintext

def newKeyPair():
    """Generate a new public/private key pair."""
    pub, priv = rsa.newkeys(keysize)
    return pub, priv

def encrypt(plaintext, pubKey):
    """Encrypt text with a public key."""
    b = BytesIO()
    encrypt_bigfile(BytesIO(plaintext), b, pubKey)
    ciphertext = b.getvalue()
    return ciphertext

def decrypt(ciphertext, privKey):
    """Decrypt text with a private key."""
    b = BytesIO()
    decrypt_bigfile(BytesIO(ciphertext), b, privKey)
    plaintext = b.getvalue()
    return plaintext
