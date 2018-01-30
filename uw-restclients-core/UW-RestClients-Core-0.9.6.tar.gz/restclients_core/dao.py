import random
import datetime
from restclients_core.util.mock import load_resource_from_path
from restclients_core.util.local_cache import set_cache_value, get_cache_value
from restclients_core.models import MockHTTP, CacheHTTP
from restclients_core.exceptions import ImproperlyConfigured
from restclients_core.cache import NoCache
from restclients_core.util.performance import PerformanceDegradation
from importlib import import_module
from commonconf import settings
from urllib3 import connection_from_url
from urllib3.util.retry import Retry
from logging import getLogger
import dateutil.parser
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse
import time
import ssl

logger = getLogger(__name__)


class DAO(object):
    """
    Base class for per-service interfaces.
    """
    def __init__(self):
        self.implementation = None

        # format is ISO 8601
        log_start_str = self.get_service_setting("TIMING_START", None)
        log_end_str = self.get_service_setting("TIMING_END", None)

        if log_start_str is not None and log_end_str is not None:
            self.log_start = dateutil.parser.parse(log_start_str)
            self.log_end = dateutil.parser.parse(log_end_str)
        else:
            self.log_start = None
            self.log_end = None

        self.log_timing = self.get_service_setting("TIMING_LOG_ENABLED", False)
        self.logging_rate = float(self.get_service_setting("TIMING_LOG_RATE",
                                                           1.0))

    def service_name(self):
        """
        This method must be overridden to define your service's short name.

        This name is used in multiple places.  The Mock DAO uses it in path
        names for file, and the Django app for browsing services uses it as
        part of the URL.
        """
        raise Exception("service_name must be defined per DAO")

    def _custom_headers(self, method, url, headers, body):
        """
        This method can be overridden to add headers to a request.  For
        example, a Bearer header can be added if a service uses OAuth tokens.
        """
        # to handle things like adding a bearer token
        pass

    def _custom_response_edit(self, method, url, headers, body, response):
        """
        This method allows a service to edit a response.

        If you want to do this, you probably really want to use
        _edit_mock_response - this method will operate on Live resources.
        """
        if self.get_implementation().is_mock():
            delay = self.get_setting("MOCKDATA_DELAY", 0.0)
            time.sleep(delay)
            self._edit_mock_response(method, url, headers, body, response)

    def _edit_mock_response(self, method, url, headers, body, response):
        """
        Override this method to edit responses in mock resources.  This can be
        used to ensure datetime fields have useful values relative to now,
        or to provide more dynamic behavior for PUT/POST/DELETE requests.

        This method should edit the response object directly.  No return value.
        """
        pass

    def get_default_service_setting(self, key):
        """
        A hook for setting useful defaults.  For example, if you have a host
        your service almost always uses, you can have this method return that
        value when passed 'HOST'.
        """
        return None

    def getURL(self, url, headers={}):
        """
        Request a URL using the HTTP method GET
        """
        return self._load_resource("GET", url, headers, None)

    def postURL(self, url, headers={}, body=None):
        """
        Request a URL using the HTTP method POST.
        """
        return self._load_resource("POST", url, headers, body)

    def putURL(self, url, headers, body=None):
        """
        Request a URL using the HTTP method PUT.
        """
        return self._load_resource("PUT", url, headers, body)

    def patchURL(self, url, headers, body):
        """
        Request a URL using the HTTP method PATCH.
        """
        return self._load_resource("PATCH", url, headers, body)

    def deleteURL(self, url, headers=None):
        """
        Request a URL using the HTTP method DELETE.
        """
        return self._load_resource("DELETE", url, headers, None)

    def service_mock_paths(self):
        """
        If your web service client ships with mock resources, override this
        method to return a list of top level paths where they can be found.

        e.g. If your resource is in
        /users/my/my_client/resources/client/file/hello.json
        you should generate ["/users/my/my_client/resources"]
        """
        return []

    def _load_resource(self, method, url, headers, body):
        start_time = time.time()
        service = self.service_name()

        bad_response = PerformanceDegradation.get_response(service, url)
        if bad_response:
            return bad_response

        custom_headers = self._custom_headers(method, url, headers, body)
        if custom_headers:
            headers.update(custom_headers)

        is_cacheable = self._is_cacheable(method, url, headers, body)

        cache = self.get_cache()

        if is_cacheable:
            cache_response = cache.getCache(service, url, headers)
            if cache_response:
                if "response" in cache_response:
                    self._log(service=service, url=url, method=method,
                              response=cache_response["response"],
                              cached=True, start_time=start_time)
                    return cache_response["response"]
                if "headers" in cache_response:
                    headers = cache_response["headers"]

        backend = self.get_implementation()

        response = backend.load(method, url, headers, body)
        self._custom_response_edit(method, url, headers, body, response)

        if is_cacheable:
            cache_post_response = cache.processResponse(service, url, response)
            if cache_post_response is not None:
                if "response" in cache_post_response:
                    self._log(service=service, url=url, method=method,
                              response=response, cached=True,
                              start_time=start_time)
                    return cache_post_response["response"]

        self._log(service=service, url=url, method=method, response=response,
                  cached=False, start_time=start_time)

        return response

    def get_cache(self):
        implementation = self.get_setting("DAO_CACHE_CLASS", None)
        return self._getModule(implementation, NoCache)

    def get_implementation(self):
        implementation = self.get_service_setting("DAO_CLASS", None)

        # Handle the easy built-ins
        if "Live" == implementation:
            return self._get_live_implementation()

        if "Mock" == implementation:
            return self._get_mock_implementation()

        # Legacy settings support
        live = "restclients.dao_implementation.%s.Live" % (self.service_name())
        mock = "restclients.dao_implementation.%s.File" % (self.service_name())

        if live == implementation:
            return self._get_live_implementation()

        if mock == implementation:
            return self._get_mock_implementation()

        if implementation:
            return self._getModule(implementation, None,
                                   [self.service_name(), self])

        return self._get_mock_implementation()

    def _is_cacheable(self, method, url, headers, body=None):
        if method == "GET":
            return True
        return False

    def _ok_status_codes():
        return [200, 201, 202, 204]

    def _error_status_codes():
        return []

    def _get_live_implementation(self):
        return LiveDAO(self.service_name(), self)

    def _get_mock_implementation(self):
        return MockDAO(self.service_name(), self)

    def get_service_setting(self, key, default=None):
        if default is None:
            default = self.get_default_service_setting(key)

        service_key = "%s_%s" % (self.service_name().upper(), key)

        if hasattr(settings, "RESTCLIENTS_%s" % service_key):
            return self.get_setting(service_key, default)
        else:
            return self.get_setting(key, default)

    def get_setting(self, key, default=None):
        key = "RESTCLIENTS_%s" % key
        return getattr(settings, key, default)

    def _getModule(self, value, default_class, args=[]):
        if not value:
            return default_class()

        module, attr = value.rsplit('.', 1)
        try:
            mod = import_module(module)
        except ImportError as e:
            raise ImproperlyConfigured('Error importing module %s: "%s"' %
                                       (module, e))
        try:
            config_module = getattr(mod, attr)
        except AttributeError:
            raise ImproperlyConfigured('Module "%s" does not define a '
                                       '"%s" class' % (module, attr))
        return config_module(*args)

    def _log(self, *args, **kwargs):
        if not self.should_log():
            return

        from_cache = 'yes' if kwargs.get('cached') else 'no'
        response = kwargs.get('response')
        cache_class = (response.cache_class if hasattr(response, 'cache_class')
                       else "None")
        total_time = time.time() - kwargs.get('start_time')
        msg = (('service:%s method:%s url:%s status:%s from_cache:%s ' +
               'cache_class:%s time:%s')
               % (kwargs.get('service'), kwargs.get('method'),
                  kwargs.get('url'), response.status,
                  from_cache, cache_class, total_time))
        logger.info(msg)

    def should_log(self):

        if self.log_start is not None and self.log_end is not None:
            if not self.log_start < datetime.datetime.now() < self.log_end:
                return False

        if not self.log_timing:
            return False

        if random.random() >= self.logging_rate:
            return False

        return True


