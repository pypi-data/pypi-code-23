import functools
import logging
import traceback
from chalice import ChaliceViewError, NotFoundError, BadRequestError, ForbiddenError
from amaasinfra.exception.message import MESSAGES
from amaasinfra.authorization.errors import AuthorizationError

class ApiErrorHandler():
    """
    Decorator for Chalice API methods. 
    This wraps an api lambda handler to raise the proper Chalice exceptions.
    """
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger()

    def __call__(self, func, *args, **kwargs):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except KeyError as e:
                self.logger.error(traceback.format_exc())
                raise NotFoundError(e)
            except (ValueError, TypeError, AttributeError) as e:
                self.logger.error(traceback.format_exc())
                raise BadRequestError(e)
            except (AuthorizationError) as e:
                self.logger.error(traceback.format_exc())
                raise ForbiddenError(e)
            except ChaliceViewError as e:
                self.logger.error(traceback.format_exc())
                raise
            except Exception as e:
                self.logger.error(traceback.format_exc())
                # consider suppressing this if the APIs are to go public
                raise BadRequestError(MESSAGES['unhandled_exception'] % str(e))
        return functools.update_wrapper(wrapper, func)