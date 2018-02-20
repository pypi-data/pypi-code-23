from ax26 import constants as const

ALL_BYTES = (const.DATA_CHUNK, const.DATA_END, const.CONNECT, const.ACK, const.CHECKSUM, const.DISCONNECT, const.GARBAGE, const.RESEND, const.SEPARATOR)

def escape_data(data):
	for bytecode in ALL_BYTES:
		data = data.replace(bytecode, const.ESC + bytecode)
	return data

def recover_data(data):
	out = b''
	i = 0
	while i < len(data):
		if data[i] == const.ESC[0] and i + 1 < len(data):
			if bytes([data[i + 1]]) in ALL_BYTES:
				out += bytes([data[i + 1]])
				i += 1  # Skips over the next byte
			else:
				out += bytes([data[i]])
		else:
			out += bytes([data[i]])
		i += 1

	return out


def decode_packet(pkt):
	try:
		(calls, chunk) = bytes(pkt)[1:].split(const.SEPARATOR, 1)
		type_byte = bytes([chunk[0]])
		body = chunk[1:]
		(src, dest) = calls.split(b'>', 1)
		return (src, dest, type_byte, body)
	except ValueError:  # Exception when split fails (Invalid packet or nothing read)
		return (None, None, None, None)

def format_header(src, dest):
	return src + b'>' + dest + const.SEPARATOR