#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Monero Boost codec, portable binary archive
'''

import base64
import collections
import json

from . import xmrserialize as x


_UVARINT_BUFFER = bytearray(1)


async def load_uvarint(reader):
    """
    Monero portable_binary_archive boost integer serialization
    :param reader:
    :return:
    """
    buffer = _UVARINT_BUFFER
    await reader.areadinto(buffer)
    size = buffer[0]
    if size == 0:
        return 0

    negative = size < 0
    size = -size if negative else size
    result = 0
    shift = 0

    # TODO: endianity, rev bytes if needed
    for _ in range(size):
        await reader.areadinto(buffer)
        result += buffer[0] << shift
        shift += 8
    return result if not negative else -result


async def dump_uvarint(writer, n):
    """
    Monero portable_binary_archive boost integer serialization
    :param writer:
    :param n:
    :return:
    """
    buffer = _UVARINT_BUFFER
    if n == 0:
        buffer[0] = 0
        return await writer.awrite(buffer)

    negative = n < 0
    ll = -n if negative else n

    size = 0
    while ll != 0:
        ll >>= 8
        size += 1

    buffer[0] = size
    await writer.awrite(buffer)

    ll = -n if negative else n

    # TODO: endianity, rev bytes if needed
    for _ in range(size):
        buffer[0] = n & 0xff
        await writer.awrite(buffer)
        ll >>= 8


class TypeWrapper(object):
    """
    Boost serialization type wrapper - versioning.
    """
    def __init__(self, tp, params=None):
        self.tp = tp
        self.params = TypeWrapper.wrap_params(params)

    @staticmethod
    def wrap_params(params):
        if not isinstance(params, (tuple, list)):
            params = (params, )

        res = []
        for v in params:
            if isinstance(v, x.XmrType):
                v = TypeWrapper(v)

        return tuple(res)

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False


    def __repr__(self):
        return 'Type<%r:%r>' % (self.tp, self.params)


class Archive(x.Archive):

    def __init__(self, iobj, writing=True, **kwargs):
        super().__init__(iobj, writing, **kwargs)
        self.version_db = {}  # type: dict[type -> tuple[int, int]]

    def type_in_db(self, tp, params):
        """
        Determines if type is in the database
        :param tp:
        :return:
        """

    async def uvarint(self, elem):
        """
        Uvarint
        :param elem:
        :return:
        """
        if self.writing:
            return await dump_uvarint(self.iobj, elem)
        else:
            return await load_uvarint(self.iobj)

    async def uint(self, elem, elem_type, params=None):
        """
        Integer types
        :param elem:
        :param elem_type:
        :param params:
        :return:
        """
        one_b_type = isinstance(elem_type, (x.Int8, x.UInt8))
        if self.writing:
            return (await x.dump_uint(self.iobj, elem, 1)) if one_b_type else (await dump_uvarint(self.iobj, elem))
        else:
            return (await x.load_uint(self.iobj, 1)) if one_b_type else (await load_uvarint(self.iobj))

