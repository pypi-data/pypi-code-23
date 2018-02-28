import traceback
import logging
import json

logger = logging.getLogger("edw.logger")


class LogErrors(object):
    def __init__(self, func, message, context=None):
        self.func = func
        self.message = message
        self.context = context

    def __call__(self, *args, **kwargs):
        try:
            if self.context:
                # It's an instance method. First argument is 'self'.
                return self.func(self.context, *args, **kwargs)
            else:
                return self.func(*args, **kwargs)
        except:
            tb = traceback.format_exc()
            self.log_error(tb)

    def log_error(self, tb):
        logger.error(json.dumps(self.build_error(tb)))

    def build_error(self, tb):
        return {
            "Type": "LogError",
            "Message": self.message,
            "Traceback": tb,
            "LoggerName": logger.name
        }


def log_errors(message, factory=LogErrors):
    def decorator(func):
        return factory(func, message)
    return decorator
