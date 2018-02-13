# -*- coding: utf-8 -*-

__all__ = ["ChaosIQException", "ConfigurationMissingError",
           "ConfigurationTokenMissing"]


class ChaosIQException(Exception):
    pass


class ConfigurationMissingError(ChaosIQException):
    pass


class ConfigurationTokenMissing(ChaosIQException):
    pass
