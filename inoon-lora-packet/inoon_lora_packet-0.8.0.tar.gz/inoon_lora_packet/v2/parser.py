from inoon_lora_packet.packet import (PacketType, PacketHeaderV2,
                                      InvalidPacketError,
                                      NotSupportedPacketError)
from inoon_lora_packet.base import base_parser
from .alive import AliveV2Packet
from .notice import NoticeV2Packet
from .data_log import DataLogV2Packet
from .event import EventV2Packet
from .ack import AckV2Packet
from .error import ErrorV2Packet


class Ver2Parser(base_parser.Parser):
    @property
    def header_length(self):
        return 16

    def parse(self, raw_packet):
        if len(raw_packet) < self.header_length:
            raise InvalidPacketError

        header = PacketHeaderV2(raw_packet)
        raw_payload = raw_packet[self.header_length:]
        packet = None

        if header.packet.type == PacketType.alive:
            packet = AliveV2Packet(raw_payload)
        elif header.packet.type == PacketType.notice:
            packet = NoticeV2Packet(raw_payload)
        elif header.packet.type == PacketType.data_log:
            packet = DataLogV2Packet(raw_payload)
        elif header.packet.type == PacketType.event:
            packet = EventV2Packet(raw_payload)
        elif header.packet.type == PacketType.ack:
            packet = AckV2Packet(raw_payload)
        elif header.packet.type == PacketType.error:
            packet = ErrorV2Packet(raw_payload)
        else:
            raise NotSupportedPacketError

        return header, packet
