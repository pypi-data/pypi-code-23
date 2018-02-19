from inoon_lora_packet.packet import Packet, HexConverter, AckType


class AckV3Packet(Packet):
    def _field_spec(self):
        return [
            {'name': 'ack_type',
             'bytes': 1,
             'convert': HexConverter.hex_to_uint,
             'restrict': [AckType[k] for k in AckType._member_map_]
             },
        ]

    def __str__(self):
        code_desc = {
            AckType.ext_mgmt: 'ExtDevMgmt',
            AckType.dev_reset: 'DevReset',
            AckType.per_change: 'RepPerChange',
            AckType.immediate: 'RepImmediate'
        }

        msg = 'ACK | '
        msg += 'TYPE: {}({}) | '.format(code_desc[self.ack_type],
                                        self.ack_type)
        return msg

    @classmethod
    def encode(cls, ack_type):
        return format(ack_type, '02x').lower()
