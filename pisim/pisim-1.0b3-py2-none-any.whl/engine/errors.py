# -*- coding: utf-8 -*-

"""Module defining exceptions raised by other modules in the package.

Module's content
================

"""


class EngineBaseError(Exception):
    """Base exception, doing nothing."""

    pass


class EtaPensionamentoNotFoundError(EngineBaseError):
    """Exception raised if tasso di conversione value is not found."""

    def __init__(self, sex, age):
        """Constructor.

        :param str sex: The sex whose index was not found.
        :param int age: The age whose index was not found.
        """
        self.age = age
        self.sex = sex

    def __str__(self):
        """Exception error string."""
        return (
            "Tasso di conversione montante f.p. <-> "
            "rendita pensionistica per anni '{}' "
            "& sesso '{}' non specificato").format(self.age, self.sex)
