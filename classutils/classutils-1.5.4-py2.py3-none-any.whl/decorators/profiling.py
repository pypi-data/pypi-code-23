# encoding: utf-8

import functools
import logging_helper
import cProfile
from io import BytesIO
import pstats

logging = logging_helper.setup_logging()


def profile(_func=None,
            profile_id=None,
            sort_by=u'cumulative'):

    """ This decorator handles any decorator args.

    :param _func:       Possibly the function to be decorated _func's type depends on the usage of the decorator.
                        It's a function if it's used as `@decorator` but ``None`` if used as `@decorator()`.
    :param profile_id:  An ID to register this profiled function with, which allows more granular control of
                        enabling/disabling profiling.
    :param sort_by:     Sets the profiler result sort method.
    :return:
    """

    profilers.register(profile_id)

    def arg_wrapper(func):

        """ This is the real decorator and profiles the decorated function. """

        @functools.wraps(func)
        def wrapper(*args,
                    **kwargs):

            """ Simple profiler for the function.

            :param args:        Args for the function.
            :param kwargs:      Kwargs for the function.
            :return:            The result of the function.
            """

            _profiler = profilers.start_if_active(profile_id)

            # Run the function
            result = func(*args,
                          **kwargs)

            profilers.stop_if_active(func=func,
                                     profile_id=profile_id,
                                     profiler=_profiler,
                                     sort_by=sort_by)

            # Return the function result
            return result

        # Return the decorated function
        return wrapper

    # _func's type depends on the usage of the decorator.  It's a function
    # if it's used as `@decorator` but ``None`` if used as `@decorator()`.
    return arg_wrapper if _func is None else arg_wrapper(_func)


class Profiling(object):

    """Supports the profile decorator"""

    def __init__(self,
                 enabled):
        self._enabled = enabled
        self._profiles = {None: True}

    def _active(self,
                profile_id):
        return self._enabled and self._profiles.get(profile_id, False)

    def register(self,
                 profile_id=None,
                 enabled=False):
        """
        When a function is decorated it can be passed a profile ID
        which will be registered here as a profile, by default they
        are disabled with the exception of the `None` profile.
        The `None` profile is used as the profile for any decorated
        functions that do not pass a profile id.
        Note: No matter what the profile state is, if self._enabled
              is False then no profiling will take place.

        :param profile_id:
        :param enabled: boole
        :return:
        """

        if profile_id is not None:
            # Check whether profile has already been registered.
            if profile_id not in self._profiles:
                # Register profile (disabled by default)
                self._profiles[profile_id] = enabled

    def enable(self,
               profile_id=None):
        """
        Enable the profile. If profile is none, global profiling
        is enabled.

        :param profile_id: name of profile
        :return: N/A
        """
        if profile_id is None:
            self._enabled = True
        else:
            self._profiles[profile_id] = True

    def disable(self,
                profile_id=None):
        """
        Disable the profile. If profile is none, global profiling
        is disabled.

        :param profile_id: name of profile
        :return: N/A
        """
        if profile_id is None:
            self._enabled = False
        else:
            self._profiles[profile_id] = False

    def start_if_active(self,
                        profile_id=None):
        """
        Used to start the profiler on condition that the
        global profiling is enabled and the if a profile
        ID is provided, that the profile is enabled.

        :param profile_id: name of profile
        :return: a cProfile.Profile object or None
        """
        profiler = None

        if self._active(profile_id):
            # Enable the profiler
            profiler = cProfile.Profile()
            profiler.enable()

        return profiler

    def stop_if_active(self,
                       func,
                       profile_id,
                       profiler,
                       sort_by):
        """
        Used to stop a running profiler on condition that the
        global profiling is enabled and the if a profile
        ID is provided, that the profile is enabled.

        :param func: the function being profile
        :param profile_id: name of the profiler
        :param profiler: cProfile.Profile instance
        :param sort_by: how to sort profiled results
        :return:
        """
        # Disable the profiler & log the output
        if self._active(profile_id):
            profiler.disable()

            buf = BytesIO()

            ps = pstats.Stats(profiler,
                              stream=buf)
            ps.sort_stats(sort_by)
            ps.print_stats()

            logging.info(u'Profile (Profile ID = {id}) for "{mod}.{name}":\n{stats}'
                         .format(id=profile_id,
                                 mod=func.__module__,
                                 name=func.__name__,
                                 stats=buf.getvalue()))


profilers = Profiling(False)

enable = profilers.enable
disable = profilers.disable
register = profilers.register