class DAOImplementation(object):
    def __init__(self, service_name, dao):
        self._service_name = service_name
        self.dao = dao

    def is_live(self):
        return False

    def is_mock(self):
        return False


class LiveDAO(DAOImplementation):
    """
    Loads response objects by fetching resources from an HTTP(s) server.
    """
    pools = {}

    def is_live(self):
        return True

    def load(self, method, url, headers, body):
        pool = self.get_pool()
        timeout = pool.timeout.read_timeout

        response = pool.urlopen(method, url, body=body, headers=headers,
                                timeout=timeout)

        return response

    def get_pool(self):
        service = self.dao.service_name()
        if service not in LiveDAO.pools:
            pool = self.create_pool()
            LiveDAO.pools[service] = pool

        return LiveDAO.pools[service]

    def create_pool(self):
        """
        Return a ConnectionPool instance of given host
        :param socket_timeout:
            socket timeout for each connection in seconds
        """

        service = self.dao.service_name()

        host = self.dao.get_service_setting("HOST")
        socket_timeout = self.dao.get_service_setting("TIMEOUT", 2)
        max_pool_size = self.dao.get_service_setting("POOL_SIZE", 10)
        key_file = self.dao.get_service_setting("KEY_FILE", None)
        cert_file = self.dao.get_service_setting("CERT_FILE", None)
        ca_certs = self.dao.get_setting("CA_BUNDLE",
                                        "/etc/ssl/certs/ca-bundle.crt")
        verify_https = self.dao.get_service_setting("VERIFY_HTTPS")

        if verify_https is None:
            verify_https = True

        kwargs = {
            "retries": Retry(total=1, connect=0, read=0, redirect=1),
            "timeout": socket_timeout,
            "maxsize": max_pool_size,
            "block": True,
        }

        if key_file is not None and cert_file is not None:
            kwargs["key_file"] = key_file
            kwargs["cert_file"] = cert_file

        if urlparse(host).scheme == "https":
            kwargs["ssl_version"] = self.dao.get_service_setting(
                "SSL_VERSION", ssl.PROTOCOL_TLSv1)
            if verify_https:
                kwargs["cert_reqs"] = "CERT_REQUIRED"
                kwargs["ca_certs"] = ca_certs

        return connection_from_url(host, **kwargs)


class MockDAO(DAOImplementation):
    """
    Loads response objects based on file content.
    """
    paths = []

    def is_mock(self):
        return True

    @classmethod
    def register_mock_path(cls, path):
        if path not in MockDAO.paths:
            MockDAO.paths.append(path)

    def get_registered_paths(self):
        return MockDAO.paths

    def _get_mock_paths(self):
        return self.get_registered_paths() + self.dao.service_mock_paths()

    def load(self, method, url, headers, body):
        service = self._service_name

        cache_key = "%s-%s" % (service, url)
        value = get_cache_value(cache_key)
        if value:
            return value

        for path in self._get_mock_paths():
            response = load_resource_from_path(path, service, "file", url,
                                               headers)

            if response:
                set_cache_value(cache_key, response)
                return response

        response = MockHTTP()
        response.status = 404
        response.reason = "Not Found"

        set_cache_value(cache_key, response)
        return response
