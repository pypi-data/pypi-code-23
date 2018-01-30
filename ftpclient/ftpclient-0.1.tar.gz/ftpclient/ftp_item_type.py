from enum import IntEnum

__all__ = ["FtpItemType"]


class FtpItemType(IntEnum):
    cdir = 1,
    pdir = 2,
    dir = 3,
    file = 4,
    unknown = 5
