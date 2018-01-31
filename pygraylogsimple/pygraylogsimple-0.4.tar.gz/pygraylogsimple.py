import pycurl
from io import BytesIO
import json
import datetime
from multiprocessing.dummy import Pool as ThreadPool

class PyGraylogSimple:

    def __init__(self, user, password, host, limit_per_request, logger=None):
        self.user = user
        self.password = password
        self.host = host
        self.limit_per_request = limit_per_request
        self.logger = logger

    def _build_search_universal_absolute_url(self, query, date_time_from, date_time_to):
        return '{0}/search/universal/absolute?query={1}&from={2}&to={3}&limit={4}'. \
            format(self.host, query, date_time_from, date_time_to, self.limit_per_request)

    def search_universal_absolute(self, query, date_time_from, date_time_to):
        url = self._build_search_universal_absolute_url(query, date_time_from, date_time_to)

        all_requests = []
        offset = 0
        total_messages = self._get_total_results(url)

        while offset < total_messages:
            full_url = url + '&offset=' + str(offset)
            all_requests.append(_GraylogCallRequest(offset, full_url))
            offset += self.limit_per_request

        pool = ThreadPool(10)
        results = pool.map(self._run, all_requests)
        return [item for sublist in results for item in sublist]     # flaten results

    def _get_total_results(self, url):
        result = self._get_response(url)
        json_data = json.loads(result)
        total_results = json_data['total_results']

        if self.logger is not None:
            self.logger('Total results to download: ' + str(total_results))

        return total_results

    def _run(self, request):
        result = self._get_response(request.url)

        if self.logger is not None:
            self.logger('{0} - downloaded package with offset: {1}'.format(
                datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y"), request.offset))

        json_data = json.loads(result)
        return json_data['messages']

    def _get_response(self, url):
        response = BytesIO()
        curl = _CurlInvoker()
        curl.call(url, self.user, self.password, response)
        result = response.getvalue()
        response.close()
        return result


class _CurlInvoker:

    @staticmethod
    def call(url, user, password, response_to_fill):
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(c.WRITEFUNCTION, response_to_fill.write)
        c.setopt(c.HTTPHEADER, ['Content-Type: application/json', 'Accept-Charset: UTF-8'])
        c.setopt(c.USERPWD, user + ':' + password)
        c.perform()
        c.close()


class _GraylogCallRequest:
    def __init__(self, offset, url):
        self.offset = offset
        self.url = url
