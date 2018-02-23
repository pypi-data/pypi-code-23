import pytest

from elife_bus_sdk.events import (
    ArticleEvent,
    CollectionEvent,
    MetricEvent,
    ProfileEvent
)


@pytest.mark.parametrize('event_class', [
    ArticleEvent,
    CollectionEvent,
    ProfileEvent
])
def test_event_will_init_with_required_fields_populated(event_class):
    assert event_class(id='12345')


@pytest.mark.parametrize('event_class', [
    ArticleEvent,
    CollectionEvent,
    ProfileEvent
])
def test_event_will_raise_exception_without_required_fields(event_class):
    with pytest.raises(AttributeError):
        event_class()


@pytest.mark.parametrize('event_class', [
    ArticleEvent,
    CollectionEvent,
    ProfileEvent
])
def test_event_can_be_converted_to_json(event_class):
    msg = event_class(id='12345')

    assert isinstance(msg.to_json(), str)


@pytest.mark.parametrize('event_class', [
    ArticleEvent,
    CollectionEvent,
    ProfileEvent
])
def test_it_will_allow_additional_fields_on_init(event_class):
    valid_data = {
        'id': 1234,
        'event': 'user_updated'
    }
    msg = event_class(**valid_data)

    assert msg['event'] == 'user_updated'


def test_metric_event_will_init_with_required_fields_populated():
    assert MetricEvent(contentType='someType', id='1234', metric='someMetric')


def test_metric_event_raises_exception_without_required_fields():
    with pytest.raises(AttributeError):
        MetricEvent()


def test_metric_event_can_be_converted_to_json():
    msg = MetricEvent(contentType='someType', id='1234', metric='someMetric')

    assert isinstance(msg.to_json(), str)


def test_metric_event_will_allow_additional_fields_on_init():
    valid_data = {
        'contentType': 'someType',
        'id': 1234,
        'metric': 'someMetric',
        'event': 'user_updated'
    }
    msg = MetricEvent(**valid_data)

    assert msg['event'] == 'user_updated'
