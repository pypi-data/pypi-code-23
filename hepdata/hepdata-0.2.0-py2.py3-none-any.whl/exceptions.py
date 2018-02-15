# -*- coding: utf-8 -*-


APP_ERRORS = {
    8: "IP address not whitelisted",
    9: "No profile matches the provided ID",
    10: "License key error",
}


class HEPError(Exception):
    """Generalizes any server/application errors"""
    def __init__(self, msg=None, code=None, response=None):
        super(HEPError, self).__init__(msg)
        self.code = code
        if code > 200:
            self.msg = "HTTP {}".format(code)
            if response is not None:
                self.msg += " ({})".format(response.request.url)
        else:
            self.msg = "Error {}: {}".format(code, APP_ERRORS.get(code, "Unknown"))

    def __str__(self):
        return self.msg
