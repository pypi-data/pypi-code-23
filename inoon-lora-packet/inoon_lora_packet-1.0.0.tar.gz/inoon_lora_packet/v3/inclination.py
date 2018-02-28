from inoon_lora_packet.packet import Packet, HexConverter


class InclinationV3Packet(Packet):
    def _field_spec(self):
        return [
            {'name': 'x_degree',
             'bytes': 2,
             'convert': HexConverter.hex_to_int16,
             'restrict': None},
            {'name': 'y_degree',
             'bytes': 2,
             'convert': HexConverter.hex_to_int16,
             'restrict': None},
            {'name': 'z_degree',
             'bytes': 2,
             'convert': HexConverter.hex_to_int16,
             'restrict': None},
        ]

    def __init__(self, raw_packet):
        super(self.__class__, self).__init__(raw_packet)

    def __str__(self):
        msg = 'INCLINATION | '
        msg += 'Degree Diff.: {}, {}, {}'.format(self.x_degree / 100.0,
                                                 self.y_degree / 100.0,
                                                 self.z_degree / 100.0)

        return msg

    @classmethod
    def encode(cls, x, y, z):
        enc = ''
        enc += '{}'.format(HexConverter.int_to_hex(x, 2, True))
        enc += '{}'.format(HexConverter.int_to_hex(y, 2, True))
        enc += '{}'.format(HexConverter.int_to_hex(z, 2, True))
        return enc.lower()
