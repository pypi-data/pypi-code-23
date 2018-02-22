from inoon_lora_packet.packet import Packet, HexConverter


class AliveV3Packet(Packet):
    mg_per_step = {
        1: 3.91,
        2: 7.81,
        3: 15.63,
        4: 31.25,
    }

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

        ]

    @property
    def gravity_x(self):
        return self._to_gravity(self.x)

    @property
    def gravity_y(self):
        return self._to_gravity(self.y)

    @property
    def gravity_z(self):
        return self._to_gravity(self.z)

    def _to_gravity(self, raw_value):
        gravity = self.mg_per_step[self.sensitivity] * raw_value / 1000
        return round(gravity, 5)

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
        msg += 'App FW: {}.{}.{} | '.format(self.app_fw_major,
                                            self.app_fw_minor,
                                            self.app_fw_rev)
        msg += 'LoRa FW: {}.{}.{}'.format(self.lora_fw_major,
                                          self.lora_fw_minor,
                                          self.lora_fw_rev)

        return msg

    @classmethod
    def encode(self, x, y, z, period, sensitivity, threshold,
               acc_no, acc_data, data_enabled, data_interval, data_blocks,
               installed, app_fw_major, app_fw_minor, app_fw_rev,
               lora_fw_major, lora_fw_minor, lora_fw_rev):
        """Create alive payload for version 3 spec.
        """
        enc = ''
        enc += HexConverter.int_to_hex(x, 2, True)
        enc += HexConverter.int_to_hex(y, 2, True)
        enc += HexConverter.int_to_hex(z, 2, True)

        enc += format(period, '04x')
        enc += format(sensitivity, '02x')
        enc += format(threshold, '04x')

        enc += format(acc_no, '02x')
        enc += '00'  # Acc Resv
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

        return enc.lower()
