# encoding: utf-8

"""
cessa.config
===========

This module defines all configuration constants for seccomp profile.

:Copyright (c) by hac(Xiao An) <hac@zju.edu.cn>. All Rights Reserved.

"""

from enum import Enum, unique

PROJECT_NAME = 'Cessa'
SYSTABLE_FILE = '/usr/local/configs/systable.list'
SYSDIG_CONF_FILE = '/usr/local/configs/sysdig.json'
LOG_FILE = '/var/log/audit/audit.log'

@unique
class Action(Enum):

    """ Defines actions for seccomp rules

    """
    KILL = 1
    TRAP = 2
    ERRNO = 3
    TRACE = 4
    ALLOW = 5

@unique
class Arch(Enum):

    """ Defines architectures

    """
    X86 = 1
    X86_64 = 2
    X32 = 3
    ARM = 4
    AARCH64 = 5
    MIPS = 6
    MIPS64 = 7
    MIPS64N32 = 8
    MIPSEL = 9
    MIPSEL64 = 10
    MIPSEL64N32 = 11
    PPC = 12
    PPC64 = 13
    PPC64LE = 14
    S390 = 15
    S390X = 16


@unique
class Operator(Enum):

    """ Defines operators for syscall arguments

    """
    NOT_EQUAL = 1
    LESS_THAN = 2
    LESS_EQUAL = 3
    EQUAL_TO = 4
    GREATER_EQUAL = 5
    GREATER_THAN = 6
    MASKED_EQUAL = 7


@unique
class Level(Enum):

    """ Represents the level of rule generation

    """
    NAME = 1
    ARG = 2
    CLABEL = 3
    CUSTOM = 4

    def __str__(self):
        return 'Level-{}'.format(self.name)

    def degrade(self, num=1):
        new_value = self.value - num > 0
        if new_value < Level.NAME.value:
            new_value = Level.NAME.value
        return Level(new_value)

    def upgrade(self, num=1):
        new_value = self.value + num
        if new_value > Level.CUSTOM.value:
            new_value = Level.CUSTOM.value
        return Level(new_value)



