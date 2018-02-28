from inoon_lora_packet.packet import (Packet, NoticeType,
                                      HexConverter, InvalidPacketError)


# TODO: Refactoring this...

class NoticeV3Packet(Packet):
    err_desc = {
        0x00: 'No reason.',
        0x01: 'Exceed Alive period.',
        0x02: 'LoRa TX fail.',
        0x04: 'LoRa join fail.',
        0x05: 'Watchdog,',
        0x06: 'No Ack for PowerOff notice.',
        0x07: 'LoRa PowerOff Command.',
        0x08: 'BLE PowerOff.',
        0x09: 'Low Battery.',
        0x0A: 'Exceed Install request.',
        0x0B: 'RESET_CONFIG.',
        0x0C: 'PowefOffUninstallCommand',
        0x0D: 'PowerOffUninstallByResv.',
        0x0E: 'PowerOffDeviceUpsideDown',
        0x81: 'Factory reset.',
        0x82: 'Upside down.',
        0x83: 'Watchdod changed.',
        0x84: 'LoRa reset.',
        0x85: 'BLE reset',
        0x86: 'LoRa SKT reset',
        0x87: 'LoRa FW updated.',
    }

    setup_desc = {
        0: 'Uninstall',
        1: 'Install',
        2: 'ReqInstall'
    }

    def _field_spec(self):
        try:
            notice_type = int(self.raw_packet[:2], 16)

            if notice_type == NoticeType.power_up:
                return PowerV3Packet.spec
            elif notice_type == NoticeType.power_off:
                return PowerV3Packet.spec
            elif notice_type == NoticeType.setup:
                return SetupV3Packet.spec

            raise InvalidPacketError
        except Exception:
            raise InvalidPacketError

    def __str__(self):
        msg = None
        if self.type == NoticeType.power_up:
            msg = self.__power_log_msg()
        elif self.type == NoticeType.power_off:
            msg = self.__power_log_msg()

        elif self.type == NoticeType.setup:
            msg = self.__setup_msg()

        return msg

    def __power_log_msg(self):
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

        msg += 'Err({}): {}'.format(self.error, self.err_desc[self.error])

        return msg

    def __setup_msg(self):
        return 'SETUP | {} -> {}'.format(self.previous, self.current)


class PowerV3Packet():
    spec = [
        {'name': 'type',
         'bytes': 1,
         'convert': HexConverter.hex_to_uint,
         'restrict': [NoticeType.power_up, NoticeType.power_off]},

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
         'restrict': [key for key in NoticeV3Packet.err_desc.keys()]},

    ]

    @classmethod
    def encode(cls, is_power_up, reason, error):
        enc_val = ''
        enc_val += format(1 if is_power_up is True else 2, '02x')
        enc_val += format(4, '02x')
        enc_val += format(reason, '02x')
        enc_val += '0000'
        enc_val += format(error, '02x')
        return enc_val.lower()


class SetupV3Packet(Packet):
    spec = [
        {'name': 'type',
         'bytes': 1,
         'convert': HexConverter.hex_to_uint,
         'restrict': None},

        {'name': 'len',
         'bytes': 1,
         'convert': HexConverter.hex_to_uint,
         'restrict': [2]},

        {'name': 'current',
         'bytes': 1,
         'convert': HexConverter.hex_to_uint,
         'restrict': [0, 1, 2]},

        {'name': 'previous',
         'bytes': 1,
         'convert': HexConverter.hex_to_uint,
         'restrict': [0, 1, 2]},
    ]

    @classmethod
    def encode(cls, prev_install, current_install):
        enc_val = ''
        enc_val += format(NoticeType.setup, '02x')
        enc_val += format(2, '02x')
        enc_val += format(current_install, '02x')
        enc_val += format(prev_install, '02x')
        return enc_val.lower()
