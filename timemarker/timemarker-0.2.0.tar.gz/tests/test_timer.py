# -*- coding: utf-8 -*-

from time import sleep

import pytest

import timemarker

from .helpers import split_oneline


class TestBasics(object):

    def test_instantiate(self):
        timer = timemarker.TimeMarker()
        assert isinstance(timer, timemarker.TimeMarker)

    def test_contextmgr(self):
        with timemarker.TimeMarker() as timer:
            assert isinstance(timer, timemarker.TimeMarker)

        assert isinstance(timer, timemarker.TimeMarker)


class TestExceptions(object):

    def test_badtag(self):
        for tag_name in ['start', 'stop']:
            with pytest.raises(ValueError):
                with timemarker.TimeMarker() as timer:
                    timer.tag(tag_name)


class TestPctgTimer(object):

    def test_onetag_pctg(self, capsys):
        with timemarker.TimeMarker() as timer:
            timer.tag("sleep_100ms")
            sleep(.1)
        timer.stats()

        out, err = capsys.readouterr()
        assert err == ''
        assert out != ''
        out_dict = split_oneline(out)

        assert out_dict['TIME'] == pytest.approx(0.1, abs=1e-2)
        assert out_dict['start'] == pytest.approx(0.0, abs=1e-2)
        assert out_dict['sleep_100ms'] == pytest.approx(1.0, abs=1e-2)

    def test_twotag_pctg(self, capsys):
        with timemarker.TimeMarker() as timer:
            timer.tag("sleep_100ms_1")
            sleep(.1)
            timer.tag("sleep_100ms_2")
            sleep(.1)
        timer.stats()

        out, err = capsys.readouterr()
        assert err == ''
        assert out != ''
        out_dict = split_oneline(out)

        assert out_dict['TIME'] == pytest.approx(0.2, abs=1e-2)
        assert out_dict['start'] == pytest.approx(0.0, abs=1e-2)
        assert out_dict['sleep_100ms_1'] == pytest.approx(.5, abs=1e-2)
        assert out_dict['sleep_100ms_2'] == pytest.approx(.5, abs=1e-2)


class TestRawTimer(object):

    def test_onetag_raw(self, capsys):
        with timemarker.TimeMarker() as timer:
            timer.tag("sleep_100ms")
            sleep(.1)
        timer.stats(fmt="raw")

        out, err = capsys.readouterr()
        assert err == ''
        assert out != ''
        out_dict = split_oneline(out)

        assert out_dict['TIME'] == pytest.approx(0.1, abs=1e-2)
        assert out_dict['start'] == pytest.approx(0.0, abs=1e-2)
        assert out_dict['sleep_100ms'] == pytest.approx(.1, abs=1e-2)

    def test_twotag_raw(self, capsys):
        with timemarker.TimeMarker() as timer:
            timer.tag("sleep_100ms_1")
            sleep(.1)
            timer.tag("sleep_100ms_2")
            sleep(.1)
        timer.stats(fmt="raw")

        out, err = capsys.readouterr()
        assert err == ''
        assert out != ''
        out_dict = split_oneline(out)

        assert out_dict['TIME'] == pytest.approx(0.2, abs=1e-2)
        assert out_dict['start'] == pytest.approx(0.0, abs=1e-2)
        assert out_dict['sleep_100ms_1'] == pytest.approx(.1, abs=1e-2)
        assert out_dict['sleep_100ms_2'] == pytest.approx(.1, abs=1e-2)


class TestTagging(object):
    def test_tag_aggregation(self, capsys):
        with timemarker.TimeMarker() as timer:
            # Run this test twice and see if the the same tags are aggregated
            for i in range(2):
                timer.tag("sleep_100ms_1")
                sleep(.1)
                timer.tag("sleep_100ms_2")
                sleep(.1)
        timer.stats(fmt='raw')

        out, err = capsys.readouterr()
        assert err == ''
        assert out != ''
        out_dict = split_oneline(out)

        assert out_dict['TIME'] == pytest.approx(0.4, abs=1e-2)
        assert out_dict['start'] == pytest.approx(0.0, abs=1e-2)
        assert out_dict['sleep_100ms_1'] == pytest.approx(.2, abs=1e-2)
        assert out_dict['sleep_100ms_2'] == pytest.approx(.2, abs=1e-2)

