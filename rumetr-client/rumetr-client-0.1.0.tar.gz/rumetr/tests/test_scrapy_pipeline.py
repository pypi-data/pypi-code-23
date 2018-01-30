import pytest

from ..scrapy import UploadPipeline
from .. import exceptions


@pytest.fixture
def spider():
    class MockedSpider:
        settings = {
            'TEST_SETTING': 1,
            'RUMETR_API_HOST': 'http://host',
            'RUMETR_TOKEN': 'tkn',
            'RUMETR_DEVELOPER': 'dvlpr',
        }
    return MockedSpider


def test_required_settings(spider):
    p = UploadPipeline()
    p.spider = spider
    p._parse_settings()
    assert p.settings['auth_key'] == 'tkn'
    assert p.settings['developer'] == 'dvlpr'


def test_no_required_setting_error(spider):
    del spider.settings['RUMETR_DEVELOPER']

    p = UploadPipeline()
    p.spider = spider
    with pytest.raises(TypeError):
        p._parse_settings()


def test_non_required_settings(spider):
    p = UploadPipeline()
    p.spider = spider
    p._parse_settings()
    assert p.settings['api_host'] == 'http://host'


def test_non_required_settings_are_no_present(spider):
    del spider.settings['RUMETR_API_HOST']
    p = UploadPipeline()
    p.spider = spider
    p._parse_settings()

    assert 'api_host' not in p.settings.keys()


def test_settings_are_parsed_only_once(spider):
    p = UploadPipeline()
    p.settings = {
        'eggs?': 'SPAM',
    }
    p.spider = spider
    p._parse_settings()
    assert p.settings == {
        'eggs?': 'SPAM',
    }  # should remain the same


@pytest.mark.parametrize('input, expected', [
    ('2017-12-01', '2017-12-01'),
    ('01.12.2016', '2016-12-01'),
])
def test_deadline_parsing(input, expected):
    assert UploadPipeline._parse_deadline(input) == expected


@pytest.mark.parametrize('input', [
    '2017',
    '2017-15-11 12:48',
    '12.12.2017 12:48',
    '12..2016',
    '12....2016',
])
def test_unparsable_deadlines(input):
    with pytest.raises(exceptions.RumetrUnparsableDeadline):
        UploadPipeline._parse_deadline(input)
