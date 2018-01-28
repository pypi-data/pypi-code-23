#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#  @namespace pytz-convert

__title__ = 'pytz-convert'
__version__ = '0.2.7'
__version_info__ = tuple(__version__.split('.'))

__author__ = 'jefft@tune.com'
__license__ = 'MIT License'
__copyright__ = 'Copyright 2018 TUNE, Inc.'

__python_required_version__ = (3, 0)

from .timezone_utils import (
    validate_tz_abbrev,
    validate_tz_name,

    convert_tz_abbrev_to_tz_hours,
    convert_tz_abbrev_to_tz_offset,
    convert_tz_abbrev_to_tz_seconds,
    convert_tz_hours_to_tz_offset,
    convert_tz_name_to_date_tz_abbrev,
    convert_tz_name_to_date_tz_offset,
    convert_tz_name_to_now_tz_abbrev,
    convert_tz_name_to_now_tz_offset,
    convert_tz_offset_and_date_to_tz_name,
    convert_tz_offset_to_now_tz_abbrev,
    convert_tz_offset_to_tz_hours,
    convert_tz_offset_to_tz_minutes,
    convert_tz_offset_to_tz_seconds,
    parse_gmt_offset_timezone,
    convert_bing_ads_tz
)
