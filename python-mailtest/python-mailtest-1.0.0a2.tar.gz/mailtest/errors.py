import six


class MailTestError(Exception):
    """MailTest exception"""

    def __init__(self, message, **kwargs):
        self.message = six.text_type(message) if message else "Unknown error"
        super(MailTestError, self).__init__(message, **kwargs)

    def __str__(self):
        return self.message
