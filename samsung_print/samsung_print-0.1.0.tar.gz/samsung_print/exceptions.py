"""
Copyright (c) 2017-2018 Fabian Affolter <fabian@affolter-engineering.ch>

Licensed under MIT. All rights reserved.
"""


class SamsungPrinterError(Exception):
    """General SamsungPrinterError exception occurred."""

    pass


class SamsungPrinterConnectionError(SamsungPrinterError):
    """When a connection error is encountered."""

    pass


class SamsungPrinterNoDataAvailable(SamsungPrinterError):
    """When no data is available."""

    pass
