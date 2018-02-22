from inoon_lora_packet.packet import (Packet, NoticeType,
                                      HexConverter, InvalidPacketError)


class NoticeV2Packet(Packet):
    def _field_spec(self):
        try:
            notice_type = int(self.raw_packet[:2], 16)

            if notice_type == NoticeType.power_up:
                return PowerUpV2Packet.spec
            elif notice_type == NoticeType.power_off:
                return PowerOffV2Packet.spec
            elif notice_type == NoticeType.setup:
                return SetupV2Packet.spec

            raise InvalidPacketError
        except Exception:
            raise InvalidPacketError

    def __str__(self):
        msg = None
        if self.type == NoticeType.power_up:
            msg = self.__power_up_msg()
        elif self.type == NoticeType.power_off:
            msg = self.__power_off_msg()

        elif self.type == NoticeType.setup:
            msg = self.__setup_msg()

        msg += 'RSSI: {}'.format(self.rssi)
        return msg

    def __power_up_msg(self):
        msg = 'ON | '
        msg += 'Reset({}): '.format(self.reason)
        if self.reason & 0x08 == 0x08:
            msg += 'CPU '
        if self.reason & 0x04 == 0x04:
            msg += 'SW '
        if self.reason & 0x02 == 0x02:
            msg += 'WD '
        if self.reason & 0x01 == 0x01:
            msg += 'nRST'
        if self.reason is 0:
            msg += '--'
        msg += ' | '

        msg += 'Err({}): '.format(self.error)
        if self.error & 0x04 == 0x04:
            msg += 'Join '
        if self.error & 0x02 == 0x02:
            msg += 'TX '
        if self.error & 0x01 == 0x01:
            msg += 'Alive'
        if self.error is 0:
            msg += '--'
        msg += ' | '

        return msg

    def __power_off_msg(self):
        msg = 'OFF | '
        if self.data == 1:
            msg += 'LoRa Off Cmd'
        elif self.data == 2:
            msg += 'BLE Off Cmd'
        elif self.data == 3:
            msg += 'Uninstalled Dev(Auto Off)'
        elif self.data == 4:
            msg += 'Low BAT'
        elif self.data == 5:
            msg += 'Error'
        else:
            msg += ''
        msg += ' | '

        return msg

    def __setup_msg(self):
        msg = 'SETUP | '
        if self.install == 0:
            msg += 'Uninstall'
        else:
            msg += 'Install'
        msg += ' | '
        return msg


class PowerUpV2Packet():
    spec = [
        {'name': 'type',
         'bytes': 1,
         'convert': HexConverter.hex_to_uint,
         'restrict': None},

        {'name': 'len',
         'bytes': 1,
         'convert': HexConverter.hex_to_uint,
         'restrict': [4]},

        {'name': 'reason',
         'bytes': '1',
         'convert': HexConverter.hex_to_uint,
         'restrict': None},

        {'name': 'resv',
         'bytes': '2',
         'convert': HexConverter.hex_to_uint,
         'restrict': None},

        {'name': 'error',
         'bytes': '1',
         'convert': HexConverter.hex_to_uint,
         'restrict': None},

        {'name': 'rssi',
         'bytes': 1,
         'convert': HexConverter.hex_to_int8,
         'restrict': None},
    ]

    @classmethod
    def encode(cls, reason, error, rssi):
        enc_val = ''
        enc_val += format(NoticeType.power_up, '02x')
        enc_val += format(4, '02x')
        enc_val += format(reason, '02x')
        enc_val += '0000'
        enc_val += format(error, '02x')
        enc_val += HexConverter.int_to_hex(rssi, 1, True)
        return enc_val.lower()


class PowerOffV2Packet():
    spec = [
        {'name': 'type',
         'bytes': 1,
         'convert': HexConverter.hex_to_uint,
         'restrict': None},

        {'name': 'len',
         'bytes': 1,
         'convert': HexConverter.hex_to_uint,
         'restrict': [1]},

        {'name': 'data',
         'bytes': '1',
         'convert': HexConverter.hex_to_uint,
         'restrict': [1, 2, 3, 4, 5]},

        {'name': 'rssi',
         'bytes': 1,
         'convert': HexConverter.hex_to_int8,
         'restrict': None},
    ]

    @classmethod
    def encode(cls, data, rssi):
        enc_val = ''
        enc_val += format(NoticeType.power_off, '02x')
        enc_val += format(1, '02x')
        enc_val += format(data, '02x')
        enc_val += HexConverter.int_to_hex(rssi, 1, True)
        return enc_val.lower()


'''
class ResetV2Packet(Packet):
    def _field_spec(self):
        return [
            {'name': 'type',
             'bytes': 1,
             'convert': HexConverter.hex_to_uint,
             'restrict': None},

            {'name': 'len',
             'bytes': 1,
             'convert': HexConverter.hex_to_uint,
             'restrict': [0]},
        ]
'''


class SetupV2Packet(Packet):
    spec = [
        {'name': 'type',
         'bytes': 1,
         'convert': HexConverter.hex_to_uint,
         'restrict': None},

        {'name': 'len',
         'bytes': 1,
         'convert': HexConverter.hex_to_uint,
         'restrict': [1]},

        {'name': 'install',
         'bytes': 1,
         'convert': HexConverter.hex_to_uint,
         'restrict': [0, 1]},

        {'name': 'rssi',
         'bytes': 1,
         'convert': HexConverter.hex_to_int8,
         'restrict': None},
    ]

    @classmethod
    def encode(cls, install, rssi):
        enc_val = ''
        enc_val += format(NoticeType.setup, '02x')
        enc_val += format(1, '02x')
        enc_val += format(install, '02x')
        enc_val += HexConverter.int_to_hex(rssi, 1, True)
        return enc_val.lower()
