# IPv4 Reassembly Usage
from reassembly import IPv4_Reassembly
# Initialise instance:
# kayword argument `strict` is set to False in default
# if strict set to True, all datagram will return
# else, only implemented ones will submit
ipv4_reassembly = IPv4_Reassembly(strict=False)
# Call reassembly:
ipv4_reassembly(packet_dict)
packet_dict = dict(
    bufid = tuple(
        ipv4.src,
        ipv4.dst,
        ipv4.id,
        ipv4.proto,
    ),
    fo = ipv4.frag_offset,
    ihl = ipv4.hdr_len,
    mf = ipv4.flags.mf,
    tl = ipv4.len,          # total length, header includes
    header = ipv4.header,   # raw bytearray type header
    payload = ipv4.payload,     # raw bytearray type payload
)
# Fetch result:
result = ipv4_reassembly.datagram
'''Datagram structure:

(tuple) datagram
    |--> (dict) data
    |       |--> "fragments" : (tuple) packet numbers
    |       |                           |--> (int) original packet range number
    |       |--> "NotImplemented" : (bool) True --> implemented
    |       |--> "packet" : (bytes) IPv4 reassembled packet
    |--> (dict) data
    |       |--> "fragments" : (tuple) packet numbers
    |       |                           |--> (int) original packet range number
    |       |--> "NotImplemented" : (bool) False --> not implemented
    |       |--> "header" : (bytes) IPv4 header
    |       |--> "payload" : (tuple) partially reassembled payload
    |       |                           |--> (bytes) payload fragment
    |--> (dict) data ...
'''


# IPv6 Reassembly
from reassembly import IPv6_Reassembly
# Initialise instance:
# kayword argument `strict` is set to False in default
# if strict set to True, all datagram will return
# else, only implemented ones will submit
ipv6_reassembly = IPv6_Reassembly(strict=False)
# Call reassembly:
ipv6_reassembly(packet_dict)
packet_dict = dict(
    bufid = tuple(
        ipv6.src,
        ipv6.dst,
        ipv6.label,
        ipv6_frag.next,     # next header field in IPv6 Fragment Header
    ),
    fo = ipv6_frag.offset,
    ihl = ipv6.hdr_len,     # header length, headers after IPv6-Frag excludes
    mf = ipv6.ipv6_frag.mf,
    tl = ipv6.len,          # total length, headers include
    header = ipv6.header,   # raw bytearray type header before IPv6-Frag (IPv6-Frag excludes)
    payload = ipv6.payload, # raw bytearray type payload after IPv6-Frag (IPv6-Frag excludes)
)
# Fetch result:
result = ipv6_reassembly.datagram
'''Datagram structure:

(tuple) datagram
    |--> (dict) data
    |       |--> "fragments" : (tuple) packet numbers
    |       |                           |--> (int) original packet range number
    |       |--> "NotImplemented" : (bool) True --> implemented
    |       |--> "packet" : (bytes) IPv6 reassembled packet
    |--> (dict) data
    |       |--> "fragments" : (tuple) packet numbers
    |       |                           |--> (int) original packet range number
    |       |--> "NotImplemented" : (bool) False --> not implemented
    |       |--> "header" : (bytes) IPv6 unfragmental header
    |       |--> "payload" : (tuple) partially reassembled payload
    |       |                           |--> (bytes) payload fragment
    |--> (dict) data ...
'''


# TCP Reassembly
from reassembly import TCP_Reassembly
# Initialise instance:
# kayword argument `strict` is set to False in default
# if strict set to True, all datagram will return
# else, only implemented ones will submit
tcp_reassembly = TCP_Reassembly(strict=False)
# Call reassembly:
tcp_reassembly(packet_dict)
packet_dict = dict(
    bufid = tuple(
        ip.src,
        ip.dst,
        tcp.secport,
        tcp.dstport,
    ),
    ack = tcp.ack,
    dsn = tcp.seq,                  # Data Sequence Number
    syn = tcp.flags.syn,
    fin = tcp.flags.fin,
    len = tcp.raw_len,              # payload length, header excludes
    first = tcp.seq,
    last = tcp.seq + tcp.raw_len,   # next (wanted) sequence number
    header = tcp.header,            # raw bytearray type header
    payload = tcp.raw,              # raw bytearray type payload
)
# Fetch result:
result = tcp_reassembly.datagram
'''Datagram structure:

(tuple) datagram
    |--> (dict) data
    |       |--> "fragments" : (tuple) packet numbers
    |       |                           |--> (int) original packet range number
    |       |--> "NotImplemented" : (bool) True --> implemented
    |       |--> "payload" : (bytes) reassembled application layer data
    |--> (dict) data
    |       |--> "fragments" : (tuple) packet numbers
    |       |                           |--> (int) original packet range number
    |       |--> "NotImplemented" : (bool) False --> not implemented
    |       |--> "payload" : (tuple) partially reassembled payload
    |       |                           |--> (bytes) payload fragment
    |--> (dict) data ...
'''
