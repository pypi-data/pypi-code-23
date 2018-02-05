"""Unit tests the alert methods of the Matchlight SDK."""
import datetime
import json
import time
import uuid

import httpretty
import pytest

import matchlight


@pytest.mark.httpretty
def test_alert_dates(connection, alert, alert_payload):
    """Verifies alert date objects are converted correctly."""
    httpretty.register_uri(
        httpretty.GET, '{}/alerts?limit=50'.format(
            matchlight.MATCHLIGHT_API_URL_V2
        ),
        body=json.dumps({'alerts': [alert_payload]}),
        content_type='application/json',
        status=200
    )
    alerts = connection.alerts.filter(limit=50)
    assert isinstance(alerts[0].date, datetime.datetime)
    assert isinstance(alerts[0].last_modified, datetime.datetime)


@pytest.mark.httpretty
def test_alert_filter(connection, alert, alert_payload):
    """Verifies alert listing and filtering."""
    httpretty.register_uri(
        httpretty.GET, '{}/alerts?limit=50'.format(
            matchlight.MATCHLIGHT_API_URL_V2
        ),
        body=json.dumps({'alerts': [alert_payload]}),
        content_type='application/json',
        status=200
    )
    alerts = connection.alerts.filter(limit=50)
    assert len(alerts) == 1
    assert alerts[0].id == alert.id


@pytest.mark.httpretty
def test_alert_filter_seen(connection, alert, alert_payload):
    """Verifies alert filtering on 'seen'."""
    # Create opposite alert
    unseen_payload = alert_payload.copy()
    unseen_payload['seen'] = 'false'
    unseen_payload['id'] = str(uuid.uuid4())

    # Get seen alerts
    httpretty.register_uri(
        httpretty.GET, '{}/alerts?seen=1&limit=50'.format(
            matchlight.MATCHLIGHT_API_URL_V2
        ),
        body=json.dumps({'alerts': [alert_payload]}),
        content_type='application/json',
        status=200
    )

    alerts = connection.alerts.filter(limit=50, seen=True)
    assert len(alerts) == 1
    assert alerts[0].id == alert_payload['id']

    # Get unseen alerts
    httpretty.register_uri(
        httpretty.GET, '{}/alerts?seen=0&limit=50'.format(
            matchlight.MATCHLIGHT_API_URL_V2
        ),
        body=json.dumps({'alerts': [unseen_payload]}),
        content_type='application/json',
        status=200
    )

    alerts = connection.alerts.filter(limit=50, seen=False)
    assert len(alerts) == 1
    assert alerts[0].id == unseen_payload['id']


@pytest.mark.httpretty
def test_alert_filter_archived(connection, alert, alert_payload):
    """Verifies alert filtering on 'archived'."""
    # Create opposite alert
    unarchived_payload = alert_payload.copy()
    unarchived_payload['archived'] = 'false'
    unarchived_payload['id'] = str(uuid.uuid4())

    # Get archived alerts
    httpretty.register_uri(
        httpretty.GET, '{}/alerts?archived=1&limit=50'.format(
            matchlight.MATCHLIGHT_API_URL_V2
        ),
        body=json.dumps({'alerts': [alert_payload]}),
        content_type='application/json',
        status=200
    )

    alerts = connection.alerts.filter(limit=50, archived=True)
    assert len(alerts) == 1
    assert alerts[0].id == alert_payload['id']

    # Get unarchived alerts
    httpretty.register_uri(
        httpretty.GET, '{}/alerts?archived=0&limit=50'.format(
            matchlight.MATCHLIGHT_API_URL_V2
        ),
        body=json.dumps({'alerts': [unarchived_payload]}),
        content_type='application/json',
        status=200
    )

    alerts = connection.alerts.filter(limit=50, archived=False)
    assert len(alerts) == 1
    assert alerts[0].id == unarchived_payload['id']


@pytest.mark.httpretty
def test_alert_filter_project(connection, alert, alert_payload, project):
    """Verifies alert filtering on 'upload_token'."""
    httpretty.register_uri(
        httpretty.GET, '{}/alerts?upload_token_filter={}&limit=50'.format(
            matchlight.MATCHLIGHT_API_URL_V2,
            project.upload_token
        ),
        body=json.dumps({'alerts': [alert_payload]}),
        content_type='application/json',
        status=200
    )

    alerts = connection.alerts.filter(limit=50, project=project)
    assert len(alerts) == 1
    assert alerts[0].id == alert_payload['id']


