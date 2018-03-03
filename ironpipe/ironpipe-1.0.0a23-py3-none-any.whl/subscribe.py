#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ironpipe import error
from ironpipe.error import *
from ironpipe.run import *

import os
import sys
import json
import shutil
import tempfile
import time
from urllib.request import Request, urlopen, urlretrieve

#
#
class Message:

    #
    #
    def __init__(self, file, metadata=None):
        self.file = file
        self.metadata = metadata

#
#
class Subscribe:

    #
    #
    def __init__(self, api_key, stream, on_success=None, on_failure=None):
        self.api_key = api_key
        self.stream = stream
        self.on_success = on_success
        self.on_failure = on_failure
        self.backend_host = BACKEND_HOST if 'BACKEND_HOST' in globals() else 'https://api.ironpipe.io'
        self.stream_run_endpoint = '%s/v1/namespaces/default/stream-runs/%s' % (self.backend_host, self.stream)

        try:
            self.run_set = self._get_runs()
        except IronpipeError:
            raise
        except Exception as e:
            raise IronpipeError('An error occurred validating your stream') from e

    #
    #
    def run(self):
        print('Subscribing to Ironpipe stream', self.stream)
        while True:
            latest_run_set = self._get_runs()
            new_runs = latest_run_set - self.run_set
            for run in new_runs:
                self._process_run(run)
            time.sleep(3)


    #
    #
    def _process_run(self, run):
        message = Message(None, run)

        if run['status'] == 'succeeded':
            if 'output_file' in run and run['output_file'] is not None:
                run_file = run['output_file']
            else:
                run_file = run['input_file']

            download_path = os.path.join(tempfile.gettempdir(), run_file['file_name'])
            if os.path.isfile(download_path):
                os.remove(download_path)

            file_download_endpoint = '%s/v1/files/%s/download' % (self.backend_host, run_file['id'])
            req = Request(file_download_endpoint)
            req.add_header('Authorization', 'Bearer %s' % (self.api_key))
            with urlopen(req) as response, open(download_path, 'wb') as out_file:
                shutil.copyfileobj(response, out_file)

            if self.on_success:
                with open(download_path, 'r') as f:
                    message.file = f
                    self.on_success(message)
            self.run_set.add(run)
        elif run['status'] == 'failed' and self.on_failure:
            self.on_failure(run)


    #
    #
    def _get_runs(self):
        run_set = set()
        req = Request(self.stream_run_endpoint)
        req.add_header('Authorization', 'Bearer %s' % (self.api_key))
        response = json.loads(urlopen(req).read())
        if 'status' in response:
            if response['status'] == 'ok' and 'data' in response:
                stream_runs = response['data']
                for run in stream_runs:
                    run_set.add(IronpipeRun(run))
            else:
                raise IronpipeError(response.error if hasattr(response, 'error') else 'Unknown Error')
        else:
            raise IronpipeError('Unexpected response')

        return run_set
