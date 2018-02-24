from mailtest.client import Client
from mailtest.errors import MailTestError


class Api(Client):
    """MailTest API"""
    BASE_URL = "https://api.mailtest.in"
    VERSION = "/v1"

    def __init__(self, **kwargs):
        super(Api, self).__init__(self, **kwargs)
        self.version = self.VERSION
        self.base_url = "%s%s" % (self.BASE_URL, self.version)

        self._active = "active"
        self._disposable = "disposable"
        self._robot = "robot"
        self._invalid = "invalid"
        self._unknown = "unknown"
        self._error = "error"
        self.statuses = {
            self._active: "ACTIVE",
            self._disposable: "DISPOSABLE",
            self._robot: "ROBOT",
            self._invalid: "INVALID",
            self._unknown: "UNKNOWN",
            self._error: "ERROR",
        }
        self.codes = {
            self._active: ["01"] ,
            self._disposable: ["11"],
            self._robot: ["12"],
            self._invalid: ["21", "22", "23"],
            self._unknown: ["81", "82"],
            self._error: ["91", "92"],
        }

    def check(self, domain):
        result = self._get(domain)
        if result.get("status") not in self.statuses.values():
            raise MailTestError
        return result
