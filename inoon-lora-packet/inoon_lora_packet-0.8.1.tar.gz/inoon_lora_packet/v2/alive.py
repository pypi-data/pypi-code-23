from inoon_lora_packet.packet import Packet, HexConverter
from inoon_lora_packet.bsp.accelerometer import BMA250E


class AliveV2Packet(Packet):
    def _field_spec(self):
        return [
            {'name': 'x',
             'bytes': 2,
             'convert': HexConverter.hex_to_int16,
             'restrict': None},

            {'name': 'y',
             'bytes': 2,
             'convert': HexConverter.hex_to_int16,
             'restrict': None},

            {'name': 'z',
             'bytes': 2,
             'convert': HexConverter.hex_to_int16,
             'restrict': None},

            {'name': 'alive_period',
             'bytes': 2,
             'convert': HexConverter.hex_to_uint,
             'restrict': None},

            {'name': 'sensitivity',
             'bytes': 1,
             'convert': HexConverter.hex_to_uint,
             'restrict': None},

            {'name': 'threshold',
             'bytes': 2,
             'convert': HexConverter.hex_to_uint,
             'restrict': None},

            {'name': 'acc_no',
             'bytes': 1,
             'convert': HexConverter.hex_to_uint,
             'restrict': None},

            {'name': 'acc_resv',
             'bytes': 1,
             'convert': HexConverter.hex_to_uint,
             'restrict': None},

            {'name': 'acc_data',
             'bytes': 1,
             'convert': HexConverter.hex_to_uint,
             'restrict': None},

            {'name': 'data_enabled',
             'bytes': 1,
             'convert': HexConverter.hex_to_uint,
             'restrict': [0, 1]},

            {'name': 'data_interval',
             'bytes': 1,
             'convert': HexConverter.hex_to_uint,
             'restrict': None},

            {'name': 'data_blocks',
             'bytes': 1,
             'convert': HexConverter.hex_to_uint,
             'restrict': None},

            {'name': 'installed',
             'bytes': 1,
             'convert': HexConverter.hex_to_uint,
             'restrict': [0, 1]},

            {'name': 'app_fw_major',
             'bytes': 1,
             'convert': HexConverter.hex_to_uint,
             'restrict': None},

            {'name': 'app_fw_minor',
             'bytes': 1,
             'convert': HexConverter.hex_to_uint,
             'restrict': None},

            {'name': 'app_fw_rev',
             'bytes': 1,
             'convert': HexConverter.hex_to_uint,
             'restrict': None},

            {'name': 'lora_fw_major',
             'bytes': 1,
             'convert': HexConverter.hex_to_uint,
             'restrict': None},

            {'name': 'lora_fw_minor',
             'bytes': 1,
             'convert': HexConverter.hex_to_uint,
             'restrict': None},

            {'name': 'lora_fw_rev',
             'bytes': 1,
             'convert': HexConverter.hex_to_uint,
             'restrict': None},

            {'name': 'rssi',
             'bytes': 1,
             'convert': HexConverter.hex_to_int8,
             'restrict': None},

        ]

    @property
    def gravity_x(self):
        return BMA250E.gravity(sensitivity=self.sensitivity, raw_value=self.x)

    @property
    def gravity_y(self):
        return BMA250E.gravity(sensitivity=self.sensitivity, raw_value=self.y)

    @property
    def gravity_z(self):
        return BMA250E.gravity(sensitivity=self.sensitivity, raw_value=self.z)

    def __str__(self):
        msg = ''
        msg += 'ALIVE | '
        msg += 'Acc Conf.: {}G, {}mg | '.format(2**self.sensitivity,
                                                self.threshold)
        msg += 'Acc Intr.: {}, {} | '.format(self.acc_no, self.acc_data)
        msg += 'Acc Vals.: {}, {}, {} | '.format(self.x, self.y, self.z)
        msg += 'Log: {}, {}s, {}blks | '.format(
            'EN' if self.data_enabled is 1 else 'DIS',
            self.data_interval, self.data_blocks)

        msg += 'Inst.: {} | '.format('Y' if self.installed is 1 else 'N')
        msg += 'Per: {}m | '.format(self.alive_period)
        msg += 'RSSI : {}'.format(self.rssi)

        return msg

    @classmethod
    def encode(self, x, y, z, period, sensitivity, threshold,
               acc_no, acc_data, data_enabled, data_interval, data_blocks,
               installed, app_fw_major, app_fw_minor, app_fw_rev,
               lora_fw_major, lora_fw_minor, lora_fw_rev, rssi):
        enc = ''
        enc += HexConverter.int_to_hex(x, 2, True)
        enc += HexConverter.int_to_hex(y, 2, True)
        enc += HexConverter.int_to_hex(z, 2, True)

        enc += format(period, '04x')
        enc += format(sensitivity, '02x')
        enc += format(threshold, '04x')

        enc += format(acc_no, '02x')
        enc += '00'
        enc += format(acc_data, '02x')

        enc += format(data_enabled, '02x')
        enc += format(data_interval, '02x')
        enc += format(data_blocks, '02x')

        enc += format(installed, '02x')

        enc += format(app_fw_major, '02x')
        enc += format(app_fw_minor, '02x')
        enc += format(app_fw_rev, '02x')

        enc += format(lora_fw_major, '02x')
        enc += format(lora_fw_minor, '02x')
        enc += format(lora_fw_rev, '02x')

        enc += HexConverter.int_to_hex(rssi, 1, True)

        return enc.lower()
