import pytest
import responses

from datarobot import errors
from datarobot.async import wait_for_async_resolution


@responses.activate
def test_success(client, async_url, async_success_callback, resolved_url):
    responses.add_callback(
        responses.GET,
        async_url,
        callback=async_success_callback,
        content_type='application/json'
    )
    result = wait_for_async_resolution(client, async_url)
    assert result == resolved_url


@responses.activate
def test_job_failure(client,
                     async_url,
                     async_job_failure_callback,
                     ):
    responses.add_callback(
        responses.GET,
        async_url,
        callback=async_job_failure_callback,
        content_type='application/json'
    )
    with pytest.raises(errors.AsyncProcessUnsuccessfulError):
        wait_for_async_resolution(client, async_url)


@responses.activate
def test_server_wtf(client,
                    async_url,
                    async_server_nonsense_callback,
                    ):
    responses.add_callback(
        responses.GET,
        async_url,
        callback=async_server_nonsense_callback,
        content_type='application/json'
    )
    with pytest.raises(errors.AsyncFailureError):
        wait_for_async_resolution(client, async_url)


@responses.activate
def test_server_timeout(client,
                        async_url,
                        async_not_finished_callback,
                        mock_async_time):
    responses.add_callback(
        responses.GET,
        async_url,
        callback=async_not_finished_callback,
        content_type='application/json'
    )
    mock_async_time.time.side_effect = (0, 0, 10**6)

    with pytest.raises(errors.AsyncTimeoutError):
        wait_for_async_resolution(client, async_url)
