#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .const import Spec
from .header import LHeader, BHeader


class Reply:
    def __init__(self):
        self._serial = -1
        self._buffer = b''
        self._header = None

    def unpack(self, buf):
        self._buffer += buf
        while self._buffer:
            self._unpack_header()
            data = self._unpack_body()
            if data is None:
                raise StopIteration
            data = self._convert_data(data)
            header = self._header
            self._header = None
            yield header, data

    def _unpack_body(self):
        if not self._header or len(self._buffer) < self._header.datalen:
            return
        data = self._buffer[:self._header.datalen - 1]  # cut b'\x00' here
        self._buffer = self._buffer[self._header.datalen:]
        return data

    def _unpack_header(self):
        while not self._header and len(self._buffer) >= Spec.HeaderSize:
            header = LHeader()
            header.unpack(self._buffer[:Spec.HeaderSize])
            if header.magic != Spec.MagicNumber:
                header = BHeader()
                header.unpack(self._buffer[:Spec.HeaderSize])
                if header.magic != Spec.MagicNumber:
                    self._buffer = self._buffer[1:]
                    continue
            self._buffer = self._buffer[Spec.HeaderSize:]
            self._header = header

    def _convert_data(self, data):
        if self._header.typ in (Spec.String, Spec.Double):
            try:
                data = float(data)
            except ValueError:
                data = data.decode()
            return data
        else:
            return data.decode()
