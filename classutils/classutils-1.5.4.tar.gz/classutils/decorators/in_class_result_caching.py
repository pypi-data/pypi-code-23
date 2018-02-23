# -*- coding: utf-8 -*-

import functools
import logging_helper

logging = logging_helper.setup_logging()

CLASS_CACHED_RESULT_PREFIX = u"_cached_"


def clear_class_cached_results(func):

    @functools.wraps(func)
    def wrapper(self,
                *args,
                **kwargs):

        """ Clears all class cached results.
        """
        [delattr(self, attr)
         for attr in dir(self)
         if attr.startswith(CLASS_CACHED_RESULT_PREFIX)]

        return func(self,
                    *args,
                    **kwargs)

    return wrapper


def class_cache_result(func):

    """ This decorator will cache the return value of the decorated function for the lifetime of the object.

    NOTE: This should only be used for class functions!
    """

    cache_id = u'{prefix}{name}'.format(prefix=CLASS_CACHED_RESULT_PREFIX,
                                        name=func.__name__)

    @functools.wraps(func)
    def wrapper(self,
                refresh=False,
                *args,
                **kwargs):

        """ Simple run time cache for the function result.

        :param self:        As this is for class methods we have to add self.
        :param refresh:     setting to True will force this cached result to refresh itself.
        :param args:        Args for the function.
        :param kwargs:      Kwargs for the function.
        :return:            The result of the function.
        """

        try:
            cached_result = getattr(self, cache_id)
            action = u'Refreshing'

        except AttributeError:
            # Value has not been cached yet
            action = u'Caching'

        else:
            if not refresh:
                logging.debug(u'Returning cached result for {id}'.format(id=cache_id))
                return cached_result

        logging.debug(u'{action} result for {id}'.format(action=action,
                                                         id=cache_id))

        result = func(self,
                      *args,
                      **kwargs)

        setattr(self, cache_id, result)

        return result

    return wrapper
