'''
Import the server certificate and server key from a certificate
chain file. The expected format of the chain file follows RFC 4346.
In short, the server certificate should come first, followed by
any ceritfying intermediate certificates, optionally followed by
the root trusted CA. The private key can be anywhere in this
order. See https://tools.ietf.org/html/rfc4346#section-7.4.2.

Requires:
pip install pyopenssl


@author: davidlepage
'''

import re
import sys
import pkg_resources

try:
    pkg_resources.get_distribution('pyopenssl')
except pkg_resources.DistributionNotFound:
    HAS_SSL = False
else:
    HAS_SSL = True


PY3 = sys.version_info[0] == 3
if PY3:
    unicode = str
else:
    unicode = unicode


CERT_TYPES = (b'CERTIFICATE', b'PRIVATE KEY', b'RSA PRIVATE KEY')

KEY_TYPES = (b'PRIVATE KEY', b'RSA PRIVATE KEY')

_PEM_RE = re.compile(b"-----BEGIN (" + b"|".join(CERT_TYPES) + \
    b""")-----\r?.+?\r?-----END \\1-----\r?\n?""", re.DOTALL)


    
def load_cert_chain(chain_file):
    """ 
    Load the certificates from the chain file.
    
    :raises IOError: Failure to read specified file
    :raises ValueError: Format issues with chain file or missing entries
    :return list of cert type matches
    """
    with open(chain_file, 'rb') as f:
        cert_chain = f.read()
    
    if not cert_chain:
        raise ValueError('Certificate chain file is empty!')

    cert_type_matches = []
    for match in _PEM_RE.finditer(cert_chain):
        cert_type_matches.append((match.group(1), match.group(0)))
    
    if not cert_type_matches:
        raise ValueError('No certificate types were found. Valid types '
            'are: {}'.format(CERT_TYPES))

    return cert_type_matches

    
class CertificateChain(object):
    def __init__(self):
        self.root = None
        self.intermediate = []
        self.private_key = None
        self.public_cert = None
        
    def __call__(self, cert=None, priv_key=None):
        """
        Pass in an openssl X509 object. This will update
        the object to split out the root cert from the
        intermediate certs and server cert/key.
        
        :param X509 cert: X509 object parsed from pyopenssl
        """
        if priv_key:
            self.private_key = priv_key
        elif cert.get_subject() == cert.get_issuer():
            self.root = cert
        else:
            if not self.public_cert:
                # Server certificate
                print("Set server cert: %s"% cert.get_subject())
                self.public_cert = cert
            else:
                # Intermediate certificate
                print("Intermediate cert: %s" % cert.get_subject())
                self.intermediate.append(cert)

    def dump_server_cert(self):
        """
        Dump the private key pkey into a buffer string encoded as PEM
        
        :return: the buffer with key dumped in
        :rtype: bytes
        """
        if self.public_cert:
            cert = OpenSSL.crypto.dump_certificate(
                OpenSSL.crypto.FILETYPE_PEM,
                self.public_cert)
            return cert
        raise ValueError('No server certificate found!')
    
    def dump_server_key(self):
        """
        Dump the server key into a buffer string encoded as PEM
        
        :return: the buffer with key dumped in
        :rtype: bytes
        """
        if self.private_key:
            key = OpenSSL.crypto.dump_privatekey(
                OpenSSL.crypto.FILETYPE_PEM,
                self.private_key)
            return key
        raise ValueError('No private key found!')
    
    @classmethod
    def from_file(cls, chain_file):
        """
        Read the certificate file specified and split out the
        server certificate, private key, intermediate certificates
        and root certificate (optional). 
        
        :raises ValueError: Format issues with chain file or missing entries
        :rtype: CertificateChain
        """
        chain = CertificateChain()
        for cert_def in load_cert_chain(chain_file):
            cert_type, b64_data = cert_def
            if cert_type in (b'CERTIFICATE',):
                cert = OpenSSL.crypto.load_certificate(
                    OpenSSL.crypto.FILETYPE_PEM,
                    b64_data)
                chain(cert)
            elif cert_type in CERT_TYPES:
                cert = OpenSSL.crypto.load_privatekey(
                    OpenSSL.crypto.FILETYPE_PEM,
                    b64_data)
                chain(priv_key=cert)
        return chain


if __name__ == '__main__':
    import OpenSSL
    from pprint import pprint
    chain = CertificateChain.from_file('/Users/davidlepage/Downloads/cert.chain')
    pprint(vars(chain))
    print(chain.dump_server_cert())
    print(chain.dump_server_key())
