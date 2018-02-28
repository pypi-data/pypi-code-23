from inoon_lora_packet.packet import Packet, HexConverter


class ReportV3Packet(Packet):
    def _field_spec(self):
        return [
            {'name': 'ctrl',
             'bytes': 1,
             'bit_fields': [
                 {'name': 'method', 'bits': 1, 'restrict': None},
                 {'name': 'overflow', 'bits': 1, 'restrict': None},
                 {'name': 'resv', 'bits': 2, 'restrict': None},
                 {'name': 'scale', 'bits': 4, 'restrict': None}
             ]},
            {'name': 'avg',
             'bytes': 2,
             'convert': HexConverter.hex_to_int16,
             'restrict': None},
            {'name': 'stddev',
             'bytes': 2,
             'convert': HexConverter.hex_to_uint,
             'restrict': None},
            {'name': 'min',
             'bytes': 2,
             'convert': HexConverter.hex_to_int16,
             'restrict': None},
            {'name': 'max',
             'bytes': 2,
             'convert': HexConverter.hex_to_int16,
             'restrict': None},
        ]

    def __str__(self):
        msg = ''
        msg += 'REPORT | '
        msg += 'Scale: {} | '.format(self.ctrl.scale)
        msg += 'Avg.: {}mg | '.format(self.gravity(self.avg))
        msg += 'StdDev.: {}mg | '.format(self.gravity(self.stddev))
        msg += 'Min.: {}mg | '.format(self.gravity(self.min))
        msg += 'Max.: {}mg '.format(self.gravity(self.max))
        return msg

    def gravity(self, value):
        return round(float(value) / self.ctrl.scale * 3.91, 2)

    @classmethod
    def encode(cls, scale, avg, std, min_val, max_val):
        enc = ''
        enc += '{:02X}'.format(scale)
        enc += HexConverter.int_to_hex(avg, 2, True)
        enc += HexConverter.int_to_hex(std, 2, False)
        enc += HexConverter.int_to_hex(min_val, 2, True)
        enc += HexConverter.int_to_hex(max_val, 2, True)
        return enc.lower()
