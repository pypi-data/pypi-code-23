from Crypto.PublicKey import ECC
from Crypto.Hash import SHA256
from Crypto.Signature import DSS

key = ECC.import_key(open("ecc.pem").read())
h = SHA256.new(b"ccc")
signer = DSS.new(key, 'fips-186-3', 'der')
signature = signer.sign(h)

verifier = DSS.new(key, 'fips-186-3', 'der')
import pdb; pdb.set_trace()
verifier.verify(h, signature)
