#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import ctypes


class _Header:
    # noinspection PyTypeChecker
    _fields_ = [
        ('magic', ctypes.c_uint32),
        ('header', ctypes.c_int32),
        ('size', ctypes.c_uint32),
        ('id', ctypes.c_uint32),
        ('sec', ctypes.c_uint32),
        ('usec', ctypes.c_uint32),
        ('cmd', ctypes.c_int32),
        ('typ', ctypes.c_int32),
        ('rows', ctypes.c_uint32),
        ('cols', ctypes.c_uint32),
        ('datalen', ctypes.c_uint32),
        ('error', ctypes.c_int32),
        ('flags', ctypes.c_int32),
        ('name', ctypes.c_char * 80)
    ]

    def pack(self, serial, cmd, typ, datalen, name):
        timestamp = time.time()
        from .const import Spec
        self.magic = Spec.MagicNumber
        self.header = Spec.HeaderVersion
        self.size = ctypes.sizeof(self)
        self.id = serial
        self.sec = int(timestamp)
        self.usec = int((timestamp - self.sec) * 1e6)
        self.cmd = cmd
        self.typ = typ
        self.datalen = datalen
        self.name = name.encode()
        self.error = 0
        # noinspection PyTypeChecker
        return bytes(self)

    def unpack(self, buffer):
        ctypes.memmove(ctypes.addressof(self), buffer, ctypes.sizeof(self))
        self.name = self.name.replace(b'\x00', b'')
        return self

    def __repr__(self):
        try:
            return (f'<Spec header: size={self.size:d}, id={self.id:d}, cmd={self.cmd:d}, type={self.typ:d}, '
                    f'datalen={self.datalen:d}, error={self.error:d}, name={self.name}')
        except AttributeError:
            return ''


class LHeader(ctypes.LittleEndianStructure):
    _fields_ = _Header._fields_
    pack = _Header.pack
    unpack = _Header.unpack
    __repr__ = _Header.__repr__


class BHeader(ctypes.BigEndianStructure):
    _fields_ = _Header._fields_
    pack = _Header.pack
    unpack = _Header.unpack
    __repr__ = _Header.__repr__


Header = LHeader
