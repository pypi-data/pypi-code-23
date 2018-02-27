import datetime
import re
import socket
import uuid
# With statement over Socket
from contextlib import contextmanager
from datetime import timedelta
from random import randrange, SystemRandom

__author__ = 'OrW'

ISO_TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"


def datetime_from_iso_string(timestamp):
    format_string = ISO_TIMESTAMP_FORMAT
    if timestamp.endswith("Z"):
        # Not all ISO-8601 strings end with "Z".
        format_string += 'Z'
    return datetime.datetime.strptime(timestamp, format_string)


@contextmanager
def socket_context(*args, **kw):
    s = socket.socket(*args, **kw)
    yield s
    s.close()


class IpUtils(object):
    def __init__(self):
        self._own_ip = None
        self._ip_name_cache = None

    def get_own_ip(self):
        if self._own_ip is None:
            with socket_context(socket.AF_INET, socket.SOCK_DGRAM) as s:
                try:
                    s.connect(("google.com", 80))
                    self._own_ip = s.getsockname()[0]
                except Exception:
                    from config.config import logger
                    logger.warning("Failed to acquire external IP - binding server on 0.0.0.0")
                    self._own_ip = "0.0.0.0"
        return self._own_ip

    def get_ip_name(self, ip):
        if self._ip_name_cache is None:
            from expiringdict import ExpiringDict
            ExpiringDict(max_len=1000, max_age_seconds=200)
        try:
            res = self._ip_name_cache.get(ip, None)
            if res is None:
                # TODO: Remove patch.
                return None
                # res = socket.gethostbyaddr(ip)[0]
                # self._ip_name_cache[ip] = res
            return res or None
        except socket.herror:
            self._ip_name_cache[ip] = 0
            return None
        except socket.gaierror:
            self._ip_name_cache[ip] = 0
            return None

    @staticmethod
    def get_ip_for_dns_name(name):
        return socket.gethostbyname(name)


IP_UTILS = IpUtils()


class DomainUtils(object):
    def __init__(self, db):
        self._db = db

    def get_ip_names(self, ip):
        names = self._db.get_dns_names_for_ip(ip)
        if len(names) == 0:
            return [IP_UTILS.get_ip_name(ip)]
        else:
            return names

    def get_most_relevant_tld(self, ip):
        import tldextract
        names = self.get_ip_names(ip)
        tlds = {}
        # Get and count tld appearances
        for name in names:
            if isinstance(name, (str, unicode)) and len(name) > 0:
                tld = tldextract.extract(name).registered_domain
                tlds[tld] = tlds.get(tld, 0) + 1
        # find the tld that appeared the most
        if len(tlds) > 0:
            most_common_tld = max([(v, k) for k, v in tlds.iteritems()])[1]
        else:
            most_common_tld = None
        # return all the names, and their most relevant tld
        return names, most_common_tld


class RandomUtils(object):
    @staticmethod
    def gen_uid():
        return uuid.uuid4().hex

    @staticmethod
    def gen_token(size=256):
        if size % 2 != 0:
            raise ValueError("Size in bits must be an even number.")
        return uuid.UUID(int=SystemRandom().getrandbits(size/2)).hex + \
               uuid.UUID(int=SystemRandom().getrandbits(size/2)).hex


    @staticmethod
    def random_datetime(start=None, end=None):
        """
        This function will return a random datetime between two datetime
        objects.
        If no range is provided - a last 24-hours range will be used
        :param datetime,None start: start date for range, now if None
        :param datetime,None end: end date for range, next 24-hours if None
        """
        # build range
        now = datetime.datetime.now()
        start = start or now
        end = end or now + timedelta(hours=24)
        delta = end - start
        int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
        # Random time
        random_second = randrange(int_delta)
        # Return random date
        return start + timedelta(seconds=random_second)


gen_uid = RandomUtils.gen_uid
gen_token = RandomUtils.gen_token


class StringUtils(object):
    @staticmethod
    def convert_camelcase_to_underscore(name, lower=True):
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        res = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
        if lower:
            return res.lower()
        else:
            return res.upper()
