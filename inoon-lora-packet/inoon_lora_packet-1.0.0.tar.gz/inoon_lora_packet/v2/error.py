from inoon_lora_packet.packet import Packet, HexConverter


class ErrorV2Packet(Packet):
    code_map = {
        1: 'OverReTx',
        2: 'JoinFail',
        3: 'Rx',
        4: 'Nok',
        5: 'OverReTxInifinite',
    }

    def _field_spec(self):
        return [
            {'name': 'code',
             'bytes': 1,
             'convert': HexConverter.hex_to_uint,
             'restrict': None},

            {'name': 'rssi',
             'bytes': 1,
             'convert': HexConverter.hex_to_int8,
             'restrict': None},
        ]

    def __str__(self):
        msg = ''
        msg += 'ERR | '
        msg += 'Code: {} | '.format(self.code_map[self.code])
        msg += 'RSSI: {}'.format(self.rssi)
        return msg

    @classmethod
    def encode(cls, code, rssi):
        enc = ''
        enc += format(code, '02x')
        enc += HexConverter.int_to_hex(rssi, 1, True)
        return enc.lower()
