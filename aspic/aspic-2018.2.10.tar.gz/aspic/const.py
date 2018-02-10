#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ctypes
from .header import Header


class Spec:
    MagicNumber = 0xFEEDFACE
    HeaderVersion = 4
    HeaderSize = ctypes.sizeof(Header)
    Close = 1
    Abort = 2
    Command = 3
    CommandReturn = 4
    Register = 6
    Unregister = 7
    Event = 8
    Func = 9
    FuncReturn = 10
    ChannelRead = 11
    ChannelSend = 12
    Reply = 13
    Hello = 14
    HelloReply = 15
    Double = 1
    String = 2
    Error = 3
    Assoc = 4
    MaxChunkSize = 0x10000
    MinPort = 6510
    MaxPort = 6530
