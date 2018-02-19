from .packet import InvalidPacketError, NotSupportedPacketError
from .v2.parser import Ver2Parser
from .v3.parser import Ver3Parser


class ParserFactory():
    @classmethod
    def get_parser(cls, version):

        if version is 1:
            return Ver2Parser()
        elif version is 2:
            return Ver2Parser()
        elif version is 3:
            return Ver3Parser()
        else:
            raise NotSupportedPacketError


class PacketParser():
    @classmethod
    def parse(cls, raw_packet):
        try:
            version = int(raw_packet[:2], 16)
            parser = ParserFactory.get_parser(version=version)
            return parser.parse(raw_packet=raw_packet)
        except ValueError:
            raise InvalidPacketError
