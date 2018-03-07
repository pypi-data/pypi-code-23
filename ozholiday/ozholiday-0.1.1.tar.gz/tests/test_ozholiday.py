#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `ozholiday` package."""
from datetime import date, datetime
import pytest
from ozholiday import isholiday




def test_not_a_holiday():
    assert not isholiday('20170105')

def test_not_a_holiday_withdetail():
    assert not isholiday('20170105', detail=True)

def test_new_years_day():
    assert isholiday('20180101')

def test_new_years_day_with_detail():
    assert isinstance(isholiday('20180101',detail=True), dict)

def test_new_years_day_with_detail_1():
    r = isholiday('20180101',detail=True)
    assert "New Year's Day" == r['Holiday Name']

def test_not_in_range():
    with pytest.raises(ValueError):
        r = isholiday('20991212')