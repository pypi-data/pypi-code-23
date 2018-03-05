"""Accern Streaming API client.

Core client functionality, common across all API requests (including performing
HTTP requests).
"""
import codecs
import re
import requests
import time
from accern.default_client import AccernClient, Event
from accern.schema import Schema
from accern import util

API_BASE = 'https://feed.accern.com/v4/stream'
END_OF_FIELD = re.compile(r'\r\n\r\n|\r\r|\n\n')


class StreamListener(AccernClient):
    def on_data(self, raw_data):
        """Call when raw data is received from connection.

        Override this method if you want to manually handle stream data. Return
        False to stop stream and close connection.
        """
        if 'disconnect' in raw_data:
            if self.on_disconnect(raw_data['disconnect']) is False:
                return False
        return raw_data

    @staticmethod
    def on_disconnect(notice):
        """Call when server return a disconnect notice."""
        if notice == 'disconnect':
            return False
        return True


class StreamClient(object):
    """Perform requests to the Accern API web services."""

    def __init__(self, listener, token=None, schema=None, **kwargs):
        """Intialize with params.

        :param client: default http client. Optional
        :param token: Accern API token. Required.
        """
        self._listener = listener or StreamListener()
        self.api_base = API_BASE
        # Keep data here as it streams in
        self.buf = u''
        self.chunk_size = kwargs.get('chunk_size', 1024)
        self.last_id = kwargs.get('last_id', None)
        self.schema = schema or {}
        # Any extra kwargs will be fed into the requests.get call later.
        self.requests_kwargs = kwargs.get('request', {})
        self.resp = None
        self.resp_iterator = None
        self.retry = kwargs.get('retry', 3000)
        self.timeout = kwargs.get('timeout', 300.0)
        self.token = token or None
        self.url = None

        # The SSE spec requires making requests with Cache-Control: nocache
        if 'headers' not in self.requests_kwargs:
            self.requests_kwargs['headers'] = {}
        self.requests_kwargs['headers']['Cache-Control'] = 'no-cache'

        # The 'Accept' header is not required, but explicit > implicit
        self.requests_kwargs['headers']['Accept'] = 'text/event-stream'
        self.new_session()

    def __iter__(self):
        return self

    def __next__(self):
        decoder = codecs.getincrementaldecoder(self.resp.encoding)(errors='replace')
        while not self._event_complete():
            try:
                next_chunk = next(self.resp_iterator)
                if not next_chunk:
                    raise EOFError()
                self.buf += decoder.decode(next_chunk)

            except (StopIteration, requests.RequestException, EOFError):
                time.sleep(self.retry / 1000.0)
                self._run()

                # The SSE spec only supports resuming from a whole message, so
                # if we have half a message we should throw it out.
                head, sep, _ = self.buf.rpartition('\n')
                self.buf = head + sep
                continue

        # Split the complete event (up to the END_OF_FIELD) into event_string,
        # and retain anything after the current complete event in self.buf
        # for next time.
        (event_string, self.buf) = re.split(END_OF_FIELD, self.buf, maxsplit=1)
        msg = Event.parse(event_string)

        # If the server requests a specific retry delay, we need to honor it.
        if msg.retry:
            self.retry = msg.retry

        # last_id should only be set if included in the message.  It's not
        # forgotten if a message omits it.
        if msg.event_id:
            self.last_id = msg.event_id

        if msg.data:
            raw_data = util.json.loads(util.json.loads(msg.data)['data'])['signals']

            data = AccernClient.quant_filter(self.schema, raw_data)
            data = AccernClient.select_fields(self.schema, data)

            if self._listener.on_data(data) is False:
                return False

        return msg

    def _event_complete(self):
        return re.search(END_OF_FIELD, self.buf) is not None

    def _run(self):
        if self.last_id:
            self.requests_kwargs['headers']['Last-Event-ID'] = self.last_id
        # Use session if set.  Otherwise fall back to requests module.
        requester = self.session or requests
        self.resp = requester.get(self.url, stream=True)
        self.resp_iterator = self.resp.iter_content(chunk_size=self.chunk_size)

        # todo: Ensure we're handling redirects.  Might also stick the 'origin'
        # attribute on Events like the Javascript spec requires.
        self.resp.raise_for_status()
        while next(self, None) is not None:
            next(self, None)


    def new_session(self):
        self.session = requests.Session()
        self.session.params = None

    def performs(self):
        """Perform HTTP GET/POST with credentials.

        :param output: output config.

        :param params: HTTP GET parameters.

        :raises ApiError: when the API returns an error.
        :raises Timeout: if the request timed out.
        :raises TransportError: when something went wrong while trying to
            exceute a request.
        """
        print ('%s - Start streaming, use [Ctrl+C] to stop...' % (util.datetime.now()))
        schema = Schema.validate_schema(method='stream', schema=self.schema)
        params = AccernClient.build_api_params(schema)
        params['token'] = AccernClient.check_token(self.token)
        encoded_params = util.urlencode(list(AccernClient.api_encode(params or {})))
        self.url = AccernClient.build_api_url(self.api_base, encoded_params)
        try:
            self._run()
        except KeyboardInterrupt:
            print ('%s - Streaming stopped...' % (util.datetime.now()))
        else:
            pass

    if util.six.PY2:
        next = __next__
