SEPARATOR = b'\x01'
CHECKSUM = b'\x02'

DATA_START = b'\x12'
DATA_CHUNK = b'\x03'
DATA_END = b'\x04'

ACK = b'\x06'
RESEND = b'\x08'

GARBAGE = b'\x07'

CONNECT = b'\x09'
DISCONNECT = b'\x10'

ESC = b'\x11'