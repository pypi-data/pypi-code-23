
import pickle, struct, logging, hashlib

MSG_PICKLED = 0x50535031        # PSP1 (pepperssh pickled v1)
FORMAT = '@LL'                  # Magic + length
HEADER_SIZE = struct.calcsize(FORMAT)

HASH_BUFFER_SIZE = 128 * 1024


logger = logging.getLogger('pepperssh')


class ProtocolError(Exception):
    """
    Raised when the data on the wire is not a pickled message.
    """
    def __init__(self, data):
        Exception.__init__(self, 'Unexpected data was received.  Perhaps stderr was not wrapped')
        self.data = data


def read_msg(readfunc):
    """
    Returns the next message read from the given function.

    Calls `readfunc` continuously (so make sure it is a blocking function) until a complete
    message has been read.
    """
    buffer = b''
    msglen = None
    while msglen is None or msglen > len(buffer):
        logger.debug('read_msg: About to read. msglen=%s bufferlen=%s', msglen, len(buffer))
        data = readfunc()
        logger.debug('read_msg: read %s bytes', len(data))
        if not data:
            raise RuntimeError('Connection closed before all data received')

        buffer += data

        if not msglen and len(buffer) >= HEADER_SIZE:
            # We have read enough for a header.  Verify the message type and extract
            # the length.
            msglen, buffer = decode_header(buffer)
            logger.debug('read_msg: decoded header.  msglen=%s', msglen)

    logger.debug('Read buffer: %r', buffer)

    msg = decode_msg(buffer)
    logger.debug('recv: %r', msg)
    return msg


def encode(msgdict):
    """
    Encodes a dictionary as a binary message.
    """
    msgbytes = pickle.dumps(msgdict)
    header = struct.pack(FORMAT, MSG_PICKLED, len(msgbytes))
    return (header, msgbytes)


def decode_header(buffer):
    if len(buffer) < HEADER_SIZE:
        raise ValueError(f'The header must be at least {HEADER_SIZE} bytes, not {len(buffer)}')
    magic, msglen = struct.unpack_from(FORMAT, buffer)
    if magic != MSG_PICKLED:
        raise ProtocolError(buffer)
    return msglen, buffer[HEADER_SIZE:]


def decode_msg(msgbytes):
    """
    Decodes a message back to a dictionary.
    """
    return pickle.loads(msgbytes)


def hash_file(filename):
    sha1 = hashlib.sha1()
    fd = open(filename, 'rb')
    while True:
        data = fd.read(HASH_BUFFER_SIZE)
        if not data:
            break
        sha1.update(data)
    return sha1.hexdigest()
