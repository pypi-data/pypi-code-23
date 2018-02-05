"""
Copyright (c) 2017-2018 Fabian Affolter <fabian@affolter-engineering.ch>

Licensed under MIT. All rights reserved.
"""
import asyncio
import logging

import yaml

import aiohttp
import async_timeout

from . import exceptions

_LOGGER = logging.getLogger(__name__)

_ENDPOINT = 'sws/app/information/home/home.json'


class Printer(object):
    """A class for handling connections to a Samsung printer."""

    def __init__(self, printer, loop, session):
        """Initialize the connection."""
        self._loop = loop
        self._session = session
        self.printer = printer
        self.data = None

    @asyncio.coroutine
    def async_get_data(self):
        url = 'http://{}/{}'.format(self.printer, _ENDPOINT)

        try:
            with async_timeout.timeout(5, loop=self._loop):
                response = yield from self._session.get(url)

            _LOGGER.debug("Response from printer: %s", response.status)
            raw_data = yield from response.text()
            self.data = yaml.load(raw_data.strip().replace('\t', ' '))
            _LOGGER.debug(self.data)
        except (asyncio.TimeoutError, aiohttp.ClientError):
            _LOGGER.error("Can not load data from printer")
            raise exceptions.SamsungPrinterConnectionError()

    def raw(self):
        """Show the raw data received from the printer."""
        return self.data

    def toner(self, color):
        """Details about the toner level."""
        toner_color = '{}_{}'.format('toner', color)
        return self.data[toner_color]

    def drum(self, color):
        """Details about the drum."""
        drum_color = '{}_{}'.format('drum', color)
        return self.data[drum_color]

    def tray(self, number):
        """Details about a tray."""
        tray_number = '{}{}'.format('tray', number)
        return self.data[tray_number]

    def capability(self):
        """Details about a capability."""
        return self.data['capability']

    def status(self, number):
        """Details about a capability."""
        return self.data['status'][number]

    def identity(self):
        """Details about a identity."""
        return self.data['identity']

    def capability(self):
        """Details about a capability."""
        return self.data['capability']

    def options(self):
        """Details about the options."""
        return self.data['options']

    def manual(self):
        """Details about the manual tray."""
        return self.data['manual']

    def mp(self):
        """Details about the mp."""
        return self.data['mp']

    def gxi(self):
        """Details about the GXI_X."""
        gxi = {}
        for entry, value in self.data.items():
            if entry.startswith('GXI_'):
                gxi[entry] = value
        return gxi
