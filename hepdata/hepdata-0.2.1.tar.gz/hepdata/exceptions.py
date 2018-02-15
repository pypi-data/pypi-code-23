# -*- coding: utf-8 -*-


APP_ERRORS = {
    7: "Invalid URL same as a 404 Not Found",
    8: "IP address not whitelisted",
    9: "No profile matches the provided ID",
    10: "License key error",
}


class HEPError(Exception):
    """Generalizes any server/application errors"""

    def __init__(self, msg=None, code=None, response=None):
        self.code = code
        msg = ''

        if response is not None:
            msg += ", ({})".format(response.request.url)

        if code > 100:
            self.msg = "HTTP {}".format(code)
        else:
            self.msg = "Error {}: {}".format(
                code, APP_ERRORS.get(code, "Unknown"))

        self.msg += msg
        super(HEPError, self).__init__(self.msg)

    def __str__(self):
        return self.msg
