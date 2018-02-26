# coding=utf-8
from pathlib import Path

import requests
from mockito import mock, verifyStubbedInvocationsAreUsed, when

from elib import downloader

URL = r'http://www.ovh.net/files/1Mio.dat'


def test_download():
    assert downloader.download(url=URL, outfile='./test', hexdigest='6cb91af4ed4c60c11613b75cd1fc6116')
    assert Path('./test').exists()


def test_download_wrong_digest():
    assert not downloader.download(url=URL, outfile='./test', hexdigest='nope')
    assert not Path('./test').exists()


def test_download_no_digest():
    assert downloader.download(url=URL, outfile='./test')
    assert Path('./test').exists()


def test_download_no_data():
    when(downloader.Downloader).download_to_memory(...)
    assert not downloader.download(url=URL, outfile='./test', hexdigest='6cb91af4ed4c60c11613b75cd1fc6116')
    verifyStubbedInvocationsAreUsed()
    assert not Path('./test').exists()


def test_download_to_memory_no_data():
    when(downloader.Downloader)._create_response().thenReturn(None)
    assert not downloader.download(url=URL, outfile='./test', hexdigest='6cb91af4ed4c60c11613b75cd1fc6116')
    verifyStubbedInvocationsAreUsed()
    assert not Path('./test').exists()


def test_download_delete_failed():
    Path('./test').touch()
    assert Path('./test').exists()
    when(downloader.Downloader)._create_response().thenReturn(None)
    assert not downloader.download(url=URL, outfile='./test', hexdigest='6cb91af4ed4c60c11613b75cd1fc6116')
    verifyStubbedInvocationsAreUsed()
    assert not Path('./test').exists()


def test_download_request_failed():
    req = mock()
    req.ok = False
    req.reason = 'nope'
    when(requests).head(...).thenReturn(req)
    assert not downloader.download(url=URL, outfile='./test', hexdigest='6cb91af4ed4c60c11613b75cd1fc6116')
    verifyStubbedInvocationsAreUsed()
    assert not Path('./test').exists()


def test_download_method_not_allowed():
    req = mock()
    req.ok = False
    req.reason = 'Method Not Allowed'
    when(requests).head(...).thenReturn(req)
    when(downloader.Downloader).download(...).thenReturn(True)
    assert downloader.download(url=URL, outfile='./test', hexdigest='6cb91af4ed4c60c11613b75cd1fc6116')
    verifyStubbedInvocationsAreUsed()
    assert not Path('./test').exists()
