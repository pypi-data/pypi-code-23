#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Ironpipe Python library

The Ironpipe library helps you build python appliations that interact
with the the Ironpipe service.

api_key
	Global variable that contains your Ironpipe account API Key

loads(configuration, namespace='default')
    Read configuration from string and load into specified namespace.

load(file, namespace='default')
    Read configuration from file and load into specified namespace.

dumps(namespace='default')
    Read configuration from specified namespace. Returns configuration.

dump(file, namespace='default')
    Read configuration from specified namespace and writes to specified file.

write(producer, file, metadata=None, namespace='default')
	Read data from file and write to specified producer to specified namespace

read(consumer, namespace='default')
	Read next avalable file from specified consumer in specified namespace.
	Returns Message instance or None if the consumer does not have any
	pending files to deliver.

Message(file, metadata=None)
    file: file descriptor pointing to a data file
    metadata: dictionary of name / value pairs

subscribe(stream, on_success=None, on_failure=None, namespace='default')
	Calls 'on_success' function with argument Message when a file is
	processed successfully by specified resource in the specified namespace.
	Calls 'on_failure' function with argument error when the specified resource
	in the specified namespace encounters an error when processing a file.

trigger(stream, namespace='default')
	Manually trigger the specified stream in the specified namespace to poll
	the data source for new files.

"""

import requests
import ironpipe
from ironpipe.error import IronpipeError
from ironpipe.subscribe import Subscribe, Message


_ERR_API_KEY = '''
No API key provided. (HINT: set your API key using "ironpipe.api.api_key = \
<API-KEY>"). You can see your API key from the Ironpipe web interface. \
See https://ironpipe.io/apikeys for details, or email support@ironpipe.io \
if you have any questions.
'''


def _api_request(operation, endpoint, token, data=None):
    """
    Helper function that sends a get or put operation to the ironpipe REST API
    returns the API response
    """
    if not token:
        raise IronpipeError(_ERR_API_KEY)

    if operation not in ('get', 'put', 'post'):
        raise IronpipeError('Ironpipe: Unknown api_request operation: {}'.format(operation))

    endpoint = ironpipe.api_base + endpoint
    headers = {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/yaml'}

    try:
        if operation == 'get':
            response = requests.get(endpoint, data=data, headers=headers)
        elif operation == 'put':
            response = requests.put(endpoint, data=data, headers=headers)
        elif operation == 'post':
            response = requests.post(endpoint, data=data, headers=headers)

        if response.status_code != requests.codes.ok:
            raise IronpipeError('Ironpipe: API request error: {}, response: {}'.format(response.status_code, response.text))

    except requests.exceptions.RequestException as e:
        print('Ironpipe: Unknown API request error: {}'.format(e))
        return None

    # API 'get' operations should always return JSON
    if operation == 'get':
        return response.json()
    else:
        return None


def loads(configuration, namespace='default'):
    '''
    Load configuration into specified namespace
    '''
    endpoint = 'v1/namespaces/' + namespace
    result = _api_request('put', endpoint, ironpipe.api_key, configuration)
    import time
    time.sleep(2)   # Just for alpha - remove
    return result


def load(file, namespace='default'):
    '''
    Read configuration from file and load into specified namespace
    '''
    configuration = file.read()

    return loads(configuration, namespace)


def dumps(namespace='default'):
    '''
    Read configuration from specified namespace.
    '''
    endpoint = 'v1/namespaces/' + namespace
    result = _api_request('get', endpoint, ironpipe.api_key)

    if result:
        result = result.get('data')
        if result:
            result = result.get('icf_code')

    return result


def dump(file, namespace='default'):
    '''
    Read configuration from specified namespace and store in specified file
    '''
    configuration = dumps(namespace)

    file.write(configuration)


def subscribe(stream, on_success=None, on_failure=None, namespace='default'):
    '''
    Subscribe to a stream
    '''
    Subscribe(ironpipe.api_key, stream, on_success=on_success, on_failure=on_failure).run()


def trigger(stream, namespace='default'):
    '''
    Trigger the specified stream in the specified namespace
    '''
    endpoint = 'v1/namespaces/' + namespace + '/stream-runs/' + stream
    return _api_request('post', endpoint, ironpipe.api_key)
