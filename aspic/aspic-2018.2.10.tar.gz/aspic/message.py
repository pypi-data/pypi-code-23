#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .const import Spec
from .header import LHeader


class Message:
    def __init__(self):
        self._serial = -1

    @property
    def serial(self):
        return self._serial

    @serial.setter
    def serial(self, serial):
        self._serial = serial

    def _pack_header(self, cmd, datalen=0, name='', typ=Spec.String):
        self._serial += 1
        h = LHeader()
        packed = h.pack(self._serial, cmd, typ, datalen, name)
        return packed

    def _pack_data(self, data):
        return str(data).encode(encoding='ascii', errors='ignore') + b'\x00'

    def _register(self, name='', datalen=0, *, typ=Spec.String):
        return self._pack_header(Spec.Register, datalen, name, typ)

    def _unregister(self, name='', datalen=0, *, typ=Spec.String):
        return self._pack_header(Spec.Unregister, datalen, name, typ)

    def _read(self, name='', datalen=0, *, typ=Spec.String):
        return self._pack_header(Spec.ChannelRead, datalen, name, typ)

    def _send(self, name='', datalen=0, *, typ=Spec.String):
        return self._pack_header(Spec.ChannelSend, datalen, name, typ)

    def hello(self):
        return self._pack_header(Spec.Hello, name='python')

    def abort(self):
        return self._pack_header(Spec.Abort)

    def motor_register_position(self, name):
        return self._register(f'motor/{name}/position')

    def motor_register_high_limit_hit(self, name):
        return self._register(f'motor/{name}/high_limit_hit')

    def motor_register_low_limit_hit(self, name):
        return self._register(f'motor/{name}/low_limit_hit')

    def motor_register_high_limit(self, name):
        return self._register(f'motor/{name}/high_limit')

    def motor_register_low_limit(self, name):
        return self._register(f'motor/{name}/low_limit')

    def motor_register_move_done(self, name):
        return self._register(f'motor/{name}/move_done')

    def motor_register_dial_position(self, name):
        return self._register(f'motor/{name}/dial_position')

    def motor_register_offset(self, name):
        return self._register(f'motor/{name}/offset')

    def motor_register_unusable(self, name):
        return self._register(f'motor/{name}/unusable')

    def motor_register_slew_rate(self, name):
        return self._register(f'motor/{name}/slew_rate')

    def motor_register_step_size(self, name):
        return self._register(f'motor/{name}/step_size')

    def motor_unregister_position(self, name):
        return self._unregister(f'motor/{name}/position')

    def motor_unregister_high_limit_hit(self, name):
        return self._unregister(f'motor/{name}/high_limit_hit')

    def motor_unregister_low_limit_hit(self, name):
        return self._unregister(f'motor/{name}/low_limit_hit')

    def motor_unregister_high_limit(self, name):
        return self._unregister(f'motor/{name}/high_limit')

    def motor_unregister_low_limit(self, name):
        return self._unregister(f'motor/{name}/low_limit')

    def motor_unregister_move_done(self, name):
        return self._unregister(f'motor/{name}/move_done')

    def motor_unregister_dial_position(self, name):
        return self._unregister(f'motor/{name}/dial_position')

    def motor_unregister_offset(self, name):
        return self._unregister(f'motor/{name}/offset')

    def motor_unregister_unusable(self, name):
        return self._unregister(f'motor/{name}/unusable')

    def motor_unregister_slew_rate(self, name):
        return self._unregister(f'motor/{name}/slew_rate')

    def motor_unregister_step_size(self, name):
        return self._unregister(f'motor/{name}/step_size')

    def motor_read_position(self, name):
        return self._read(f'motor/{name}/position')

    def motor_read_unusable(self, name):
        return self._read(f'motor/{name}/unusable')

    def motor_move(self, name, position):
        data = self._pack_data(position)
        header = self._send(f'motor/{name}/start_one', len(data))
        return header + data

    def motor_set_offset(self, name, offset):
        data = self._pack_data(offset)
        header = self._send(f'motor/{name}/offset', len(data))
        return header + data

    def motor_set_slew_rate(self, name, slew):
        data = self._pack_data(slew)
        header = self._send(f'motor/{name}/slew_rate', len(data))
        return header + data

    def counter_register(self, name):
        return self._register(f'scaler/{name}/value')

    def counter_unregister(self, name):
        return self._unregister(f'scaler/{name}/value')

    def counter_read(self, name):
        return self._read(f'scaler/{name}/value')

    def counter_count(self, name, sec):
        data = self._pack_data(sec)
        header = self._send(f'scaler/{name}/count', len(data))
        return header + data

    def command_run(self, command):
        data = self._pack_data(command)
        header = self._pack_header(Spec.CommandReturn, len(data))
        return header + data

    def command_register(self):
        return self._register('status/ready')

    def command_unregister(self):
        return self._unregister('status/ready')
