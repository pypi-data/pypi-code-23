from accern import error, util
from accern.schema import Schema
from datetime import datetime
import re
import sys
import textwrap

try:
    import requests
except ImportError:
    requests = None
else:
    try:
        # Require version 0.8.8, but don't want to depend on distutils
        version = requests.__version__
        major, minor, patch = [int(i) for i in version.split('.')]
    except Exception:
        # Probably some new-fangled version, so it should support verify
        pass
    else:
        if (major, minor, patch) < (0, 8, 8):
            sys.stderr.write(
                'Warning: the Accern library requires that your Python '
                '"requests" library be newer than version 0.8.8, but your '
                '"requests" library is version %s. Accern will fall back to '
                'an alternate HTTP library so everything should work. We '
                'recommend upgrading your "requests" library. If you have any '
                'questions, please contact support@accern.com. (HINT: running '
                '"pip install -U requests" should upgrade your requests '
                'library to the latest version.)' % (version,))
            requests = None


__all__ = [
    'AccernClient',
    'Event',
    'new_http_client'
]


QUANT = [
    'event_impact_gt_mu_add_sigma',
    'event_impact_gt_mu_pos_add_sigma_pos',
    'event_impact_gt_mu_pos_add_2sigma_pos',
    'event_impact_gt_1pct_pos',
    'event_impact_lt_mu_sub_sigma',
    'event_impact_lt_mu_neg_sub_sigma_neg',
    'event_impact_lt_mu_neg_sub_2sigma_neg',
    'event_impact_lt_1pct_neg',
    'event_impact_neg',
    'event_impact_pct_change_avg',
    'event_impact_pct_change_stdev',
    'event_impact_pos',
    'event_relevance',
    'event_sentiment',
    'event_source_timeliness_score',
    'entity_exchange',
    'entity_relevance',
    'entity_sentiment',
    'harvested_at',
    'story_group_sentiment_avg',
    'story_group_sentiment_stdev',
    'story_group_count',
    'story_group_traffic_sum',
    'story_sentiment',
    'story_traffic'
]


def new_http_client(*args, **kwargs):
    return RequestsClient(*args, **kwargs)


class AccernClient(object):
    @staticmethod
    def api_encode(params):
        if isinstance(params, object):
            for key, value in util.six.iteritems(params):
                key = util.utf8(key)
                if value is None:
                    continue
                elif isinstance(value, list):
                    yield (key, ",".join(value))
                else:
                    yield (key, util.utf8(value))

    @staticmethod
    def build_api_url(url, query):
        scheme, netloc, path, base_query, fragment = util.urlsplit(url)
        if base_query:
            query = '%s&%s' % (base_query, query)
        return util.urlunsplit((scheme, netloc, path, query, fragment))

    @staticmethod
    def build_api_headers(token, method):
        if method == "POST":
            return {
                'Content-Type': 'application/json',
                'IO-Authorization': token
            }
        elif method == "GET":
            return {
                'Content-Type': 'application/json',
                'IO-Authorization': token
            }

    @staticmethod
    def build_api_params(schema):
        if schema is None:
            filters = {}
        else:
            filters = schema.get('filters', {})
        avail_params = [value for value in filters if value in Schema.get_url_params()]
        params = {key: filters[key] for key in avail_params}
        if 'harvested_at' in filters:
            del params['harvested_at']
            params['from'] = filters['harvested_at'][0]
        return params

    @classmethod
    def check_values(cls, raw_data, f, f_values):
        if f == 'harvested_at':
            for data in raw_data:
                if (datetime.strptime(data[f], '%Y-%m-%dT%H:%M:%S.%fZ') >= datetime.strptime(f_values[0], '%Y-%m-%d %H:%M:%S')) and \
                   (datetime.strptime(data[f], '%Y-%m-%dT%H:%M:%S.%fZ') <= datetime.strptime(f_values[1], '%Y-%m-%d %H:%M:%S')):
                    yield data
        else:
            for data in raw_data:
                for value in f_values:
                    if data[f] >= value[0] and data[f] <= value[1]:
                        yield data

    @staticmethod
    def check_token(token):
        if token:
            my_token = token
        else:
            from accern import token
            my_token = token

        if my_token is None:
            raise error.AuthenticationError('No token provided.')
        return my_token

    @staticmethod
    def handle_error(rbody, rcode, resp):
        try:
            error_data = resp['error']
        except (KeyError, TypeError):
            raise error.APIError(
                "Invalid response object from API: %r (HTTP response code "
                "was %d)" % (rbody, rcode), rbody, rcode, resp)

        if rcode == 400:
            return error.AccernError(error_data, rbody, rcode)

    @staticmethod
    def select_fields(schema, raw_data):
        if schema is None:
            select = []
        else:
            select = schema.get('select', [])
        names = [option['alias'] if 'alias' in option else option['field'] for option in select]
        fields = [option['field'] for option in select]
        data_selected = []

        for data in raw_data:
            if bool(select) > 0:
                try:
                    if isinstance(select, list):
                        new_data = dict(zip(names, [data[field] for field in fields]))
                    else:
                        raise error.AccernError('Select field should be a list.')
                except KeyError:
                    raise error.AccernError('Invalid select values passed.')
            else:
                new_data = data

            if 'entity_competitors' in new_data:
                new_data['entity_competitors'] = ' | '.join(new_data['entity_competitors'])
            if 'entity_indices' in new_data:
                new_data['entity_indices'] = ' | '.join(new_data['entity_indices'])

            data_selected.append(new_data)

        return data_selected

    @classmethod
    def quant_filter(cls, schema, raw_data):
        if schema is None:
            filters = {}
        else:
            filters = schema.get('filters', {})

        for f in filters:
            if f in QUANT:
                data_filtered = list(cls.check_values(raw_data, f, filters[f]))
                raw_data = data_filtered

        return raw_data


