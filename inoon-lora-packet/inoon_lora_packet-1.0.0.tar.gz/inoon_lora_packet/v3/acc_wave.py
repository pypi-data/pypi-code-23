from inoon_lora_packet.packet import (Packet, InvalidPacketError, HexConverter)


class AccWaveV3Packet(Packet):
    axis_ctrl = {
        0: ['x', 'y', 'z'],
        1: ['x'],
        2: ['y'],
        3: ['z']
    }

    def _field_spec(self):
        return [
            {'name': 'ctrl',
             'bytes': 1,
             'bit_fields': [
                 {'name': 'resv', 'bits': 2, 'restrict': None},
                 {'name': 'axis', 'bits': 2, 'restrict': [0, 1, 2, 3]},
                 {'name': 'id', 'bits': 4, 'restrict': None}
             ]},
            {'name': 'seq',
             'bytes': 1,
             'convert': HexConverter.hex_to_uint,
             'restrict': range(0, 256)}
        ]

    def __init__(self, raw_packet):
        super(self.__class__, self).__init__(raw_packet)

        log_packet = raw_packet[4:]
        axises = self.axis_ctrl[self.ctrl.axis]

        if len(log_packet) % (len(axises) * 4) != 0:
            raise InvalidPacketError

        for axis in axises:
            setattr(self, axis, [])

        frame_len = len(axises) * 4
        for i in range(0, len(log_packet), frame_len):
            frame = log_packet[i:i+frame_len]
            for i, axis in enumerate(axises):
                value = HexConverter.hex_to_int16(frame[i*4:(i+1)*4])
                getattr(self, axis).append(value)

    def __str__(self):
        msg = ''
        msg += 'WAVE | '
        msg += 'Axis: {} | '.format(' '.join(self.axis_ctrl[self.ctrl.axis]))
        msg += 'ID: {} | '.format(self.ctrl.id)
        msg += 'Seq: {}'.format(self.seq)
        return msg

    @classmethod
    def encode(cls, pckt_id, seq, axis, values):
        """values parameter is dict type.
        """
        enc = ''

        ctrl = (axis << 4) | pckt_id
        enc += '{:02X}'.format(ctrl)
        enc += '{:02X}'.format(seq)

        if axis == 0:
            acc_values = list(zip(values['x'], values['y'], values['z']))

            for value in acc_values:
                enc += HexConverter.int_to_hex(value[0], 2, True)
                enc += HexConverter.int_to_hex(value[1], 2, True)
                enc += HexConverter.int_to_hex(value[2], 2, True)
        else:
            axis_name = ''
            if axis == 1:
                axis_name = 'x'
            elif axis == 2:
                axis_name = 'y'
            else:
                axis_name = 'z'

            for value in values[axis_name]:
                enc += HexConverter.int_to_hex(value, 2, True)

        return enc.lower()