@pytest.mark.httpretty
def test_alert_filter_record(connection, alert, alert_payload,
                             document_record):
    """Verifies alert filtering on 'record_id'."""
    httpretty.register_uri(
        httpretty.GET, '{}/alerts?record_id_filter={}&limit=50'.format(
            matchlight.MATCHLIGHT_API_URL_V2,
            document_record.id
        ),
        body=json.dumps({'alerts': [alert_payload]}),
        content_type='application/json',
        status=200
    )

    alerts = connection.alerts.filter(limit=50, record=document_record)
    assert len(alerts) == 1
    assert alerts[0].id == alert_payload['id']


@pytest.mark.httpretty
def test_alert_filter_mtime(connection, alert, alert_payload):
    """Verifies alert filtering on 'seen'."""
    now = time.time()
    # Two days ago
    old_payload = alert_payload.copy()
    old_payload['mtime'] = now - 172800
    old_payload['id'] = str(uuid.uuid4())

    # Get all alerts
    httpretty.register_uri(
        httpretty.GET, '{}/alerts?mtime={}&limit=50'.format(
            matchlight.MATCHLIGHT_API_URL_V2,
            now - 259200
        ),
        body=json.dumps({'alerts': [alert_payload, old_payload]}),
        content_type='application/json',
        status=200
    )

    alerts = connection.alerts.filter(
        limit=50,
        last_modified=datetime.datetime.fromtimestamp(now - 259200)
    )
    assert len(alerts) == 2

    # Get new alerts
    httpretty.register_uri(
        httpretty.GET, '{}/alerts?mtime={}&limit=50'.format(
            matchlight.MATCHLIGHT_API_URL_V2,
            now - 86400
        ),
        body=json.dumps({'alerts': [alert_payload]}),
        content_type='application/json',
        status=200
    )

    alerts = connection.alerts.filter(
        limit=50,
        last_modified=datetime.datetime.fromtimestamp(now - 86400)
    )
    assert len(alerts) == 1
    assert alerts[0].id == alert_payload['id']


@pytest.mark.httpretty
def test_alert_edit(connection, alert, alert_payload):
    """Verifies alert editing."""
    # Do nothing
    httpretty.register_uri(
        httpretty.POST, '{}/alert/{}/edit'.format(
            matchlight.MATCHLIGHT_API_URL_V2,
            alert.id,
        ),
        body=json.dumps({
            'archived': True,
            'seen': True
        }),
        status=200
    )
    response = connection.alerts.edit(alert.id)
    assert response['seen'] is True
    assert response['archived'] is True

    # Un-archive
    httpretty.register_uri(
        httpretty.POST, '{}/alert/{}/edit'.format(
            matchlight.MATCHLIGHT_API_URL_V2,
            alert.id,
        ),
        body=json.dumps({
            'archived': False,
            'seen': True
        }),
        status=200
    )
    response = connection.alerts.edit(alert.id, archived=False)
    assert response['seen'] is True
    assert response['archived'] is False

    # Un-see
    httpretty.register_uri(
        httpretty.POST, '{}/alert/{}/edit'.format(
            matchlight.MATCHLIGHT_API_URL_V2,
            alert.id,
        ),
        body=json.dumps({
            'archived': False,
            'seen': False
        }),
        status=200
    )
    response = connection.alerts.edit(alert.id, seen=False)
    assert response['seen'] is False
    assert response['archived'] is False

    # Both
    httpretty.register_uri(
        httpretty.POST, '{}/alert/{}/edit'.format(
            matchlight.MATCHLIGHT_API_URL_V2,
            alert.id,
        ),
        body=json.dumps({
            'archived': True,
            'seen': True
        }),
        status=200
    )
    response = connection.alerts.edit(alert.id, seen=True, archived=True)
    assert response['seen'] is True
    assert response['archived'] is True


@pytest.mark.httpretty
def test_alert_details(connection, alert, alert_details_pii_payload):
    """Verifies alert get details responses."""
    httpretty.register_uri(
        httpretty.GET, '{}/alert/{}/details'.format(
            matchlight.MATCHLIGHT_API_URL_V2,
            alert.id
        ),
        body=json.dumps(alert_details_pii_payload),
        content_type='application/json',
        status=200
    )

    details_ = connection.alerts.get_details(alert)
    assert details_ == alert_details_pii_payload

    details_ = connection.alerts.get_details(alert.id)
    assert details_ == alert_details_pii_payload
