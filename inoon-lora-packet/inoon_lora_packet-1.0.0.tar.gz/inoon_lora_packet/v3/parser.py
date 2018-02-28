from inoon_lora_packet.packet import (PacketType, PacketHeaderV3,
                                      InvalidPacketError,
                                      NotSupportedPacketError)
from inoon_lora_packet.base import base_parser
from .ack import AckV3Packet
from .alive import AliveV3Packet
from .event import EventV3Packet
from .error import ErrorV3Packet
from .notice import NoticeV3Packet
from .data_log import DataLogV3Packet
from .report import ReportV3Packet
from .acc_wave import AccWaveV3Packet
from .inclination import InclinationV3Packet


class Ver3Parser(base_parser.Parser):
    @property
    def header_length(self):
        return 20

    def parse(self, raw_packet):
        if len(raw_packet) < self.header_length:
            raise InvalidPacketError

        header = PacketHeaderV3(raw_packet)
        raw_payload = raw_packet[self.header_length:-2]
        packet = None

        if header.packet.type == PacketType.alive:
            packet = AliveV3Packet(raw_payload)
        elif header.packet.type == PacketType.notice:
            packet = NoticeV3Packet(raw_payload)
        elif header.packet.type == PacketType.data_log:
            packet = DataLogV3Packet(raw_payload)
        elif header.packet.type == PacketType.event:
            packet = EventV3Packet(raw_payload)
        elif header.packet.type == PacketType.ack:
            packet = AckV3Packet(raw_payload)
        elif header.packet.type == PacketType.error:
            packet = ErrorV3Packet(raw_payload)
        elif header.packet.type == PacketType.report:
            packet = ReportV3Packet(raw_payload)
        elif header.packet.type == PacketType.acc_wave:
            packet = AccWaveV3Packet(raw_payload)
        elif header.packet.type == PacketType.inclination:
            packet = InclinationV3Packet(raw_payload)
        else:
            raise NotSupportedPacketError

        return header, packet
