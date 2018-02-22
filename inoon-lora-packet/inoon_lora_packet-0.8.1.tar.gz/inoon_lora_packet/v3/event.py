from inoon_lora_packet.packet import Packet, HexConverter, EventType


class EventV3Packet(Packet):
    def _field_spec(self):
        return [
            {'name': 'type',
             'bytes': 1,
             'convert': HexConverter.hex_to_uint,
             'restrict': [EventType[k] for k in EventType._member_map_]},

            {'name': 'x_count',
             'bytes': 1,
             'convert': HexConverter.hex_to_uint,
             'restrict': None},

            {'name': 'y_count',
             'bytes': '1',
             'convert': HexConverter.hex_to_uint,
             'restrict': None},

            {'name': 'z_count',
             'bytes': '1',
             'convert': HexConverter.hex_to_uint,
             'restrict': None},
        ]

    def __str__(self):
        msg = 'EVENT | '
        if self.type == 1:
            msg += 'High-G'
        elif self.type == 8:
            msg += 'Collapse'
        else:
            msg += '{}'.format(self.type)
        msg += ' | '

        msg += 'Intr. Cnt.: {}, {}, {} | '.format(self.x_count, self.y_count,
                                                  self.z_count)

        return msg

    @classmethod
    def encode(cls, event_type, x_count, y_count, z_count):
        enc_val = ''
        enc_val += format(event_type, '02x')
        enc_val += format(x_count, '02x')
        enc_val += format(y_count, '02x')
        enc_val += format(z_count, '02x')
        return enc_val.lower()
