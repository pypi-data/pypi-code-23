import datetime
import re
import time

import enum


Date = datetime.date
Time = datetime.time
Timestamp = datetime.datetime
Binary = buffer


def DateFromTicks(ticks):
    return Date(*time.localtime(ticks)[:3])


def TimeFromTicks(ticks):
    return Time(*time.localtime(ticks)[3:6])


def TimestampFromTicks(ticks):
    return Timestamp(*time.localtime(ticks)[:6])


class Type(enum.Enum):
    STRING = 'string'
    BINARY = 'binary'
    NUMBER = 'number'
    DATETIME = 'datetime'
    ROWID = 'rowid'
    UNKNOWN = 'unknown'

    @classmethod
    def from_header(cls, header):
        header = _clean_header(header)
        header = header.lower()
        try:
            return TYPE_REMAPPING[header]
        except KeyError:
            return cls(header)


header_cleaner = re.compile(r'^(\w+)\(.*\)$')


def _clean_header(header):
    match = header_cleaner.match(header)
    if match:
        header = match.group(1)
    return header


TYPE_REMAPPING = {
    'bigint': Type.NUMBER,
    'blob': Type.BINARY,
    'boolean': Type.NUMBER,
    'cblob': Type.STRING,
    'char': Type.STRING,
    'character': Type.STRING,
    'datetime': Type.DATETIME,
    'date': Type.DATETIME,
    'decimal': Type.NUMBER,
    'double precisison': Type.NUMBER,
    'double': Type.NUMBER,
    'dynamic': Type.UNKNOWN,
    'float': Type.NUMBER,
    'int2': Type.NUMBER,
    'int8': Type.NUMBER,
    'integer': Type.NUMBER,
    'int': Type.NUMBER,
    'mediumint': Type.NUMBER,
    'native character': Type.STRING,
    'nchar': Type.STRING,
    'numeric': Type.NUMBER,
    'nvarchar': Type.STRING,
    'real': Type.NUMBER,
    'smallint': Type.NUMBER,
    'text': Type.STRING,
    'timestamp': Type.DATETIME,
    'tinyint': Type.NUMBER,
    'unsigned big int': Type.NUMBER,
    'varchar': Type.STRING,
    'varying character': Type.STRING,
}


STRING = Type.STRING
BINARY = Type.BINARY
NUMBER = Type.NUMBER
DATETIME = Type.DATETIME
ROWID = Type.ROWID
