# -*- coding: utf-8 -*-

def noop(*args, **kwargs):
    pass

class AbstractDisassembler(object):
    _buffer = None
    _eop = None  # end of packet symbol
    _eoplen = None  # end of packet symbol length
    _charset = None

    def __call__(self, data):
        raise NotImplementedError('__call__ method must be implemented')

    def __init__(self, eop, charset='utf-8'):
        self._buffer = bytearray()
        self._charset = charset
        self._eop = eop
        self._eoplen = len(eop)

    def _extend_buffer(self, data):
        self._buffer.extend(data)
    
    def _parse_packets(self, data=None):
        packets = []
        
        if data is not None:
            self._extend_buffer(data)

        while True:
            try:
                eopstart = self._buffer.index(self._eop)
            except ValueError:
                break

            packet = self._buffer[:eopstart]
            
            # cut packet with end of packet sybmbols
            del self._buffer[:eopstart + self._eoplen]
            
            if len(packet):
                packets.append(self._parse_packet(packet))

        return packets

    def _parse_packet(self, data):
        raise NotImplementedError('_parse_packet method must be implement')


class GreetingDisassembler(AbstractDisassembler):
    """ For read just single greeting packet """

    _ongreeting = None

    def __init__(self, ongreeting=noop):
        super(GreetingDisassembler, self).__init__(b'\r\n')

        self._ongreeting = ongreeting

    def __call__(self, data):
        packets = self._parse_packets(data)

        if len(packets) > 0:
            for packet in packets:
                self._ongreeting(packet)

    # override
    def _parse_packet(self, data):
        greeting, version = data.decode(self._charset, 'ignore').split(u'/', 1)
        return greeting, version


class PacketDisassembler(AbstractDisassembler):
    _onpacket = None
    _onresponse = None
    _onevent = None
    _onunkown = None

    def __init__(self, onpacket=noop, onresponse=noop, onevent=noop, onunkown=noop):
        super(PacketDisassembler, self).__init__(b'\r\n\r\n')

        self._onpacket = onpacket
        self._onresponse = onresponse
        self._onevent = onevent
        
    def __call__(self, data):
        for packet in self._parse_packets(data):
            self._onpacket(packet)
            
            if 'Response' in packet.keys():
                self._onresponse(packet)
            elif 'Event' in packet.keys():
                self._onevent(packet)
            else:
                self._onunkown(packet)

    # NOTE: do more check
    def _parse_packet(self, data):
        entrys = (entry.decode(self._charset, 'ignore').split(':', 1) for entry in data.split(b'\r\n'))
        return {key.strip(): value.strip() for key, value in entrys}
