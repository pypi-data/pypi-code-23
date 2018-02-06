import time

from . import errors


def wait_for_async_resolution(client, async_location, max_wait=600):
    """
    Wait for successful resolution of the provided async_location.

    Parameters
    ----------
    client : RESTClientObject
        The configured v2 requests session
    async_location : str
        The URL we are polling for resolution. This can be either a fully-qualified URL
        like `http://host.com/routeName/` or just the relative route within the API
        i.e. `routeName/`.
    max_wait : int
        The number of seconds to wait before giving up

    Returns
    -------
    location : str
        The URL of the now-finished resource

    Raises
    ------
    AsyncFailureError
        If any of the responses from the server are unexpected
    AsyncProcessUnsuccessfulError
        If the job being waited for has failed or has been cancelled.
    AsyncTimeoutError
        If the resource did not resolve in time
    """
    start_time = time.time()

    join_endpoint = not async_location.startswith('http')  # Accept full qualified and relative urls

    response = client.get(async_location, allow_redirects=False, join_endpoint=join_endpoint)
    while time.time() < start_time + max_wait:
        if response.status_code == 303:
            return response.headers['Location']
        if response.status_code != 200:
            e_template = 'The server gave an unexpected response. Status Code {}: {}'
            raise errors.AsyncFailureError(e_template.format(
                response.status_code, response.text))
        data = response.json()
        if data['status'].lower()[:5] in ['error', 'abort']:
            e_template = 'The job did not complete successfully. Job Data: {}'
            raise errors.AsyncProcessUnsuccessfulError(e_template.format(data))
        time.sleep(5)
        response = client.get(async_location, allow_redirects=False, join_endpoint=join_endpoint)

    timeout_msg = 'Client timed out in {} seconds waiting for {} to resolve. Last status was {}: {}'
    raise errors.AsyncTimeoutError(timeout_msg.format(max_wait,
                                                      async_location,
                                                      response.status_code,
                                                      response.text))
