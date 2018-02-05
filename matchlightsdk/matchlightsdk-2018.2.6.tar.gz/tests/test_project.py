"""Unit tests the project methods of the Matchlight SDK."""
import datetime
import json

import httpretty
import pytest
import six.moves

import matchlight


PROJECT_TYPES = ('bulk_pii', 'document', 'pii', 'source_code')


def test_project_last_modified(project):
    """Verifies that a project's ``last_date_modified`` is parsed."""
    assert project.last_modified == datetime.datetime.fromtimestamp(
        project.last_date_modified)


@pytest.mark.httpretty
def test_project_add(connection, project_name, project_payload,
                     project_type, upload_token):
    """Verifies project creation."""
    httpretty.register_uri(
        httpretty.POST, '{}/project/add'.format(
            matchlight.MATCHLIGHT_API_URL_V2),
        body=json.dumps({'data': project_payload}),
        content_type='application/json', status=200)
    project = connection.projects.add(project_name, project_type)
    assert project.upload_token == upload_token


@pytest.mark.httpretty
def test_project_edit(connection, project, project_payload):
    """Verifies project renaming."""
    httpretty.register_uri(
        httpretty.POST, '{}/project/{}/edit'.format(
            matchlight.MATCHLIGHT_API_URL_V2,
            project.upload_token,
        ),
        body='{}', status=200)
    new_name = 'Test Project 1'
    connection.projects.edit(project, new_name)
    assert project.name == new_name

    new_name = 'Test Project 2'
    httpretty.register_uri(
        httpretty.GET, '{}/project/{}'.format(
            matchlight.MATCHLIGHT_API_URL_V2,
            project.upload_token,
        ),
        body=json.dumps(project_payload),
        content_type='application/json', status=200)
    project = connection.projects.edit(project.upload_token, new_name)
    assert project.name == new_name


@pytest.mark.httpretty
def test_project_delete(connection, project, project_payload):
    """Verifies project deletion."""
    httpretty.register_uri(
        httpretty.POST, '{}/project/{}/delete'.format(
            matchlight.MATCHLIGHT_API_URL_V2,
            project.upload_token,
        ),
        body='{}', status=200)
    httpretty.register_uri(
        httpretty.GET, '{}/project/{}'.format(
            matchlight.MATCHLIGHT_API_URL_V2,
            project.upload_token,
        ),
        body=json.dumps(project_payload),
        content_type='application/json', status=200)
    connection.projects.delete(project)


@pytest.mark.httpretty
def test_project_filter(connection, project_payload, project):
    """Verifies project listing and filtering by type."""
    httpretty.register_uri(
        httpretty.GET, '{}/projects'.format(
            matchlight.MATCHLIGHT_API_URL_V2),
        body=json.dumps({'data': [project_payload]}),
        content_type='application/json', status=200)
    projects = connection.projects.filter()
    assert len(projects) == 1
    assert projects[0].upload_token == project.upload_token

    httpretty.reset()

    project_list = [project_payload]
    for _ in six.moves.range(5):
        payload = project_payload.copy()
        for project_type in PROJECT_TYPES:
            if project_type == payload['project_type']:
                continue
            payload['project_type'] = project_type
            break
        project_list.append(payload)
    httpretty.register_uri(
        httpretty.GET, '{}/projects'.format(
            matchlight.MATCHLIGHT_API_URL_V2),
        body=json.dumps({'data': project_list}),
        content_type='application/json', status=200)
    projects = connection.projects.filter(project_type=project.project_type)
    assert len(projects) == 1
    assert projects[0].project_type == project.project_type


@pytest.mark.httpretty
def test_project_get(connection, project_payload, project):
    """Verifies project retrieval."""
    httpretty.register_uri(
        httpretty.GET, '{}/project/{}'.format(
            matchlight.MATCHLIGHT_API_URL_V2,
            project.upload_token),
        responses=[
            httpretty.Response(body=json.dumps(project_payload),
                               content_type='application/json',
                               status=200),
            httpretty.Response(body='{}', content_type='application/json',
                               status=404),
            httpretty.Response(body='{}', content_type='application/json',
                               status=500),
        ])

    project_ = connection.projects.get(project.upload_token)
    assert project.upload_token == project_.upload_token

    project_ = connection.projects.get(project.upload_token)
    assert project_ is None

    with pytest.raises(matchlight.error.ConnectionError):
        connection.projects.get(project.upload_token)


@pytest.mark.httpretty
def test_project_iteration(connection, project, project_payload):
    """Verifies project iteration."""
    httpretty.register_uri(
        httpretty.GET, '{}/projects'.format(matchlight.MATCHLIGHT_API_URL_V2),
        body=json.dumps({'data': [project_payload]}),
        content_type='application/json', status=200,
    )
    projects_iterable = iter(connection.projects)
    assert next(projects_iterable).details == project.details
    with pytest.raises(StopIteration):
        next(projects_iterable)
