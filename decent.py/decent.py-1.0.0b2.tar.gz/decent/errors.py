class DecentError(Exception):
    @classmethod
    def success_false(cls, url, error):
        message = "{}: {}".format(error["error"]["code"], error["error"]["message"])
        return cls("Request to {} was unsuccessful ({})".format(url, message))