class Event(object):
    SSE_LINE_PATTERN = re.compile('(?P<name>[^:]*):?( ?(?P<value>.*))?')

    def __init__(self, data='', event='message', event_id=None, retry=None):
        self.data = data
        self.event = event
        self.event_id = event_id
        self.retry = retry

    def dump(self):
        lines = []
        if self.event_id:
            lines.append('id: %s' % self.event_id)

        # Only include an event line if it's not the default already.
        if self.event != 'message':
            lines.append('event: %s' % self.event)

        if self.retry:
            lines.append('retry: %s' % self.retry)

        lines.extend('data: %s' % d for d in self.data.split('\n'))
        return '\n'.join(lines) + '\n\n'

    @classmethod
    def parse(cls, raw):
        """Given a possibly-multiline string representing an SSE message, parse it and return a Event object."""
        msg = cls()
        for line in raw.splitlines():
            m = cls.SSE_LINE_PATTERN.match(line)
            if m is None:
                # Malformed line.  Discard but warn.
                sys.stderr.write('Invalid SSE line: "%s"' % line, SyntaxWarning)
                continue

            name = m.group('name')
            if name == '':
                # line began with a ":", so is a comment.  Ignore
                continue
            value = m.group('value')

            if name == 'data':
                # If we already have some data, then join to it with a newline.
                # Else this is it.
                if msg.data:
                    msg.data = '%s\n%s' % (msg.data, value)
                else:
                    msg.data = value
            elif name == 'event':
                msg.event = value
            elif name == 'id':
                msg.event_id = value
            elif name == 'retry':
                msg.retry = int(value)

        return msg

    def __str__(self):
        return self.data


class HTTPClient(object):
    def request(self, method, url, headers, post_data=None):
        raise NotImplementedError(
            'HTTPClient subclasses must implement `request`')


class RequestsClient(HTTPClient):
    name = 'requests'

    def __init__(self, timeout=80, session=None, **kwargs):
        super(RequestsClient, self).__init__(**kwargs)
        self._timeout = timeout
        self._session = session or requests.Session()

    def request(self, method, url, headers, post_data=None):
        kwargs = {}
        try:
            try:
                result = self._session.request(method,
                                               url,
                                               headers=headers,
                                               data=post_data,
                                               timeout=self._timeout,
                                               **kwargs)
            except TypeError as e:
                raise TypeError(
                    'Warning: It looks like your "requests" library is out of '
                    'date. You can fix that by running "pip install -U requests".) '
                    'The underlying error was: %s' % (e))
            content = result.content
            status_code = result.status_code
        except Exception as e:
            # Would catch just requests.exceptions.RequestException, but can
            # also raise ValueError, RuntimeError, etc.
            self.handle_request_error(e)
        return content, status_code, result.headers

    @staticmethod
    def handle_request_error(e):
        if isinstance(e, requests.exceptions.RequestException):
            msg = ("Unexpected error communicating with Accern.  "
                   "If this problem persists, let us know at "
                   "support@accern.com.")
            err = "%s: %s" % (type(e).__name__, str(e))
        else:
            msg = ("Unexpected error communicating with Accern. "
                   "It looks like there's probably a configuration "
                   "issue locally.  If this problem persists, let us "
                   "know at support@accern.com.")
            err = "A %s was raised" % (type(e).__name__,)
            if str(e):
                err += " with error message %s" % (str(e),)
            else:
                err += " with no error message"
        msg = textwrap.fill(msg) + "\n\n(Network error: %s)" % (err,)
        raise error.APIConnectionError(msg)
