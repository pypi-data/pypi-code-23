from .bcrypt import BCryptScheme
from AuthEncoding import registerScheme

registerScheme(u'BCRYPT', BCryptScheme())
